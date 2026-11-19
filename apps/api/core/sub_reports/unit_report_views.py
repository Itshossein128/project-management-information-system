"""Canonical unit daily report API views (feature 032, US1).

Base: /api/v1/projects/{project_id}/units/{unit}/daily-reports/
`unit` is one of the six canonical values taken from the URL and is never an
editable report field.
"""
from __future__ import annotations

from decimal import Decimal
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import Http404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.reporting_units import SpecialtyUnit, is_canonical_unit
from permissions.project import HasProjectPermission, IsProjectMember
from sub_reports.models import (
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportHseIncident,
    DisciplineSubReportIssue,
    DisciplineSubReportLabor,
    DisciplineSubReportMachinery,
    DisciplineSubReportMaterial,
    DisciplineSubReportVisit,
    SubReportStatus,
    UnitReportAttachment,
    UnitReportStatusEvent,
)
from projects.models import Project
from sub_reports import unit_report_services as svc
from sub_reports.services.offline_sync import dispatch_operations
from sub_reports.serializers import (
    UnitReportActivitySectionSerializer,
    UnitReportConcreteSectionSerializer,
    UnitReportLaborSectionSerializer,
    UnitReportMachinerySectionSerializer,
    UnitReportMaterialSectionSerializer,
)
from sub_reports.services.attachments import attach_image_to_activity
from sub_reports.services.section_validation import (
    SectionContractError,
    resolve_stoppage_vocabulary,
    update_activity_row,
    update_labor_row,
    update_machinery_row,
    update_material_row,
    validate_concrete_rows,
    validate_narrative_rows,
    validate_activity_rows,
    validate_labor_rows,
    validate_machinery_rows,
    validate_material_rows,
)
from sub_reports.unit_report_serializers import (
    UnitReportCurrentQuerySerializer,
    UnitReportDetailSerializer,
    UnitReportHistorySerializer,
    UnitReportOpenSerializer,
    UnitReportRejectSerializer,
)


class UnitReportViewSet(viewsets.GenericViewSet):
    """Read/open/mutate the current unit report for project/date/unit."""

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('retrieve', 'history', 'current', 'excel'):
            return 'view_reports'
        if self.action in ('approve', 'reject'):
            return 'approve_reports'
        return 'edit_reports'

    # -- helpers ---------------------------------------------------------

    def _unit(self):
        unit = self.kwargs.get('unit')
        if not is_canonical_unit(unit):
            raise svc.UnitReportError(_('invalid_specialty_unit'), 'invalid_specialty_unit')
        return unit

    def _project_id(self):
        return self.kwargs['project_pk']

    def _report_or_404(self):
        return svc.get_scoped_report(
            project_id=self._project_id(), unit=self._unit(), report_id=self.kwargs['pk'],
        )

    def _detail(self, report):
        return Response(UnitReportDetailSerializer(report, context={'request': self.request}).data)

    # -- endpoints -------------------------------------------------------

    @extend_schema(methods=['GET'], responses=UnitReportDetailSerializer)
    @action(detail=False, methods=['get'])
    def current(self, request, *args, **kwargs):
        query = UnitReportCurrentQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        report = (
            svc.current_report_queryset(self._project_id(), self._unit(), query.validated_data['date'])
            .first()
        )
        if report is None:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')
        return self._detail(report)

    @extend_schema(methods=['POST'], request=UnitReportOpenSerializer, responses={
        201: UnitReportDetailSerializer, 200: UnitReportDetailSerializer,
    })
    @action(detail=False, methods=['post'])
    def open(self, request, *args, **kwargs):
        payload = UnitReportOpenSerializer(data=request.data, context={'unit': self._unit()})
        payload.is_valid(raise_exception=True)
        report, created = svc.open_unit_report(
            project=self._project(),
            unit=self._unit(),
            report_date=payload.validated_data['report_date'],
            user=request.user,
            sub_discipline=payload.validated_data.get('sub_discipline', ''),
        )
        data = UnitReportDetailSerializer(report, context={'request': request}).data
        return Response(data, status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def _project(self):
        from projects.models import Project

        try:
            return Project.objects.get(id=self._project_id())
        except Project.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def retrieve(self, request, *args, **kwargs):
        return self._detail(self._report_or_404())

    def partial_update(self, request, *args, **kwargs):
        from sub_reports.serializers import (
            SubReportActivitySerializer,
            SubReportConcreteSerializer,
            SubReportGeneralActivitySerializer,
            SubReportLaborSerializer,
            SubReportMaterialSerializer,
            SubReportNoteSerializer,
        )

        nested_serializers = {
            'activities': SubReportActivitySerializer,
            'labor_entries': SubReportLaborSerializer,
            'material_entries': SubReportMaterialSerializer,
            'concrete_entries': SubReportConcreteSerializer,
            'general_activities': SubReportGeneralActivitySerializer,
            'notes': SubReportNoteSerializer,
        }
        nested_data = {}
        for key, ser_cls in nested_serializers.items():
            if key in request.data:
                ser = ser_cls(data=request.data[key], many=True)
                ser.is_valid(raise_exception=True)
                nested_data[key] = ser.validated_data

        from sub_reports.unit_report_serializers import validate_sub_discipline_for_unit
        if 'sub_discipline' in request.data:
            validate_sub_discipline_for_unit(request.data['sub_discipline'], self._unit())

        report = svc.update_unit_report(
            self._report_or_404(),
            user=request.user,
            unit=self._unit(),
            enforce_permission=True,
            validated_fields={
                field: request.data[field]
                for field in ('form_code', 'revision_number', 'weather_condition', 'site_status', 'sub_discipline')
                if field in request.data
            },
            nested_data=nested_data,
        )
        return self._detail(report)

    def destroy(self, request, *args, **kwargs):
        svc.soft_delete_unit_report(self._report_or_404(), user=request.user, unit=self._unit(), enforce_permission=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Export sub-report as Shiraz Excel spreadsheet (FILE 5 / FILE 6)', tags=['Unit Daily Reports'])
    @action(detail=True, methods=['get'])
    def excel(self, request, *args, **kwargs):
        from django.http import HttpResponse
        from sub_reports.shiraz_subreport_excel import ShirazSubReportExcelBuilder

        report = self._report_or_404()
        builder = ShirazSubReportExcelBuilder(report)
        excel_bytes, filename = builder.build()

        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @extend_schema(methods=['GET'], responses=UnitReportHistorySerializer)
    @action(detail=True, methods=['get'])
    def history(self, request, *args, **kwargs):
        report = self._report_or_404()
        versions = list(
            type(report).all_objects.filter(lineage_id=report.lineage_id).order_by('version_number'),
        )
        superseded_by_map = {
            v.supersedes_id: v.id for v in versions if v.supersedes_id
        }
        for v in versions:
            v.superseded_by = superseded_by_map.get(v.id)

        events = list(
            UnitReportStatusEvent.objects.filter(report_version__lineage_id=report.lineage_id)
            .select_related('actor')
            .order_by('occurred_at', 'id'),
        )
        serializer = UnitReportHistorySerializer({
            'lineage_id': report.lineage_id,
            'current_version_id': next(
                (v.id for v in versions if v.is_current and not v.is_deleted), report.id,
            ),
            'versions': versions,
            'events': events,
        })
        return Response(serializer.data)

    @extend_schema(methods=['POST'], responses=UnitReportDetailSerializer)
    @action(detail=True, methods=['post'])
    def correct(self, request, *args, **kwargs):
        report = svc.correct_unit_report(
            self._report_or_404(), user=request.user, unit=self._unit(), enforce_permission=True,
        )
        return self._detail(report)

    @extend_schema(methods=['POST'], responses=UnitReportDetailSerializer)
    @action(detail=True, methods=['post'])
    def submit(self, request, *args, **kwargs):
        report = svc.submit_unit_report(self._report_or_404(), user=request.user, unit=self._unit(), enforce_permission=True)
        return self._detail(report)

    @extend_schema(methods=['POST'], responses=UnitReportDetailSerializer)
    @action(detail=True, methods=['post'])
    def approve(self, request, *args, **kwargs):
        report = svc.approve_unit_report(
            self._report_or_404(), user=request.user, unit=self._unit(),
            sod_checker=_sod_violation,
            enforce_permission=True,
        )
        return self._detail(report)

    @extend_schema(methods=['POST'], request=UnitReportRejectSerializer, responses=UnitReportDetailSerializer)
    @action(detail=True, methods=['post'])
    def reject(self, request, *args, **kwargs):
        payload = UnitReportRejectSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        report = svc.reject_unit_report(
            self._report_or_404(),
            user=request.user,
            rejection_reason=payload.validated_data['rejection_reason'],
            unit=self._unit(),
            enforce_permission=True,
        )
        return self._detail(report)


def _sod_violation(report, approver):
    """Existing stable SoD contract: preparer/submitter may not approve."""
    if getattr(approver, 'is_superuser', False):
        return None
    if report.created_by_id == approver.id:
        return _('sod_self_approve')
    if report.submitted_by_id == approver.id:
        return _('sod_self_approve')
    return None


@method_decorator(transaction.atomic, name='dispatch')
class UnitReportActivitySectionViewSet(viewsets.GenericViewSet):
    """§1 executed-activity child rows bound to one unit-report version (033).

    Reads require ``view_reports``; mutations require ``edit_reports`` and
    the 032 edit rule (current draft/rejected version, same project scope).
    Contract violations render as a fielded 422 envelope carrying stable
    codes + localized messages (contracts/unit-report-sections-api.md §1).
    """

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.action == 'list':
            return 'view_reports'
        return 'edit_reports'

    # -- helpers ---------------------------------------------------------

    def _unit(self):
        unit = self.kwargs.get('unit')
        if not is_canonical_unit(unit):
            raise svc.UnitReportError(_('invalid_specialty_unit'), 'invalid_specialty_unit')
        return unit

    def _report(self):
        return svc.get_scoped_report(
            project_id=self.kwargs['project_pk'], unit=self._unit(),
            report_id=self.kwargs['pk'],
        )

    def _editable_report(self):
        report = self._report()
        return svc.lock_editable_report(report, self.request.user, unit=self._unit(), enforce_permission=True)

    def _row(self, report):
        try:
            return report.activities.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except DisciplineSubReportActivity.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _rows(self, saved, code=status.HTTP_200_OK):
        return Response(UnitReportActivitySectionSerializer(saved, many=True).data, code)

    def _violation(self, exc: SectionContractError):
        return Response(
            {
                'error': {
                    'code': exc.codes[0] if exc.codes else 'section_contract_violation',
                    'message': (
                        exc.messages[0] if exc.messages
                        else str(_('invalid section payload'))
                    ),
                    'details': {'errors': exc.errors},
                },
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    # -- endpoints -------------------------------------------------------

    @extend_schema(responses={200: UnitReportActivitySectionSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = report.activities.filter(is_deleted=False).order_by('row_number', 'id')
        return self._rows(rows)

    @extend_schema(
        request=UnitReportActivitySectionSerializer,
        responses={201: UnitReportActivitySectionSerializer(many=True)},
    )
    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        try:
            saved = validate_activity_rows(report, rows, context={'request': request})
        except SectionContractError as exc:
            return self._violation(exc)
        return self._rows(saved, status.HTTP_201_CREATED)

    @extend_schema(
        request=UnitReportActivitySectionSerializer,
        responses={200: UnitReportActivitySectionSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        try:
            updated = update_activity_row(
                report, row, request.data, context={'request': request},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return Response(UnitReportActivitySectionSerializer(updated).data)

    def destroy(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class UnitReportLaborSectionViewSet(viewsets.GenericViewSet):
    """§2 labor child rows bound to one unit-report version (feature 033, T021).

    Reads require ``view_reports``; mutations require ``edit_reports`` and
    the 032 edit rule (current draft/rejected version, same project scope).
    """

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.action == 'list':
            return 'view_reports'
        return 'edit_reports'

    def _unit(self):
        unit = self.kwargs.get('unit')
        if not is_canonical_unit(unit):
            raise svc.UnitReportError(_('invalid_specialty_unit'), 'invalid_specialty_unit')
        return unit

    def _report(self):
        return svc.get_scoped_report(
            project_id=self.kwargs['project_pk'],
            unit=self._unit(),
            report_id=self.kwargs['pk'],
        )

    def _editable_report(self):
        report = self._report()
        return svc.lock_editable_report(report, self.request.user, unit=self._unit(), enforce_permission=True)

    def _row(self, report):
        try:
            return report.labor_entries.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except DisciplineSubReportLabor.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _rows(self, report, saved, code=status.HTTP_200_OK):
        data = UnitReportLaborSectionSerializer(
            saved, many=True, context={'request': self.request, 'report': report},
        ).data
        data_sorted = sorted(
            data,
            key=lambda r: (
                0 if r.get('labor_category') == 'indirect' else 1,
                r.get('display_order') or 0,
                r.get('job_title') or '',
            ),
        )
        return Response(data_sorted, code)

    def _violation(self, exc: SectionContractError):
        return Response(
            {
                'error': {
                    'code': exc.codes[0] if exc.codes else 'section_contract_violation',
                    'message': (
                        exc.messages[0]
                        if exc.messages
                        else str(_('invalid section payload'))
                    ),
                    'details': {'errors': exc.errors},
                },
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @extend_schema(responses={200: UnitReportLaborSectionSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = report.labor_entries.filter(is_deleted=False).select_related('contractor_ref').order_by('id')
        return self._rows(report, rows)

    @extend_schema(
        request=UnitReportLaborSectionSerializer,
        responses={201: UnitReportLaborSectionSerializer(many=True)},
    )
    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        try:
            saved = validate_labor_rows(
                report, rows, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return self._rows(report, saved, status.HTTP_201_CREATED)

    @extend_schema(
        request=UnitReportLaborSectionSerializer,
        responses={200: UnitReportLaborSectionSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        try:
            updated = update_labor_row(
                report, row, request.data, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return Response(
            UnitReportLaborSectionSerializer(
                updated, context={'request': request, 'report': report},
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class UnitReportMachinerySectionViewSet(viewsets.GenericViewSet):
    """§3 machinery child rows bound to one unit-report version (feature 033, T028).

    Reads require ``view_reports``; mutations require ``edit_reports`` and
    the 032 edit rule (current draft/rejected version, same project scope).
    """

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.action == 'list':
            return 'view_reports'
        return 'edit_reports'

    def _unit(self):
        unit = self.kwargs.get('unit')
        if not is_canonical_unit(unit):
            raise svc.UnitReportError(_('invalid_specialty_unit'), 'invalid_specialty_unit')
        return unit

    def _report(self):
        return svc.get_scoped_report(
            project_id=self.kwargs['project_pk'],
            unit=self._unit(),
            report_id=self.kwargs['pk'],
        )

    def _editable_report(self):
        report = self._report()
        return svc.lock_editable_report(report, self.request.user, unit=self._unit(), enforce_permission=True)

    def _row(self, report):
        try:
            return report.machinery_rows.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except DisciplineSubReportMachinery.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _rows(self, report, saved, code=status.HTTP_200_OK):
        data = UnitReportMachinerySectionSerializer(
            saved, many=True, context={'request': self.request, 'report': report},
        ).data
        if self.request.query_params.get('include_vocabulary') in ('1', 'true', 'yes'):
            vocabulary = resolve_stoppage_vocabulary(report)
            return Response({'rows': data, 'stoppage_reasons': vocabulary}, code)
        return Response(data, code)

    def _violation(self, exc: SectionContractError):
        return Response(
            {
                'error': {
                    'code': exc.codes[0] if exc.codes else 'section_contract_violation',
                    'message': (
                        exc.messages[0]
                        if exc.messages
                        else str(_('invalid section payload'))
                    ),
                    'details': {'errors': exc.errors},
                },
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @extend_schema(responses={200: UnitReportMachinerySectionSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = (
            report.machinery_rows.filter(is_deleted=False)
            .select_related('equipment_ref')
            .order_by('row_number', 'id')
        )
        return self._rows(report, rows)

    @extend_schema(
        request=UnitReportMachinerySectionSerializer,
        responses={201: UnitReportMachinerySectionSerializer(many=True)},
    )
    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        try:
            saved = validate_machinery_rows(
                report, rows, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return self._rows(report, saved, status.HTTP_201_CREATED)

    @extend_schema(
        request=UnitReportMachinerySectionSerializer,
        responses={200: UnitReportMachinerySectionSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        try:
            updated = update_machinery_row(
                report, row, request.data, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return Response(
            UnitReportMachinerySectionSerializer(
                updated, context={'request': request, 'report': report},
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(transaction.atomic, name='dispatch')
class UnitReportMaterialSectionViewSet(viewsets.GenericViewSet):
    """§4 material child rows bound to one unit-report version (feature 033, T035).

    Reads require ``view_reports``; mutations require ``edit_reports`` and
    the 032 edit rule (current draft/rejected version, same project scope).
    """

    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.action == 'list':
            return 'view_reports'
        return 'edit_reports'

    def _unit(self):
        unit = self.kwargs.get('unit')
        if not is_canonical_unit(unit):
            raise svc.UnitReportError(_('invalid_specialty_unit'), 'invalid_specialty_unit')
        return unit

    def _report(self):
        return svc.get_scoped_report(
            project_id=self.kwargs['project_pk'],
            unit=self._unit(),
            report_id=self.kwargs['pk'],
        )

    def _editable_report(self):
        report = self._report()
        return svc.lock_editable_report(report, self.request.user, unit=self._unit(), enforce_permission=True)

    def _row(self, report):
        try:
            return report.material_entries.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except DisciplineSubReportMaterial.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _rows(self, report, saved, code=status.HTTP_200_OK):
        data = UnitReportMaterialSectionSerializer(
            saved, many=True, context={'request': self.request, 'report': report},
        ).data
        return Response(data, code)

    def _violation(self, exc: SectionContractError):
        return Response(
            {
                'error': {
                    'code': exc.codes[0] if exc.codes else 'section_contract_violation',
                    'message': (
                        exc.messages[0]
                        if exc.messages
                        else str(_('invalid section payload'))
                    ),
                    'details': {'errors': exc.errors},
                },
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @extend_schema(responses={200: UnitReportMaterialSectionSerializer(many=True)})
    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = (
            report.material_entries.filter(is_deleted=False)
            .select_related('material_ref')
            .order_by('id')
        )
        return self._rows(report, rows)

    @extend_schema(
        request=UnitReportMaterialSectionSerializer,
        responses={201: UnitReportMaterialSectionSerializer(many=True)},
    )
    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        try:
            saved = validate_material_rows(
                report, rows, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return self._rows(report, saved, status.HTTP_201_CREATED)

    @extend_schema(
        request=UnitReportMaterialSectionSerializer,
        responses={200: UnitReportMaterialSectionSerializer},
    )
    def partial_update(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        try:
            updated = update_material_row(
                report, row, request.data, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return Response(
            UnitReportMaterialSectionSerializer(
                updated, context={'request': request, 'report': report},
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        report = self._editable_report()
        row = self._row(report)
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UnitReportConcreteSectionViewSet(UnitReportMaterialSectionViewSet):
    """§5 concrete pour rows (feature 033, T041)."""

    def _row(self, report):
        try:
            return report.concrete_entries.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except DisciplineSubReportConcrete.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _rows(self, report, saved, code=status.HTTP_200_OK):
        data = UnitReportConcreteSectionSerializer(
            saved, many=True, context={'request': self.request, 'report': report},
        ).data
        return Response(data, code)

    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = report.concrete_entries.filter(is_deleted=False).order_by('id')
        return self._rows(report, rows)

    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        try:
            saved = validate_concrete_rows(
                report, rows, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return self._rows(report, saved, status.HTTP_201_CREATED)


class _NarrativeSectionViewSet(UnitReportMaterialSectionViewSet):
    narrative_kind = 'issue'
    row_model = DisciplineSubReportIssue
    related = 'issues'

    def _row(self, report):
        try:
            return getattr(report, self.related).get(pk=self.kwargs['row_pk'], is_deleted=False)
        except self.row_model.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')

    def _present(self, rows, code=status.HTTP_200_OK):
        data = []
        for row in rows:
            item = {
                'id': str(row.id),
                'row_number': getattr(row, 'row_number', 1),
                'text': getattr(row, 'text', ''),
                'kind': getattr(row, 'kind', self.narrative_kind),
            }
            if hasattr(row, 'owner_user_id'):
                item['owner_user'] = str(row.owner_user_id) if row.owner_user_id else None
                item['due_date'] = row.due_date.isoformat() if getattr(row, 'due_date', None) else None
            if hasattr(row, 'severity'):
                item['severity'] = row.severity
                item['immediate_action'] = row.immediate_action
            if hasattr(row, 'activity_description'):
                item['activity_description'] = row.activity_description
                item['location'] = row.location
                item['quantity'] = str(row.quantity) if row.quantity is not None else None
                item['unit'] = row.unit
                item['notes'] = row.notes
            data.append(item)
        return Response(data, status=code)

    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = getattr(report, self.related).filter(is_deleted=False).order_by('row_number', 'id')
        return self._present(rows)

    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        payload = request.data
        rows = payload if isinstance(payload, list) else [payload]
        stamped = []
        for row in rows:
            item = dict(row)
            item['kind'] = self.narrative_kind
            stamped.append(item)
        try:
            saved = validate_narrative_rows(
                report, stamped, context={'request': request, 'report': report},
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return self._present(saved, status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UnitReportIssueSectionViewSet(_NarrativeSectionViewSet):
    narrative_kind = 'issue'
    row_model = DisciplineSubReportIssue
    related = 'issues'


class UnitReportVisitSectionViewSet(_NarrativeSectionViewSet):
    narrative_kind = 'visit'
    row_model = DisciplineSubReportVisit
    related = 'visits'


class UnitReportHseSectionViewSet(_NarrativeSectionViewSet):
    narrative_kind = 'hse'
    row_model = DisciplineSubReportHseIncident
    related = 'hse_incidents'


class UnitReportGeneralSectionViewSet(_NarrativeSectionViewSet):
    narrative_kind = 'general_activity'
    row_model = DisciplineSubReportGeneralActivity
    related = 'general_activities'


class UnitReportAttachmentSectionViewSet(UnitReportMaterialSectionViewSet):
    """JPEG/PNG activity images (feature 033, T051). Local storage key when MinIO is absent."""

    def list(self, request, *args, **kwargs):
        report = self._report()
        rows = report.attachments.filter(is_deleted=False).order_by('id')
        return Response([
            {
                'id': str(row.id),
                'row_kind': row.row_kind,
                'row_id': row.row_id,
                'declared_content_type': row.declared_content_type,
                'size_bytes': row.size_bytes,
                'capture_date': row.capture_date.isoformat() if row.capture_date else None,
                'work_front': row.work_front,
            }
            for row in rows
        ])

    def create(self, request, *args, **kwargs):
        report = self._editable_report()
        upload = request.FILES.get('file')
        content = upload.read() if upload is not None else b''
        try:
            saved = attach_image_to_activity(
                report=report,
                activity_row_id=request.data.get('row_id') or request.data.get('activity_row_id'),
                file_content=content,
                declared_content_type=(
                    request.data.get('declared_content_type')
                    or getattr(upload, 'content_type', '')
                ),
                capture_date=request.data.get('capture_date') or None,
                work_front=request.data.get('work_front') or '',
            )
        except SectionContractError as exc:
            return self._violation(exc)
        return Response(
            {'id': str(saved.id), 'row_kind': saved.row_kind, 'row_id': saved.row_id},
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        report = self._editable_report()
        try:
            row = report.attachments.get(pk=self.kwargs['row_pk'], is_deleted=False)
        except UnitReportAttachment.DoesNotExist:
            raise svc.UnitReportNotFound(_('unit_report_not_found'), 'unit_report_not_found')
        row.is_deleted = True
        row.deleted_at = timezone.now()
        row.save(update_fields=['is_deleted', 'deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SyncOperationsV2View(APIView):
    """Versioned targeted synchronization endpoint (v2, Feature 037).

    Scoped under /api/v1/projects/{project_pk}/daily-reports/sync-operations/v2/.
    Kept disabled until full foundation and reader/writer deployment verification.
    """
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_reports'

    def post(self, request, project_pk):
        if not getattr(settings, 'V2_OFFLINE_SYNC_ENABLED', False):
            raise Http404('v2 sync operations endpoint is disabled')
        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            raise Http404('project not found')
        try:
            payload = dispatch_operations(project=project, actor=request.user, body=request.data)
        except PermissionDenied:
            return Response({'detail': 'Current project edit permission is required'}, status=status.HTTP_403_FORBIDDEN)
        return Response(payload, status=status.HTTP_200_OK)


class ContractorLaborLedgerView(APIView):
    """Returns labor ledger entries credited to a contractor for a project (feature 038, US6)."""
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_reports'

    def get(self, request, project_pk, contractor_pk):
        from sub_reports.models import SubcontractorLaborLedgerEntry
        from projects.models import Stakeholder

        try:
            contractor = Stakeholder.objects.get(id=contractor_pk, project_id=project_pk, is_deleted=False)
        except Stakeholder.DoesNotExist:
            raise svc.UnitReportNotFound(_('contractor_not_found'), 'contractor_not_found')

        entries = SubcontractorLaborLedgerEntry.objects.filter(
            project_id=project_pk,
            contractor=contractor,
        ).order_by('-report_date', 'created_at')

        total = sum((e.total_person_hours for e in entries), Decimal('0.00'))

        data = {
            'project_id': str(project_pk),
            'contractor_id': str(contractor_pk),
            'contractor_name': contractor.name,
            'total_person_hours': str(total),
            'entries': [
                {
                    'id': str(e.id),
                    'report_date': str(e.report_date),
                    'discipline': e.discipline,
                    'activity_row_id': str(e.activity_row_id),
                    'foreman_count': e.foreman_count,
                    'worker_count': e.worker_count,
                    'shift_hours': str(e.shift_hours),
                    'total_person_hours': str(e.total_person_hours),
                    'status': e.status,
                }
                for e in entries
            ],
        }
        return Response(data, status=status.HTTP_200_OK)



