"""Standalone form APIs (labor camp, equipment log, manpower)."""

from collections import defaultdict
from datetime import datetime, timedelta

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.jalali import parse_jalali_or_gregorian
from common.serializers import JalaliDateField
from common.viewsets import ProjectScopedViewSet
from config.pagination import DefaultPageNumberPagination
from field_reports.models import (
    DailyReportLabor,
    EquipmentLog,
    LaborCampReport,
    LaborCategory,
    LaborJobTitle,
)
from rest_framework import serializers


class LaborCampSerializer(serializers.ModelSerializer):
    report_date = JalaliDateField()
    empty_capacity = serializers.SerializerMethodField()
    warning = serializers.SerializerMethodField()

    class Meta:
        model = LaborCampReport
        fields = [
            'id',
            'report_date',
            'connex_number',
            'subcontractor_name',
            'total_residents',
            'present_count',
            'on_leave_count',
            'capacity',
            'empty_capacity',
            'warning',
        ]
        read_only_fields = ['id']

    def get_empty_capacity(self, obj):
        return obj.capacity - obj.total_residents

    def get_warning(self, obj):
        if obj.present_count + obj.on_leave_count != obj.total_residents:
            return 'جمع حاضر و مرخصی با تعداد مستقر مطابقت ندارد'
        return None


@extend_schema_view(
    list=extend_schema(summary='List labor camp reports', tags=['Labor camp']),
    create=extend_schema(summary='Create labor camp report(s)', tags=['Labor camp']),
    partial_update=extend_schema(summary='Update labor camp report', tags=['Labor camp']),
    destroy=extend_schema(summary='Delete labor camp report', tags=['Labor camp']),
)
class LaborCampReportViewSet(ProjectScopedViewSet):
    queryset = LaborCampReport.objects.all()
    serializer_class = LaborCampSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def get_queryset(self):
        qs = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(report_date__gte=parse_jalali_or_gregorian(date_from))
        if date_to:
            qs = qs.filter(report_date__lte=parse_jalali_or_gregorian(date_to))
        return qs.order_by('-report_date')

    def list(self, request, *args, **kwargs):
        if request.query_params.get('grouped') == 'true':
            qs = self.filter_queryset(self.get_queryset())
            grouped = defaultdict(list)
            for row in qs:
                key = row.report_date.isoformat()
                ser = self.get_serializer(row)
                grouped[key].append(ser.data)
            result = []
            for date_key, records in grouped.items():
                totals = {
                    'total_residents': sum(r['total_residents'] for r in records),
                    'present': sum(r['present_count'] for r in records),
                    'on_leave': sum(r['on_leave_count'] for r in records),
                    'capacity': sum(r['capacity'] for r in records),
                    'empty': sum(r['empty_capacity'] for r in records),
                }
                result.append({'date': date_key, 'records': records, 'totals': totals})
            return Response(result)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        payload = request.data
        items = payload if isinstance(payload, list) else [payload]
        created = []
        warnings = []
        for item in items:
            ser = self.get_serializer(data=item)
            ser.is_valid(raise_exception=True)
            obj = ser.save(
                project_id=self.get_project_id(),
                created_by=request.user,
                updated_by=request.user,
            )
            data = self.get_serializer(obj).data
            if data.get('warning'):
                warnings.append(data['warning'])
            created.append(data)
        body = created[0] if len(created) == 1 and not isinstance(payload, list) else created
        resp = Response(body, status=status.HTTP_201_CREATED)
        if warnings:
            resp.data = body if isinstance(body, dict) else {'results': body, 'warning': warnings[0]}
        return resp


class EquipmentLogSerializer(serializers.ModelSerializer):
    log_date = JalaliDateField()
    warning = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentLog
        fields = [
            'id',
            'equipment',
            'log_date',
            'equipment_name',
            'equipment_ref',
            'shift',
            'status',
            'ownership_type',
            'work_start',
            'work_end',
            'repair_hours',
            'idle_hours',
            'idle_reason',
            'productive_hours',
            'hourly_rate',
            'fuel_cost',
            'activity_ref',
            'notes',
            'warning',
        ]
        read_only_fields = ['id']

    def get_warning(self, obj):
        if obj.work_start and obj.work_end and obj.productive_hours is not None:
            start = datetime.combine(obj.log_date, obj.work_start)
            end = datetime.combine(obj.log_date, obj.work_end)
            if end < start:
                end += timedelta(days=1)
            expected = (end - start).total_seconds() / 3600 - float(obj.repair_hours or 0)
            if abs(float(obj.productive_hours) - expected) > 0.5:
                return 'کارکرد مفید با بازه زمانی و ساعات تعمیر مطابقت ندارد'
        return None


@extend_schema_view(
    list=extend_schema(summary='List equipment logs', tags=['Equipment']),
    create=extend_schema(summary='Create equipment log', tags=['Equipment']),
    partial_update=extend_schema(summary='Update equipment log', tags=['Equipment']),
    destroy=extend_schema(summary='Delete equipment log', tags=['Equipment']),
)
class EquipmentLogViewSet(ProjectScopedViewSet):
    queryset = EquipmentLog.objects.select_related('activity_ref').all()
    serializer_class = EquipmentLogSerializer
    pagination_class = DefaultPageNumberPagination
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('date'):
            qs = qs.filter(log_date=parse_jalali_or_gregorian(p['date']))
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        if p.get('ownership_type'):
            qs = qs.filter(ownership_type=p['ownership_type'])
        if p.get('equipment_name'):
            qs = qs.filter(equipment_name__icontains=p['equipment_name'])
        return qs.order_by('-log_date')


class EquipmentLogSummaryView(APIView):
    view_permission = 'view_reports'

    def get_permissions(self):
        from permissions.project import HasProjectPermission, IsProjectMember
        from rest_framework.permissions import IsAuthenticated

        return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]

    @property
    def required_permission(self):
        return self.view_permission

    @extend_schema(summary='Equipment log summary by date', tags=['Equipment'])
    def get(self, request, project_pk):
        from django.db.models import Count

        qs = EquipmentLog.objects.filter(project_id=project_pk, is_deleted=False)
        date = request.query_params.get('date')
        if date:
            qs = qs.filter(log_date=parse_jalali_or_gregorian(date))
        rows = (
            qs.values('log_date', 'equipment_name', 'status')
            .annotate(count=Count('id'))
            .order_by('-log_date', 'equipment_name')
        )
        grouped = defaultdict(lambda: defaultdict(lambda: {'total_units': 0, 'active': 0, 'standby': 0, 'broken': 0, 'under_repair': 0}))
        for row in rows:
            d = row['log_date'].isoformat()
            name = row['equipment_name']
            grouped[d][name]['total_units'] += row['count']
            grouped[d][name][row['status']] = grouped[d][name].get(row['status'], 0) + row['count']
        result = []
        for d, equipments in grouped.items():
            for name, stats in equipments.items():
                result.append({'date': d, 'equipment_name': name, **stats})
        return Response(result)


class StandaloneManpowerSerializer(serializers.ModelSerializer):
    report_date = JalaliDateField()

    class Meta:
        model = DailyReportLabor
        fields = [
            'id',
            'report_date',
            'labor_category',
            'job_title',
            'shift_1_count',
            'shift_2_count',
            'shift_3_count',
            'total_count',
            'work_hours',
            'overtime_hours',
        ]
        read_only_fields = ['id', 'total_count']


@extend_schema_view(
    list=extend_schema(summary='List standalone manpower', tags=['Manpower']),
    create=extend_schema(summary='Batch upsert manpower', tags=['Manpower']),
    partial_update=extend_schema(summary='Update manpower row', tags=['Manpower']),
    destroy=extend_schema(summary='Delete manpower row', tags=['Manpower']),
)
class StandaloneManpowerViewSet(ProjectScopedViewSet):
    queryset = DailyReportLabor.objects.filter(report__isnull=True)
    serializer_class = StandaloneManpowerSerializer
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def get_queryset(self):
        qs = DailyReportLabor.objects.filter(
            project_id=self.get_project_id(),
            report__isnull=True,
            is_deleted=False,
        )
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(report_date=parse_jalali_or_gregorian(date))
        return qs.order_by('labor_category', 'job_title')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        project_id = self.get_project_id()
        payload = request.data
        items = payload if isinstance(payload, list) else [payload]
        saved = []
        for item in items:
            ser = self.get_serializer(data=item)
            ser.is_valid(raise_exception=True)
            data = ser.validated_data
            report_date = data['report_date']
            obj, _ = DailyReportLabor.objects.update_or_create(
                project_id=project_id,
                report_date=report_date,
                report=None,
                labor_category=data['labor_category'],
                job_title=data['job_title'],
                defaults={
                    'shift_1_count': data.get('shift_1_count', 0),
                    'shift_2_count': data.get('shift_2_count', 0),
                    'shift_3_count': data.get('shift_3_count', 0),
                    'is_deleted': False,
                },
            )
            saved.append(self.get_serializer(obj).data)
        body = saved[0] if len(saved) == 1 and not isinstance(payload, list) else {'count': len(saved), 'results': saved}
        return Response(body, status=status.HTTP_201_CREATED)
