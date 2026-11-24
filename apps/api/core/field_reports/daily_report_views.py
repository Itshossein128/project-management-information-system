"""Daily report CRUD, approval workflow, offline sync-batch and PDF export."""
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Exists, OuterRef
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import WorkflowViewSetMixin
from common.jalali import gregorian_to_jalali, parse_date_optional
from config.exceptions import CodedValidationError, ConflictError
from config.pagination import DefaultPageNumberPagination
from permissions.project import CanReadReportExport, HasProjectPermission, IsProjectMember
from projects.models import Project, Stakeholder
from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportCorrectionRequest,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportLaborCamp,
    DailyReportMaterial,
    ReportShift,
    ReportStatus,
    SiteStatus,
)
from field_reports.models import LaborJobTitle
from field_reports.serializers import (
    DailyReportActivitySerializer,
    DailyReportConcreteLogSerializer,
    DailyReportCorrectionRequestSerializer,
    DailyReportDetailSerializer,
    DailyReportEquipmentSerializer,
    DailyReportHeaderSerializer,
    DailyReportIncidentSerializer,
    DailyReportLaborCampSerializer,
    DailyReportLaborSerializer,
    DailyReportListSerializer,
    DailyReportMaterialSerializer,
    DailyReportVersionSerializer,
    LaborJobTitleSerializer,
)
from field_reports import services
from field_reports.services import correction_service, data_contract
from field_reports.services.activity_log import scoped_filter_id
from field_reports.services.form_profiles import resolve_labor_rows_for_profile
from field_reports.services.lifecycle_errors import lifecycle_error_detail, get_lifecycle_msg
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    ensure_daily_report_summary,
    rebuild_daily_report_summary,
)
from field_reports.services.material_reconciliation import reconcile_report_materials

EDITABLE_STATUSES = {ReportStatus.DRAFT, ReportStatus.REJECTED}
AUTO_SUMMARY_CREATE_MSG = (
    'گزارش روزانه پروژه به‌صورت خودکار از گزارش‌های واحد تخصصی ساخته می‌شود. '
    'از مسیر by-date استفاده کنید.'
)
DERIVED_READONLY_MSG = 'این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید'


def _validate_report_ready_for_submit(report: DailyReport, request=None) -> list[str]:
    """Return soft warnings. Raises ValidationError for hard failures."""
    errors: list[str] = []
    warnings: list[str] = []

    if not (report.work_front or '').strip():
        warnings.append('محل/جبهه کاری خالی است — تکمیل آن توصیه می‌شود')

    activities = list(report.activities.filter(is_deleted=False))
    if not activities:
        errors.append('گزارش باید حداقل یک فعالیت داشته باشد')
    for idx, row in enumerate(activities, start=1):
        if row.quantity_measured and row.quantity is None:
            raise ValidationError({
                'detail': [lifecycle_error_detail(
                    'quantity_unset_invalid',
                    request=request,
                )],
            })
        if (not row.quantity_measured) and row.quantity is not None:
            errors.append(f'ردیف فعالیت {idx}: مقدار ثبت‌نشده نباید عدد داشته باشد')

    equipment_rows = list(report.equipment_entries.filter(is_deleted=False))
    for idx, row in enumerate(equipment_rows, start=1):
        has_start = bool(row.work_start)
        has_end = bool(row.work_end)
        if has_start != has_end:
            errors.append(f'ردیف ماشین‌آلات {idx}: ساعت شروع و پایان باید با هم ثبت شوند')

    camp_rows = list(report.labor_camp_entries.filter(is_deleted=False))
    for idx, row in enumerate(camp_rows, start=1):
        if (row.present_count + row.on_leave_count) != row.total_residents:
            errors.append(
                f'ردیف کمپ {idx}: مجموع حاضر و مرخصی باید با کل ساکنین برابر باشد',
            )
        if row.total_residents > row.capacity:
            errors.append(f'ردیف کمپ {idx}: کل ساکنین نمی‌تواند بیشتر از ظرفیت باشد')

    if errors:
        raise ValidationError({'submit_validation': errors})
    return warnings


@extend_schema_view(
    list=extend_schema(summary='List daily reports', tags=['Daily Reports']),
    create=extend_schema(summary='Create daily report header', tags=['Daily Reports']),
    retrieve=extend_schema(summary='Get daily report with child rows', tags=['Daily Reports']),
    partial_update=extend_schema(summary='Update daily report header', tags=['Daily Reports']),
    destroy=extend_schema(summary='Soft-delete daily report', tags=['Daily Reports']),
)
class DailyReportViewSet(WorkflowViewSetMixin, viewsets.ModelViewSet):
    lookup_url_kwarg = 'pk'
    pagination_class = DefaultPageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    view_permission = 'view_reports'
    edit_permission = 'edit_reports'
    approve_permission = 'approve_reports'

    def get_project_id(self):
        return self.kwargs['project_pk']

    @property
    def required_permission(self):
        if self.action == 'by_date':
            if self.request.method.upper() == 'GET':
                return self.view_permission
            return self.edit_permission
        if self.action in (
            'list', 'retrieve', 'pdf', 'excel', 'excel_range', 'versions', 'materials_reconciliation',
            'materials_details', 'provenance', 'contract', 'contract_summary',
        ):
            return self.view_permission
        if self.action == 'correction_requests' and self.request.method.upper() == 'GET':
            return self.view_permission
        if self.action in ('review', 'approve', 'reject'):
            return self.approve_permission
        return self.edit_permission

    def get_permissions(self):
        if self.action in ('pdf', 'excel', 'excel_range'):
            return [IsAuthenticated(), CanReadReportExport()]
        if self.action in (
            'list', 'retrieve', 'versions', 'materials_reconciliation',
            'materials_details', 'provenance', 'contract', 'contract_summary', 'by_date',
        ) or (
            self.action == 'correction_requests' and self.request.method.upper() == 'GET'
        ):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    # Queries: before optimization=47, after=4 (list with select_related + prefetch_related)
    def get_queryset(self):
        qs = (
            DailyReport.objects.filter(project_id=self.get_project_id(), is_deleted=False)
            .select_related('project', 'prepared_by', 'submitted_by', 'reviewed_by', 'approved_by')
            .prefetch_related('activities', 'labor_entries', 'equipment_entries', 'machinery_rows', 'incidents')
        )
        if self.action in ('excel', 'pdf'):
            return qs
        params = self.request.query_params
        try:
            date_from = parse_date_optional(params.get('date_from'))
            date_to = parse_date_optional(params.get('date_to'))
        except (ValueError, OverflowError):
            if self.action == 'list':
                return qs.none()
            raise
        if date_from:
            qs = qs.filter(report_date__gte=date_from)
        if date_to:
            qs = qs.filter(report_date__lte=date_to)
        status_filter = params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        try:
            for parameter, column in (('prepared_by', 'prepared_by_id'), ('lineage_id', 'lineage_id')):
                if params.get(parameter):
                    qs = qs.filter(**{column: params[parameter]})
        except DjangoValidationError:
            if self.action == 'list':
                return qs.none()
            raise
        is_current = params.get('is_current')
        if is_current is None and self.action == 'list':
            qs = qs.filter(is_current=True)
        elif is_current is not None:
            qs = qs.filter(is_current=is_current.lower() in ('1', 'true', 'yes'))
        if self.action == 'list':
            dimensions = {}
            if params.get('discipline'):
                discipline = params['discipline'].strip()
                if not discipline:
                    return qs.none()
                dimensions['source_discipline__iexact'] = discipline
            if params.get('block'):
                dimensions['block'] = params['block']
            if params.get('contractor'):
                contractor = scoped_filter_id(Stakeholder, self.get_project_id(), params['contractor'])
                if contractor is None:
                    return qs.none()
                dimensions['contractor_ref_id'] = contractor
            if dimensions:
                eligible = DailyReportActivity.objects.filter(report_id=OuterRef('pk'), is_deleted=False)
                qs = qs.filter(Exists(eligible.filter(**dimensions)))
            return qs.order_by('-report_date', 'pk')
        return qs.order_by('-report_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyReportListSerializer
        if self.action in ('create', 'partial_update'):
            return DailyReportHeaderSerializer
        return DailyReportDetailSerializer

    # -- CRUD ---------------------------------------------------------------

    @action(detail=False, methods=['get'], url_path='contract')
    def contract(self, request, *args, **kwargs):
        get_object_or_404(Project, pk=self.get_project_id())
        include_mappings = request.query_params.get('include_mappings', 'true').lower()
        if include_mappings not in ('true', 'false'):
            raise ValidationError({'include_mappings': _('Expected true or false.')})
        contract = data_contract.load_daily_report_contract()
        if include_mappings == 'false':
            contract.pop('field_mappings')
        profile = request.query_params.get('profile')
        if profile is not None:
            if profile not in contract['form_profiles']:
                raise ValidationError({'profile': _('Unknown daily report form profile.')})
            contract['form_profiles'] = {profile: contract['form_profiles'][profile]}
        return Response(contract)

    @action(detail=True, methods=['get'], url_path='contract-summary')
    def contract_summary(self, request, *args, **kwargs):
        report = get_object_or_404(
            DailyReport.objects.select_related('project'),
            pk=self.kwargs['pk'], project_id=self.get_project_id(),
        )
        self.check_object_permissions(request, report)
        contract = data_contract.load_daily_report_contract()
        header = data_contract.project_report_header(report, preview=True)
        labor_summary = None
        if report.presentation_profile_code:
            try:
                profile = resolve_labor_rows_for_profile(
                    report.labor_entries.filter(is_deleted=False), report.presentation_profile_code,
                )
            except DjangoValidationError as exc:
                raise ValidationError({'profile': exc.messages}) from exc
            labor_summary = {
                'profile_code': profile['profile_code'],
                'standard_indirect_slots': len(profile['standard_indirect']),
                'standard_direct_slots': len(profile['standard_direct']),
                'appendix_indirect_count': len(profile['appendix_indirect']),
                'appendix_direct_count': len(profile['appendix_direct']),
            }
        signature_scope = contract['signature_scope']
        return Response({
            'contract_version': report.contract_version or None,
            'is_synthetic_reference': report.is_synthetic_reference,
            **header,
            'labor_profile_resolution': labor_summary,
            'signature_scope': {
                'mode': signature_scope['mode'],
                'pki_digital_signature_claimed': signature_scope['pki_digital_signature_in_scope'],
                'whole_body_tamper_seal_claimed': signature_scope['whole_report_tamper_seal_in_scope'],
            },
        })

    def create(self, request, *args, **kwargs):
        if services._derived_sections_in_payload(request.data):
            raise ValidationError({'detail': DERIVED_READONLY_MSG, 'code': 'derived_readonly'})
        raise ValidationError({'detail': AUTO_SUMMARY_CREATE_MSG, 'code': 'auto_summary_only'})

    @action(detail=False, methods=['get', 'post'], url_path='by-date')
    def by_date(self, request, *args, **kwargs):
        if request.method.upper() == 'POST' and services._derived_sections_in_payload(request.data):
            raise ValidationError({'detail': DERIVED_READONLY_MSG, 'code': 'derived_readonly'})
        raw = request.query_params.get('date') or request.data.get('report_date') or request.data.get('date')
        report_date = parse_date_optional(raw)
        if report_date is None:
            raise ValidationError({'date': 'تاریخ الزامی است', 'code': 'date_required'})

        raw_shift = request.query_params.get('shift') or request.data.get('shift')
        project_id = self.get_project_id()
        contract_report = DailyReport.objects.filter(
            project_id=project_id, report_date=report_date, is_current=True,
        ).exclude(contract_version='').first()
        if contract_report is not None:
            worked_shifts = contract_report.canonical_worked_shift_ids
            if raw_shift is not None:
                try:
                    canonical_shift = data_contract.normalize_canonical_shift_id(raw_shift)
                except DjangoValidationError as exc:
                    raise ValidationError({'shift': exc.messages}) from exc
                if canonical_shift not in worked_shifts:
                    raise NotFound(_('This shift did not work on the selected report date.'))
            response = DailyReportDetailSerializer(contract_report, context={'request': request}).data
            response['canonical_worked_shift_ids'] = worked_shifts
            return Response(response)

        shift = ReportShift.FULL
        if raw_shift:
            shift_map = {
                '1': ReportShift.DAY,
                '2': ReportShift.NIGHT,
                'day': ReportShift.DAY,
                'night': ReportShift.NIGHT,
                'full': ReportShift.FULL,
                'shift_1': ReportShift.DAY,
                'shift_2': ReportShift.NIGHT,
            }
            shift = shift_map.get(str(raw_shift).lower(), raw_shift)

        if request.method.upper() == 'GET':
            report = (
                DailyReport.objects.filter(
                    project_id=project_id,
                    report_date=report_date,
                    shift=shift,
                    is_deleted=False,
                    is_current=True,
                )
                .order_by('-created_at')
                .first()
            )
            if report is None:
                report = ensure_daily_report_summary(
                    project_id, report_date, user=request.user, shift=shift,
                )
            return Response(DailyReportDetailSerializer(report, context={'request': request}).data)

        created_before = DailyReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            shift=shift,
            is_deleted=False,
            is_current=True,
        ).exists()
        report = ensure_daily_report_summary(
            project_id, report_date, user=request.user, shift=shift,
        )
        status_code = status.HTTP_200_OK if created_before else status.HTTP_201_CREATED
        return Response(DailyReportDetailSerializer(report, context={'request': request}).data, status=status_code)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        from permissions.project import member_has_codename
        from projects.models import Project
        from rest_framework.exceptions import PermissionDenied

        Project.objects.select_for_update().get(pk=self.get_project_id())
        instance = self.get_object()
        instance = DailyReport.objects.select_for_update().get(pk=instance.pk, project_id=self.get_project_id())
        if instance.is_deleted or not instance.is_current:
            raise ValidationError({'detail': lifecycle_error_detail('report_not_current', request=request), 'code': 'report_not_current'})
        if not member_has_codename(request.user, self.get_project_id(), 'edit_reports'):
            raise PermissionDenied('Current project edit permission is required')
        from field_reports.services.derived_lock import report_has_derived_rows
        if (not instance.is_current or instance.is_deleted) and set(request.data) & {
            'activities', 'labor', 'labor_entries', 'materials', 'material_entries',
            'concrete_logs', 'machinery_rows', 'general_activities', 'visits', 'incidents',
        }:
            raise ValidationError({'detail': lifecycle_error_detail('report_not_current', request=request), 'code': 'report_not_current'})
        if report_has_derived_rows(instance) and services._derived_sections_in_payload(request.data):
            raise ValidationError({'detail': lifecycle_error_detail('derived_readonly', request=request), 'code': 'derived_readonly'})
        if instance.status == ReportStatus.APPROVED:
            raise ValidationError({'detail': lifecycle_error_detail('report_locked', request=request), 'code': 'report_locked'})
        # Auto-summary allows metadata/overrides even when not draft if still editable workflow.
        if instance.is_auto_summary:
            allowed = {
                'management_opinion', 'general_notes', 'weather_condition', 'site_status',
                'weather_override', 'site_status_override', 'temp_min', 'temp_max',
                'work_front', 'location_notes', 'weather_impact_notes', 'inactivity_reason',
            }
            if instance.status not in EDITABLE_STATUSES and not set(request.data).issubset(allowed):
                raise ValidationError('فقط گزارش‌های پیش‌نویس یا رد شده قابل ویرایش هستند')
            if instance.status not in EDITABLE_STATUSES:
                data = {k: v for k, v in request.data.items() if k in allowed}
                serializer = DailyReportHeaderSerializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(updated_by=request.user)
                instance.refresh_from_db()
                return Response(DailyReportDetailSerializer(instance, context={'request': request}).data)
        elif instance.status not in EDITABLE_STATUSES:
            raise ValidationError('فقط گزارش‌های پیش‌نویس یا رد شده قابل ویرایش هستند')

        if instance.status in EDITABLE_STATUSES and 'activities' in request.data:
            activities_data = request.data['activities']
            if isinstance(activities_data, list):
                from projects.models import Activity, Stakeholder
                from contracts.models import Contract

                for row in activities_data:
                    for key, model in (
                        ('activity_ref', Activity), ('contractor_ref', Stakeholder),
                        ('subcontractor_ref', Contract),
                    ):
                        ref = row.get(key)
                        if not ref:
                            continue
                        try:
                            exists = model.objects.filter(pk=ref, project_id=instance.project_id).exists()
                        except (DjangoValidationError, ValueError):
                            exists = False
                        if not exists:
                            raise ValidationError({key: _('Select a reference in the current project.')})
                instance.activities.all().delete()
                for row in activities_data:
                    qm = row.get('quantity_measured')
                    if qm is None:
                        qm = row.get('quantity') is not None
                    DailyReportActivity.objects.create(
                        report=instance,
                        activity_ref_id=row.get('activity_ref'),
                        activity_description=row.get('activity_description', ''),
                        shift=row.get('shift', 'shift_1'),
                        unit=row.get('unit', ''),
                        quantity=row.get('quantity'),
                        quantity_measured=bool(qm),
                        subcontractor_name=row.get('subcontractor_name', ''),
                        subcontractor_ref_id=row.get('subcontractor_ref'),
                        contractor_ref_id=row.get('contractor_ref'),
                        crew_name=row.get('crew_name', ''),
                        headcount=row.get('headcount'),
                        foreman_count=row.get('foreman_count'),
                        worker_count=row.get('worker_count'),
                        parcel=row.get('parcel'),
                        zone=row.get('zone'),
                        block=row.get('block'),
                        floor=row.get('floor'),
                        location_detail=row.get('location_detail'),
                        notes=row.get('notes', ''),
                    )

        header_data = {k: v for k, v in request.data.items() if k != 'activities'}
        if header_data:
            serializer = DailyReportHeaderSerializer(instance, data=header_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_by=request.user)
        instance.refresh_from_db()
        return Response(DailyReportDetailSerializer(instance, context={'request': request}).data)
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ReportStatus.DRAFT:
            raise ValidationError('فقط گزارش‌های پیش‌نویس قابل حذف هستند')
        instance.soft_delete(user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # -- Workflow -----------------------------------------------------------

    def _submit(self, instance, request):
        if instance.status not in EDITABLE_STATUSES:
            raise ValidationError({'detail': [lifecycle_error_detail(
                'report_not_in_submittable_state',
                request=request,
            )]})
        if instance.site_status == SiteStatus.INACTIVE and not instance.inactivity_reason:
            raise ValidationError(
                {'inactivity_reason': [ErrorDetail('در صورت تعطیلی کارگاه، انتخاب علت الزامی است.', code='inactivity_reason_required')]},
            )
        warnings = _validate_report_ready_for_submit(instance, request=request)
        services.submit_report(instance, request.user)
        data = DailyReportDetailSerializer(instance, context={'request': request}).data
        if warnings:
            data['submit_warnings'] = warnings
        return Response(data)

    @extend_schema(summary='Mark under review', tags=['Daily Reports'])
    @action(detail=True, methods=['post'])
    def review(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ReportStatus.SUBMITTED:
            raise ValidationError('فقط گزارش‌های ارسال شده قابل بررسی هستند')
        if instance.site_status == SiteStatus.INACTIVE and not instance.inactivity_reason:
            raise ValidationError(
                {'inactivity_reason': [ErrorDetail('در صورت تعطیلی کارگاه، انتخاب علت الزامی است.', code='inactivity_reason_required')]},
            )
        services.review_report(instance, request.user, request.data.get('notes', ''))
        return Response(DailyReportDetailSerializer(instance, context={'request': request}).data)

    def _approve(self, instance, request):
        if instance.status not in (ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW):
            raise ValidationError('فقط گزارش‌های ارسال شده یا در حال بررسی قابل تأیید هستند')
        if instance.submitted_by_id and instance.submitted_by_id == request.user.id:
            raise ValidationError({
                'detail': lifecycle_error_detail('sod_self_approval_forbidden', request=request),
                'code': 'sod_self_approval_forbidden',
            })
        if instance.site_status == SiteStatus.INACTIVE and not instance.inactivity_reason:
            raise ValidationError(
                {'inactivity_reason': [ErrorDetail('در صورت تعطیلی کارگاه، انتخاب علت الزامی است.', code='inactivity_reason_required')]},
            )
        services.approve_report(instance, request.user)
        return Response(DailyReportDetailSerializer(instance, context={'request': request}).data)

    def _reject(self, instance, request):
        if instance.status not in (ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW):
            raise ValidationError('فقط گزارش‌های ارسال شده یا در حال بررسی قابل رد هستند')
        reason = (request.data.get('reason') or '').strip()
        if not reason:
            # Same localized ErrorDetail under both `detail` and `reason`: the
            # exception handler picks `detail` for an unprefixed error.message
            # while the reason field error survives in error.details.
            raise ValidationError({
                'detail': [lifecycle_error_detail(
                    'rejection_reason_required',
                    request=request,
                )],
                'reason': [lifecycle_error_detail(
                    'rejection_reason_required',
                    request=request,
                )],
            })
        if len(reason) < 10:
            raise ValidationError({
                'detail': [lifecycle_error_detail(
                    'rejection_reason_min_length_10',
                    request=request,
                )],
                'reason': [lifecycle_error_detail(
                    'rejection_reason_min_length_10',
                    request=request,
                )],
            })
        services.reject_report(instance, request.user, reason)
        return Response(DailyReportDetailSerializer(instance, context={'request': request}).data)

    # -- Offline sync -------------------------------------------------------

    @extend_schema(summary='Batch-sync offline reports', tags=['Daily Reports'])
    @action(detail=False, methods=['post'], url_path='sync-batch')
    def sync_batch(self, request, *args, **kwargs):
        reports = request.data
        if not isinstance(reports, list):
            raise ValidationError('بدنه درخواست باید آرایه‌ای از گزارش‌ها باشد')
        summary = services.sync_batch(
            project_id=self.get_project_id(),
            user=request.user,
            reports=reports,
        )
        return Response(summary, status=status.HTTP_200_OK)

    # -- PDF ----------------------------------------------------------------

    @extend_schema(summary='Export report as PDF', tags=['Daily Reports'])
    @action(detail=True, methods=['get'])
    def pdf(self, request, *args, **kwargs):
        from field_reports.pdf import generate_daily_report_pdf

        instance = self.get_object()
        pdf_bytes, filename = generate_daily_report_pdf(instance, language=getattr(request, 'LANGUAGE_CODE', 'fa'))

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response

    @extend_schema(summary='Export report as Shiraz FILE 4 Excel', tags=['Daily Reports'])
    @action(detail=True, methods=['get'])
    def excel(self, request, *args, **kwargs):
        from field_reports.shiraz_file4_excel import ShirazFile4ExcelBuilder

        instance = self.get_object()
        builder = ShirazFile4ExcelBuilder(instance, language=getattr(request, 'LANGUAGE_CODE', 'fa'))
        excel_bytes, filename = builder.build()

        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @extend_schema(summary='Export current approved daily reports by date range', tags=['Daily Reports'])
    @action(detail=False, methods=['get'], url_path='excel')
    def excel_range(self, request, *args, **kwargs):
        from openpyxl import Workbook
        from field_reports.shiraz_file4_excel import ShirazFile4ExcelBuilder

        language = getattr(request, 'LANGUAGE_CODE', 'fa')
        english = language.startswith('en')
        try:
            first = parse_date_optional(request.query_params.get('date_from'))
            last = parse_date_optional(request.query_params.get('date_to'))
        except (ValueError, OverflowError):
            first = last = None
        if first is None or last is None or first > last:
            raise CodedValidationError(
                'Enter valid start and end dates in chronological order.' if english
                else 'تاریخ شروع و پایان معتبر و به ترتیب زمانی وارد کنید.',
                code='invalid_export_date_range',
            )
        max_days = settings.DAILY_REPORT_EXCEL_RANGE_MAX_DAYS
        if (last - first).days + 1 > max_days:
            raise CodedValidationError(
                f'The date range may contain at most {max_days} days.' if english
                else f'بازه خروجی حداکثر می‌تواند {max_days} روز باشد.',
                code='export_date_range_too_large',
            )

        reports = list(
            DailyReport.objects.filter(
                project_id=self.get_project_id(), report_date__range=(first, last), is_current=True,
                status=ReportStatus.APPROVED, is_deleted=False,
            ).select_related('project', 'prepared_by').prefetch_related('worked_shifts').order_by('report_date', 'pk')
        )
        if not reports:
            raise CodedValidationError(
                'No current approved reports were found in this range.' if english
                else 'گزارش جاری تأییدشده‌ای در این بازه یافت نشد.',
                code='no_reports_in_export_range',
            )
        if len({report.report_date for report in reports}) != len(reports):
            raise ConflictError(
                'More than one current approved report was found for the same date.' if english
                else 'برای یک تاریخ چند گزارش جاری تأییدشده یافت شد.',
                code='ambiguous_legacy_report_date',
            )

        workbook = Workbook()
        workbook.remove(workbook.active)
        for report in reports:
            name = gregorian_to_jalali(report.report_date).replace('/', '-')
            sheet = workbook.create_sheet(name)
            ShirazFile4ExcelBuilder(report, language=language, sheet=sheet).populate()
        output = BytesIO()
        workbook.save(output)
        from_name, to_name = (gregorian_to_jalali(value).replace('/', '-') for value in (first, last))
        response = HttpResponse(
            output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="daily-reports-{from_name}-{to_name}.xlsx"'
        return response

    # -- Versions / correction / reconciliation -----------------------------

    @extend_schema(summary='List report versions in lineage', tags=['Daily Reports'])
    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = correction_service.list_versions(instance)
        return Response(DailyReportVersionSerializer(qs, many=True).data)

    @extend_schema(summary='Rebuild an editable daily report summary', tags=['Daily Reports'])
    @action(detail=True, methods=['post'], url_path='rebuild')
    def rebuild(self, request, *args, **kwargs):
        instance = DailyReport.all_objects.filter(
            pk=self.kwargs['pk'], project_id=self.get_project_id(),
        ).first()
        if instance is None:
            raise NotFound()
        self.check_object_permissions(request, instance)
        report = rebuild_daily_report_summary(
            project_id=instance.project_id,
            report_date=instance.report_date,
            user=request.user,
            report=instance,
            shift=instance.shift,
            request=request,
        )
        return Response(DailyReportDetailSerializer(report, context={'request': request}).data)

    @extend_schema(summary='List or open correction requests', tags=['Daily Reports'])
    @action(detail=True, methods=['get', 'post'], url_path='correction-requests')
    def correction_requests(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.method.lower() == 'get':
            lineage_id = instance.lineage_id or instance.id
            qs = DailyReportCorrectionRequest.objects.filter(
                project_id=instance.project_id,
                source_report__lineage_id=lineage_id,
                is_deleted=False,
            ).order_by('-requested_at')
            return Response(DailyReportCorrectionRequestSerializer(qs, many=True).data)
        correction = correction_service.open_correction(
            source_report=instance,
            user=request.user,
            reason=request.data.get('reason', ''),
            request=request,
        )
        return Response(
            DailyReportCorrectionRequestSerializer(correction).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(summary='Provenance drill-down for one derived row', tags=['Daily Reports'])
    @action(
        detail=True,
        methods=['get'],
        url_path=r'provenance/(?P<derived_kind>[^/.]+)/(?P<derived_row>[^/.]+)',
    )
    def provenance(self, request, derived_kind=None, derived_row=None, *args, **kwargs):
        from field_reports.models import DailyReportDerivedSource
        from permissions.project import active_member_has_codename

        instance = self.get_object()
        can_view = active_member_has_codename(request.user, instance.project_id, 'view_reports')

        sources = DailyReportDerivedSource.objects.filter(
            daily_report=instance,
            derived_kind=derived_kind,
            derived_row_id=str(derived_row),
        ).select_related('source_report').order_by('ordinal', 'id')
        if not sources.exists():
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        rows = []
        for source in sources:
            if can_view and source.source_report and (
                source.source_report.project_id == instance.project_id and not source.source_report.is_deleted
            ):
                rows.append({
                    'source_report': str(source.source_report_id) if source.source_report_id else None,
                    'source_report_version': source.source_report_version,
                    'source_unit': source.source_unit,
                    'source_row_kind': source.source_row_kind,
                    'source_row_id': source.source_row_id,
                    'contribution_value': (
                        str(source.contribution_value) if source.contribution_value is not None else None
                    ),
                    'can_view_source': True,
                    'href': (
                        f'/api/v1/projects/{instance.project_id}/units/{source.source_unit}'
                        f'/daily-reports/{source.source_report_id}/'
                        if source.source_report_id and source.source_unit
                        else None
                    ),
                })
            else:
                rows.append({
                    'source_report': None,
                    'source_report_version': None,
                    'source_unit': None,
                    'source_row_kind': None,
                    'source_row_id': None,
                    'contribution_value': None,
                    'can_view_source': False,
                    'href': None,
                })
        return Response({'derived_kind': derived_kind, 'derived_row': str(derived_row), 'rows': rows})

    @extend_schema(summary='Material reconciliation hints', tags=['Daily Reports'])
    @action(detail=True, methods=['get'], url_path='materials-reconciliation')
    def materials_reconciliation(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(reconcile_report_materials(instance))

    @extend_schema(summary='Materials summary and details', tags=['Daily Reports'])
    @action(detail=True, methods=['get'], url_path='materials-details')
    def materials_details(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DailyReportDetailSerializer(instance, context={'request': request})
        return Response(serializer.get_materials_summary(instance))


class DailyReportCorrectionCancelView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_reports'

    def get_project_id(self):
        return self.kwargs['project_pk']

    @extend_schema(summary='Cancel open correction request', tags=['Daily Reports'])
    def post(self, request, *args, **kwargs):
        correction = DailyReportCorrectionRequest.objects.filter(
            id=self.kwargs['correction_id'],
            project_id=self.get_project_id(),
            is_deleted=False,
        ).first()
        if correction is None:
            raise NotFound('درخواست اصلاح یافت نشد')
        correction = correction_service.cancel_correction(
            correction=correction,
            user=request.user,
            request=request,
        )
        return Response(DailyReportCorrectionRequestSerializer(correction).data)


# ---------------------------------------------------------------------------
# Child row viewsets
# ---------------------------------------------------------------------------


class DailyReportChildViewSet(viewsets.ModelViewSet):
    lookup_url_kwarg = 'pk'
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    supports_batch = False
    upsert_keys: tuple[str, ...] = ()

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    def get_project_id(self):
        return self.kwargs['project_pk']

    def get_report(self):
        if not hasattr(self, '_report'):
            self._report = DailyReport.all_objects.filter(
                id=self.kwargs['report_pk'], project_id=self.get_project_id(),
            ).first()
            if self._report is None:
                raise ValidationError('گزارش روزانه یافت نشد')
        return self._report

    def _assert_editable(self):
        from field_reports.services.derived_lock import assert_child_row_mutable
        report = self.get_report()
        return assert_child_row_mutable(report, request=self.request)

    def get_queryset(self):
        return self.queryset.filter(
            report_id=self.kwargs['report_pk'],
            report__project_id=self.get_project_id(),
            is_deleted=False,
        )

    def create(self, request, *args, **kwargs):
        self._assert_editable()
        report = self.get_report()
        data = request.data
        if isinstance(data, list):
            if not self.supports_batch:
                raise ValidationError('این نقطه ورودی از ثبت گروهی پشتیبانی نمی‌کند')
            return self._batch_upsert(report, data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(report=report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _batch_upsert(self, report, rows):
        results = []
        with transaction.atomic():
            for row in rows:
                lookup = {key: row.get(key) for key in self.upsert_keys}
                existing = self.queryset.filter(
                    report=report, is_deleted=False, **lookup,
                ).first()
                serializer = self.get_serializer(existing, data=row, partial=existing is not None)
                serializer.is_valid(raise_exception=True)
                serializer.save(report=report)
                results.append(serializer.data)
        return Response(results, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        from field_reports.services.derived_lock import assert_child_row_mutable
        assert_child_row_mutable(self.get_report(), serializer.instance, request=self.request)
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        from field_reports.services.derived_lock import assert_child_row_mutable
        assert_child_row_mutable(self.get_report(), instance, request=request)
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DailyReportActivityViewSet(DailyReportChildViewSet):
    queryset = DailyReportActivity.objects.all()
    serializer_class = DailyReportActivitySerializer


class DailyReportLaborViewSet(DailyReportChildViewSet):
    queryset = DailyReportLabor.objects.all()
    serializer_class = DailyReportLaborSerializer
    supports_batch = True
    upsert_keys = ('labor_category', 'job_title')


class DailyReportEquipmentViewSet(DailyReportChildViewSet):
    queryset = DailyReportEquipment.objects.all()
    serializer_class = DailyReportEquipmentSerializer


class DailyReportMaterialViewSet(DailyReportChildViewSet):
    queryset = DailyReportMaterial.objects.all()
    serializer_class = DailyReportMaterialSerializer


class DailyReportConcreteLogViewSet(DailyReportChildViewSet):
    queryset = DailyReportConcreteLog.objects.all()
    serializer_class = DailyReportConcreteLogSerializer


class DailyReportLaborCampViewSet(DailyReportChildViewSet):
    queryset = DailyReportLaborCamp.objects.all()
    serializer_class = DailyReportLaborCampSerializer


class DailyReportIncidentViewSet(DailyReportChildViewSet):
    queryset = DailyReportIncident.objects.all()
    serializer_class = DailyReportIncidentSerializer


@extend_schema_view(get=extend_schema(summary='List fixed labor job titles', tags=['Daily Reports']))
class LaborJobTitleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    serializer_class = LaborJobTitleSerializer
    queryset = LaborJobTitle.objects.all()
    pagination_class = None
    required_permission = 'view_reports'

    def get_permissions(self):
        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    def get_queryset(self):
        qs = LaborJobTitle.objects.all()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        return qs.order_by('category', 'display_order')
