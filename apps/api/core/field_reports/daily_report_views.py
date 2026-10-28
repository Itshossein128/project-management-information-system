"""Daily report CRUD, approval workflow, offline sync-batch and PDF export."""
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.mixins import WorkflowViewSetMixin
from common.jalali import parse_date_optional
from config.pagination import DefaultPageNumberPagination
from permissions.project import HasProjectPermission, IsProjectMember
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
from field_reports.services import correction_service
from field_reports.services.lifecycle_errors import lifecycle_error_detail, get_lifecycle_msg
from field_reports.services.daily_report_aggregation import (
    build_aggregation_meta,
    ensure_daily_report_summary,
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
            'list', 'retrieve', 'pdf', 'excel', 'versions', 'materials_reconciliation',
            'materials_details', 'provenance',
        ):
            return self.view_permission
        if self.action == 'correction_requests' and self.request.method.upper() == 'GET':
            return self.view_permission
        if self.action in ('review', 'approve', 'reject'):
            return self.approve_permission
        return self.edit_permission

    def get_permissions(self):
        if self.action in (
            'list', 'retrieve', 'pdf', 'versions', 'materials_reconciliation',
            'materials_details', 'provenance', 'by_date',
        ) or (
            self.action == 'correction_requests' and self.request.method.upper() == 'GET'
        ):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    # Queries: before optimization=47, after=4 (list with select_related + prefetch_related)
    def get_queryset(self):
        qs = (
            DailyReport.objects.filter(project_id=self.get_project_id(), is_deleted=False)
            .select_related('prepared_by', 'submitted_by', 'reviewed_by', 'approved_by')
            .prefetch_related('activities', 'labor_entries', 'equipment_entries', 'machinery_rows', 'incidents')
        )
        params = self.request.query_params
        date_from = parse_date_optional(params.get('date_from'))
        date_to = parse_date_optional(params.get('date_to'))
        if date_from:
            qs = qs.filter(report_date__gte=date_from)
        if date_to:
            qs = qs.filter(report_date__lte=date_to)
        status_filter = params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        prepared_by = params.get('prepared_by')
        if prepared_by:
            qs = qs.filter(prepared_by_id=prepared_by)
        lineage_id = params.get('lineage_id')
        if lineage_id:
            qs = qs.filter(lineage_id=lineage_id)
        is_current = params.get('is_current')
        if is_current is None and self.action == 'list':
            qs = qs.filter(is_current=True)
        elif is_current is not None:
            qs = qs.filter(is_current=is_current.lower() in ('1', 'true', 'yes'))
        return qs.order_by('-report_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyReportListSerializer
        if self.action in ('create', 'partial_update'):
            return DailyReportHeaderSerializer
        return DailyReportDetailSerializer

    # -- CRUD ---------------------------------------------------------------

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

        project_id = self.get_project_id()
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
        if not member_has_codename(request.user, self.get_project_id(), 'edit_reports'):
            raise PermissionDenied('Current project edit permission is required')
        if instance.is_auto_summary and services._derived_sections_in_payload(request.data):
            raise ValidationError({'detail': DERIVED_READONLY_MSG, 'code': 'derived_readonly'})
        if instance.status == ReportStatus.APPROVED:
            raise ValidationError({'detail': 'گزارش قفل‌شده است', 'code': 'report_locked'})
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
        pdf_bytes, filename = generate_daily_report_pdf(instance)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response

    @extend_schema(summary='Export report as Shiraz FILE 4 Excel', tags=['Daily Reports'])
    @action(detail=True, methods=['get'])
    def excel(self, request, *args, **kwargs):
        from field_reports.shiraz_file4_excel import ShirazFile4ExcelBuilder

        instance = self.get_object()
        builder = ShirazFile4ExcelBuilder(instance)
        excel_bytes, filename = builder.build()

        response = HttpResponse(
            excel_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # -- Versions / correction / reconciliation -----------------------------

    @extend_schema(summary='List report versions in lineage', tags=['Daily Reports'])
    @action(detail=True, methods=['get'], url_path='versions')
    def versions(self, request, *args, **kwargs):
        instance = self.get_object()
        qs = correction_service.list_versions(instance)
        return Response(DailyReportVersionSerializer(qs, many=True).data)

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

        instance = self.get_object()
        user = request.user
        can_view = False
        if user and user.is_authenticated:
            if user.is_superuser or user.groups.filter(name='admin').exists():
                can_view = True
            else:
                from permissions.project import member_has_codename
                can_view = member_has_codename(user, instance.project_id, 'view_reports')

        sources = DailyReportDerivedSource.objects.filter(
            daily_report=instance,
            derived_kind=derived_kind,
            derived_row_id=str(derived_row),
        ).order_by('ordinal', 'id')
        if not sources.exists():
            return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)
        rows = []
        for source in sources:
            if can_view:
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
            self._report = DailyReport.objects.filter(
                id=self.kwargs['report_pk'],
                project_id=self.get_project_id(),
                is_deleted=False,
            ).first()
            if self._report is None:
                raise ValidationError('گزارش روزانه یافت نشد')
        return self._report

    def _assert_editable(self):
        report = self.get_report()
        if report.is_auto_summary:
            raise ValidationError({'detail': DERIVED_READONLY_MSG, 'code': 'derived_collection_read_only'})
        if report.status == ReportStatus.APPROVED:
            raise ValidationError({'detail': 'گزارش قفل‌شده است', 'code': 'report_locked'})
        if report.status not in EDITABLE_STATUSES:
            raise ValidationError('فقط ردیف‌های گزارش‌های پیش‌نویس یا رد شده قابل تغییر هستند')

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
        self._assert_editable()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        self._assert_editable()
        instance = self.get_object()
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
