"""Weekly / monthly project period report API (FR-PRG)."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from common.jalali import gregorian_to_jalali, parse_jalali_or_gregorian
from permissions.project import member_has_codename
from projects.models import Project
from schedule.measurement_views import ProgressDomainView
from schedule.models import (
    PeriodReportFigure,
    PeriodReportFigureSourceItem,
    PeriodReportKind,
    ProjectPeriodReport,
)
from schedule.services import period_report_service as svc
from schedule.services.measurement_service import ProgressValidationError


def serialize_figure(figure: PeriodReportFigure) -> dict:
    return {
        'id': str(figure.id),
        'section': figure.section,
        'label_key': figure.label_key,
        'value': figure.value,
        'calculated_value': figure.calculated_value,
        'is_overridden': bool(figure.is_overridden),
        'version': figure.version,
        'unit_of_measure': figure.unit_of_measure or '',
        'value_status': figure.value_status,
        'source_type': figure.source_type,
        'source_id': str(figure.source_id) if figure.source_id else None,
        'source_path': figure.source_path,
        'source_approved': figure.source_approved,
        'last_updated_at': figure.last_updated_at.isoformat() if figure.last_updated_at else None,
        'override_count': figure.overrides.count(),
    }


def serialize_report(report: ProjectPeriodReport, *, with_figures: bool = True) -> dict:
    data = {
        'id': str(report.id),
        'project_id': str(report.project_id),
        'kind': report.kind,
        'title': report.title,
        'period_start': report.period_start.isoformat(),
        'period_end': report.period_end.isoformat(),
        'status': report.status,
        'serial_number': report.serial_number or '',
        'warnings': report.warnings or [],
        'generated_at': report.generated_at.isoformat(),
        'generated_by': str(report.generated_by_id) if report.generated_by_id else None,
        'approved_at': report.approved_at.isoformat() if report.approved_at else None,
        'approved_by': str(report.approved_by_id) if report.approved_by_id else None,
        'superseded_by': str(report.superseded_by_id) if report.superseded_by_id else None,
    }
    if with_figures:
        data['figures'] = [serialize_figure(f) for f in report.figures.prefetch_related('overrides')]
    return data


def serialize_override(override) -> dict:
    return {
        'id': str(override.id),
        'figure_id': str(override.figure_id),
        'old_value': override.old_value,
        'new_value': override.new_value,
        'reason': override.reason,
        'created_by': str(override.created_by_id),
        'created_at': override.created_at.isoformat(),
    }


def serialize_source_item(item: PeriodReportFigureSourceItem) -> dict:
    source_date_jalali = ''
    if item.source_date:
        try:
            source_date_jalali = gregorian_to_jalali(item.source_date)
        except Exception:
            source_date_jalali = ''
    return {
        'id': str(item.id),
        'figure_id': str(item.figure_id),
        'source_type': item.source_type,
        'source_id': str(item.source_id) if item.source_id else None,
        'daily_report_id': str(item.daily_report_id) if item.daily_report_id else None,
        'source_date': item.source_date.isoformat() if item.source_date else None,
        'source_date_jalali': source_date_jalali,
        'source_code': item.source_code,
        'contributed_quantity': item.contributed_quantity,
        'created_by': str(item.created_by_id) if item.created_by_id else None,
        'created_by_name': (
            (item.created_by.get_full_name() or item.created_by.username)
            if item.created_by
            else ''
        ),
        'approved_by': str(item.approved_by_id) if item.approved_by_id else None,
        'approved_by_name': (
            (item.approved_by.get_full_name() or item.approved_by.username)
            if item.approved_by
            else ''
        ),
    }


class ProgressReportListCreateView(ProgressDomainView):
    """List/generate reports. Generation needs only ``view_dashboard`` (membership)."""

    @property
    def required_permission(self):
        return self.read_permission

    @extend_schema(summary='List weekly/monthly period reports', tags=['Progress Reports'])
    def get(self, request, project_pk):
        qs = ProjectPeriodReport.objects.filter(project_id=project_pk)
        kind = request.query_params.get('kind')
        if kind:
            qs = qs.filter(kind=kind)
        if request.query_params.get('include_superseded', '').lower() not in ('1', 'true', 'yes'):
            qs = qs.filter(status__in=['generated', 'approved'])
        return Response([serialize_report(r, with_figures=False) for r in qs])

    @extend_schema(summary='Generate weekly/monthly period report', tags=['Progress Reports'])
    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        kind = request.data.get('kind')
        start_raw = request.data.get('period_start')
        end_raw = request.data.get('period_end')
        if kind not in PeriodReportKind.values or not start_raw or not end_raw:
            raise ProgressValidationError(
                'kind، period_start و period_end الزامی هستند.', 'invalid_period',
            )
        report = svc.generate_period_report(
            project,
            kind,
            parse_jalali_or_gregorian(start_raw),
            parse_jalali_or_gregorian(end_raw),
            request.user,
        )
        return Response(serialize_report(report), status=status.HTTP_201_CREATED)


class ProgressReportDetailView(ProgressDomainView):
    @property
    def required_permission(self):
        return self.read_permission

    @extend_schema(summary='Period report detail with figures', tags=['Progress Reports'])
    def get(self, request, project_pk, report_id):
        report = get_object_or_404(ProjectPeriodReport, pk=report_id, project_id=project_pk)
        return Response(serialize_report(report))


class ProgressReportApproveView(ProgressDomainView):
    approve_permission = 'approve_reports'

    @property
    def required_permission(self):
        return self.approve_permission

    @extend_schema(summary='Approve period report and generate official serial number', tags=['Progress Reports'])
    def post(self, request, project_pk, report_id):
        project = get_object_or_404(Project, pk=project_pk)
        report = get_object_or_404(ProjectPeriodReport, pk=report_id, project=project)
        approved_report = svc.approve_period_report(report, request.user)
        return Response(serialize_report(approved_report))


class ProgressReportFigureView(ProgressDomainView):
    """Figures are read-only; PATCH/PUT are rejected with ``figure_immutable``."""

    @extend_schema(summary='Figure detail', tags=['Progress Reports'])
    def get(self, request, project_pk, figure_id):
        figure = get_object_or_404(PeriodReportFigure, pk=figure_id, report__project_id=project_pk)
        return Response(serialize_figure(figure))

    @extend_schema(summary='Direct figure mutation is forbidden', tags=['Progress Reports'])
    def patch(self, request, project_pk, figure_id):
        get_object_or_404(PeriodReportFigure, pk=figure_id, report__project_id=project_pk)
        svc.reject_direct_figure_mutation()

    put = patch


class ProgressReportFigureSourcesView(ProgressDomainView):
    @extend_schema(summary='Figure provenance breakdown source items', tags=['Progress Reports'])
    def get(self, request, project_pk, figure_id):
        figure = get_object_or_404(PeriodReportFigure, pk=figure_id, report__project_id=project_pk)
        items = figure.source_items.select_related('created_by', 'approved_by').order_by('source_date', 'created_at')
        return Response([serialize_source_item(item) for item in items])


class ProgressReportFigureOverrideView(ProgressDomainView):
    write_permission = 'edit_reports'

    @property
    def required_permission(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            if member_has_codename(self.request.user, str(self.kwargs['project_pk']), 'approve_reports'):
                return 'approve_reports'
            return 'edit_reports'
        return self.read_permission

    @extend_schema(summary='Override a report figure with audit trail', tags=['Progress Reports'])
    def post(self, request, project_pk, figure_id):
        figure = get_object_or_404(PeriodReportFigure, pk=figure_id, report__project_id=project_pk)
        if 'new_value' not in request.data:
            raise ProgressValidationError('new_value الزامی است.', 'override_value_required')
        override = svc.apply_figure_override(
            figure,
            request.data.get('new_value'),
            request.data.get('reason', ''),
            request.user,
            expected_version=request.data.get('expected_version'),
        )
        figure.refresh_from_db()
        return Response(
            {'override': serialize_override(override), 'figure': serialize_figure(figure)},
            status=status.HTTP_201_CREATED,
        )
