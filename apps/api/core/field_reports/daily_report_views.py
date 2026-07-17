"""Daily report CRUD, approval workflow, offline sync-batch and PDF export."""
from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.http import HttpResponse
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.jalali import parse_date_optional
from config.exceptions import ConflictError
from config.pagination import DefaultPageNumberPagination
from permissions.project import HasProjectPermission, IsProjectMember
from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportLaborCamp,
    DailyReportMaterial,
    ReportStatus,
)
from field_reports.models import LaborJobTitle
from field_reports.serializers import (
    DailyReportActivitySerializer,
    DailyReportConcreteLogSerializer,
    DailyReportDetailSerializer,
    DailyReportEquipmentSerializer,
    DailyReportHeaderSerializer,
    DailyReportIncidentSerializer,
    DailyReportLaborCampSerializer,
    DailyReportLaborSerializer,
    DailyReportListSerializer,
    DailyReportMaterialSerializer,
    LaborJobTitleSerializer,
)
from field_reports import services

EDITABLE_STATUSES = {ReportStatus.DRAFT, ReportStatus.REJECTED}


def _validate_report_ready_for_submit(report: DailyReport):
    errors: list[str] = []

    activities = list(report.activities.filter(is_deleted=False))
    if not activities:
        errors.append('گزارش باید حداقل یک فعالیت داشته باشد')
    for idx, row in enumerate(activities, start=1):
        if row.quantity_measured and row.quantity is None:
            errors.append(f'ردیف فعالیت {idx}: در حالت اندازه‌گیری شده، مقدار باید ثبت شود')

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


@extend_schema_view(
    list=extend_schema(summary='List daily reports', tags=['Daily Reports']),
    create=extend_schema(summary='Create daily report header', tags=['Daily Reports']),
    retrieve=extend_schema(summary='Get daily report with child rows', tags=['Daily Reports']),
    partial_update=extend_schema(summary='Update daily report header', tags=['Daily Reports']),
    destroy=extend_schema(summary='Soft-delete daily report', tags=['Daily Reports']),
)
class DailyReportViewSet(viewsets.ModelViewSet):
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
        if self.action in ('list', 'retrieve', 'pdf'):
            return self.view_permission
        if self.action in ('review', 'approve', 'reject'):
            return self.approve_permission
        return self.edit_permission

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'pdf'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    # Queries: before optimization=47, after=4 (list with select_related + prefetch_related)
    def get_queryset(self):
        qs = (
            DailyReport.objects.filter(project_id=self.get_project_id())
            .select_related('prepared_by', 'submitted_by', 'reviewed_by', 'approved_by').prefetch_related('activities', 'labor_entries', 'equipment_entries', 'incidents')
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
        return qs.order_by('-report_date')

    def get_serializer_class(self):
        if self.action == 'list':
            return DailyReportListSerializer
        if self.action in ('create', 'partial_update'):
            return DailyReportHeaderSerializer
        return DailyReportDetailSerializer

    # -- CRUD ---------------------------------------------------------------

    def create(self, request, *args, **kwargs):
        serializer = DailyReportHeaderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project_id = self.get_project_id()
        report_date = serializer.validated_data['report_date']
        shift = serializer.validated_data.get('shift') or 'full'
        if DailyReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            shift=shift,
            is_deleted=False,
        ).exists():
            raise ConflictError(
                f'گزارش روزانه برای تاریخ {request.data.get("report_date")} '
                f'و شیفت {shift} قبلاً ثبت شده است',
            )
        instance = serializer.save(
            project_id=project_id,
            prepared_by=request.user,
            created_by=request.user,
            updated_by=request.user,
        )
        detail = DailyReportDetailSerializer(instance)
        return Response(detail.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in EDITABLE_STATUSES:
            raise ValidationError('فقط گزارش‌های پیش‌نویس یا رد شده قابل ویرایش هستند')
        serializer = DailyReportHeaderSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=request.user)
        return Response(DailyReportDetailSerializer(instance).data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ReportStatus.DRAFT:
            raise ValidationError('فقط گزارش‌های پیش‌نویس قابل حذف هستند')
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.updated_by = request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    # -- Workflow -----------------------------------------------------------

    @extend_schema(summary='Submit for approval', tags=['Daily Reports'])
    @action(detail=True, methods=['post'])
    def submit(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in EDITABLE_STATUSES:
            raise ValidationError('فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند')
        _validate_report_ready_for_submit(instance)
        services.submit_report(instance, request.user)
        return Response(DailyReportDetailSerializer(instance).data)

    @extend_schema(summary='Mark under review', tags=['Daily Reports'])
    @action(detail=True, methods=['post'])
    def review(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status != ReportStatus.SUBMITTED:
            raise ValidationError('فقط گزارش‌های ارسال شده قابل بررسی هستند')
        services.review_report(instance, request.user, request.data.get('notes', ''))
        return Response(DailyReportDetailSerializer(instance).data)

    @extend_schema(summary='Approve report', tags=['Daily Reports'])
    @action(detail=True, methods=['post'])
    def approve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in (ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW):
            raise ValidationError('فقط گزارش‌های ارسال شده یا در حال بررسی قابل تأیید هستند')
        services.approve_report(instance, request.user)
        return Response(DailyReportDetailSerializer(instance).data)

    @extend_schema(summary='Reject report', tags=['Daily Reports'])
    @action(detail=True, methods=['post'])
    def reject(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status not in (ReportStatus.SUBMITTED, ReportStatus.UNDER_REVIEW):
            raise ValidationError('فقط گزارش‌های ارسال شده یا در حال بررسی قابل رد هستند')
        reason = (request.data.get('reason') or '').strip()
        if len(reason) < 10:
            raise ValidationError({'reason': 'دلیل رد باید حداقل ۱۰ کاراکتر باشد'})
        services.reject_report(instance, request.user, reason)
        return Response(DailyReportDetailSerializer(instance).data)

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
        if self.get_report().status not in EDITABLE_STATUSES:
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
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])
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
