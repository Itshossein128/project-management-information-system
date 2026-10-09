"""Weekly / monthly project period report API (FR-PRG)."""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from common.jalali import parse_jalali_or_gregorian
from projects.models import Project
from schedule.measurement_views import ProgressDomainView
from schedule.models import PeriodReportFigure, PeriodReportKind, ProjectPeriodReport
from schedule.services import period_report_service as svc
from schedule.services.measurement_service import ProgressValidationError


def serialize_figure(figure: PeriodReportFigure) -> dict:
    return {
        'id': str(figure.id),
        'section': figure.section,
        'label_key': figure.label_key,
        'value': figure.value,
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
        'generated_at': report.generated_at.isoformat(),
        'generated_by': str(report.generated_by_id) if report.generated_by_id else None,
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
            qs = qs.filter(status='generated')
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


class ProgressReportFigureOverrideView(ProgressDomainView):
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
        )
        figure.refresh_from_db()
        return Response(
            {'override': serialize_override(override), 'figure': serialize_figure(figure)},
            status=status.HTTP_201_CREATED,
        )
