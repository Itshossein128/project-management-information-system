"""
Excel import/export and XLSX report endpoints for department activity records.
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Max, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from business_meta.models import Project
from business_meta.permissions import CanViewBusinessAssignments, IsHrOrAdminOrReadOnly, IsVisitorReadOnly
from common.jalali import parse_jalali_or_gregorian
from common.validators import validate_xlsx_upload
from permissions.project import HasProjectPermission, IsProjectMember

from .department_activity_io import (
    department_display_label,
    export_activities_to_xlsx,
    generate_activity_report_pdf,
    generate_daily_activity_report_xlsx,
    generate_weekly_activity_report_xlsx,
    import_activities_from_xlsx,
    normalize_persian_numbers,
)
from .department_activity_services import (
    get_department_activity_queryset,
    normalize_department,
    require_valid_department,
)
from .models import DepartmentActivityRecord


def to_persian_digits(val: Any) -> str:
    s = str(val)
    for e, p in zip('0123456789', '۰۱۲۳۴۵۶۷۸۹'):
        s = s.replace(e, p)
    return s


def _parse_query_date(raw_date: str | None) -> date | None:
    if not raw_date:
        return None
    cleaned = normalize_persian_numbers(raw_date).strip()
    try:
        return parse_jalali_or_gregorian(cleaned)
    except Exception:
        pass
    parsed = parse_date(cleaned)
    if parsed:
        return parsed
    raise ValueError('فرمت تاریخ نامعتبر است (الگوی معتبر: YYYY-MM-DD)')


class _DepartmentActivityDataBase(APIView):
    permission_classes = [
        IsAuthenticated,
        IsProjectMember,
        HasProjectPermission,
        CanViewBusinessAssignments,
        IsVisitorReadOnly,
        IsHrOrAdminOrReadOnly,
    ]
    required_permission = 'view_reports'

    def _get_business(self, project_pk: int) -> Project | None:
        try:
            return Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return None

    def _require_department(self, request) -> str | Response:
        department = require_valid_department(request.query_params.get('department'))
        if not department:
            return Response(
                {
                    'error': (
                        'Query parameter `department` is required and must be a valid department slug.'
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return department


class DepartmentActivityExportView(_DepartmentActivityDataBase):
    @extend_schema(
        summary='Export department activity records to Excel',
        description=(
            'Download activity rows as .xlsx with RTL alignment and Persian headers. '
            'Requires `department`. Supports the same optional filters as the list endpoint.'
        ),
        parameters=[
            OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True),
            OpenApiParameter(name='date_from', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='date_to', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='location', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='activity_description', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='contractor', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='contractor_ref', type=OpenApiTypes.UUID, required=False),
            OpenApiParameter(name='unit', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='material_type', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='consumption_location', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='supplier', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='ordering', type=OpenApiTypes.STR, required=False),
        ],
        tags=['Project activity records'],
    )
    def get(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        department = self._require_department(request)
        if isinstance(department, Response):
            return department

        qs = get_department_activity_queryset(project_pk, request.query_params)
        xlsx_bytes = export_activities_to_xlsx(list(qs), department=department, persian_headers=True)
        filename = f'{department}_activity_export.xlsx'
        response = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DepartmentActivityImportView(_DepartmentActivityDataBase):
    parser_classes = [MultiPartParser, FormParser]
    required_permission = 'edit_reports'

    @extend_schema(
        summary='Import department activity records from Excel',
        description=(
            'Upload .xlsx with activity columns. Requires `department` query parameter and `edit_reports` permission. '
            'Atomic execution: if any row fails validation, entire batch is rolled back.'
        ),
        parameters=[OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True)],
        tags=['Project activity records'],
    )
    def post(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        department = self._require_department(request)
        if isinstance(department, Response):
            return department

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_xlsx_upload(file_obj)
        except ValidationError as exc:
            return Response({'error': exc.detail}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_bytes = file_obj.read()
        except OSError as exc:
            return Response(
                {'error': f'Failed to read file: {exc}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created, errors = import_activities_from_xlsx(business, department, file_bytes)
        if errors:
            first_err = errors[0]
            row_num = first_err.get('row')
            err_dict = first_err.get('errors', {})
            err_code = first_err.get('code')
            if not err_code:
                # Check inside any error entry for code
                for e in errors:
                    if e.get('code'):
                        err_code = e.get('code')
                        break
            if not err_code:
                err_code = 'validation_error'

            first_field, first_msg = (
                next(iter(err_dict.items())) if err_dict else ('', 'خطای اعتبارسنجی داده‌ها')
            )
            if row_num:
                detail = f'خطا در سطر {to_persian_digits(row_num)}: {first_msg}'
            else:
                detail = str(first_msg)
            return Response(
                {
                    'error': {
                        'code': err_code,
                        'message': detail,
                        'details': errors,
                    },
                    'detail': detail,
                    'created': 0,
                    'errors': errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            'created': created,
            'detail': f'تعداد {created} رکورد فعالیت با موفقیت ثبت شد.',
            'errors': [],
        })


class DepartmentActivityDailyReportView(_DepartmentActivityDataBase):
    @extend_schema(
        summary='Download daily department activity Excel workbook (.xlsx)',
        description=(
            'Single-day Excel report with official project header, RTL layout, '
            'and live dynamic =SUM() total formula.'
        ),
        parameters=[
            OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True),
            OpenApiParameter(name='date', type=OpenApiTypes.DATE, required=False),
        ],
        tags=['Project activity records'],
    )
    def get(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        department = self._require_department(request)
        if isinstance(department, Response):
            return department

        date_param = request.query_params.get('date')
        try:
            target_date = _parse_query_date(date_param)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not target_date:
            target_date = timezone.localdate() - timedelta(days=1)

        dept_norm = normalize_department(department) or department
        dept_filter = ['buildings', 'civil'] if dept_norm in ('civil', 'buildings') else [dept_norm]

        qs = DepartmentActivityRecord.objects.filter(
            project_id=project_pk,
            department__in=dept_filter,
            date=target_date,
        ).order_by('-created_at')

        xlsx_bytes = generate_daily_activity_report_xlsx(
            business=business,
            department=department,
            report_date=target_date,
            records=list(qs),
        )
        filename = f'{department}_daily_report_{target_date}.xlsx'
        response = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DepartmentActivityWeeklyReportView(_DepartmentActivityDataBase):
    @extend_schema(
        summary='Download weekly department activity multi-sheet Excel workbook (.xlsx)',
        description=(
            'Eight-sheet Excel report containing 7 daily tabs (Saturday to Friday) '
            'and 1 Summary sheet with live dynamic =SUM() calculation formulas.'
        ),
        parameters=[
            OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True),
            OpenApiParameter(name='week_start', type=OpenApiTypes.DATE, required=False),
        ],
        tags=['Project activity records'],
    )
    def get(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        department = self._require_department(request)
        if isinstance(department, Response):
            return department

        week_start_param = request.query_params.get('week_start')
        try:
            week_start = _parse_query_date(week_start_param)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not week_start:
            today = timezone.localdate()
            # Saturday is weekday 5 in Python (Monday=0 ... Sunday=6)
            days_since_saturday = (today.weekday() - 5) % 7
            week_start = today - timedelta(days=days_since_saturday)

        week_end = week_start + timedelta(days=6)
        dept_norm = normalize_department(department) or department
        dept_filter = ['buildings', 'civil'] if dept_norm in ('civil', 'buildings') else [dept_norm]

        qs = DepartmentActivityRecord.objects.filter(
            project_id=project_pk,
            department__in=dept_filter,
            date__gte=week_start,
            date__lte=week_end,
        ).order_by('date', '-created_at')

        opening_balances = None
        if dept_norm == 'warehouse':
            prior_agg = (
                DepartmentActivityRecord.objects.filter(
                    project_id=project_pk,
                    department__in=dept_filter,
                    date__lt=week_start,
                )
                .values('material_type', 'unit')
                .annotate(
                    total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
                    total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
                )
            )
            opening_balances = {
                ((item['material_type'] or '').strip(), (item['unit'] or '').strip()): float(item['total_in'] - item['total_out'])
                for item in prior_agg
            }

        xlsx_bytes = generate_weekly_activity_report_xlsx(
            business=business,
            department=department,
            week_start=week_start,
            records=list(qs),
            opening_balances=opening_balances,
        )
        filename = f'{department}_weekly_report_{week_start}_{week_end}.xlsx'
        response = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class WarehouseBalanceView(_DepartmentActivityDataBase):
    @extend_schema(
        summary='Query warehouse material balance summary',
        description=(
            'Returns stock balance aggregated by (material_type, unit) up to the specified date. '
            'Requires `view_reports` permission.'
        ),
        parameters=[
            OpenApiParameter(name='as_of_date', type=OpenApiTypes.DATE, required=False, description='Cutoff date (defaults to today)'),
            OpenApiParameter(name='search', type=OpenApiTypes.STR, required=False, description='Case-insensitive search on material_type'),
        ],
        tags=['Project warehouse records'],
    )
    def get(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        raw_as_of = request.query_params.get('as_of_date')
        try:
            as_of_date = _parse_query_date(raw_as_of)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if not as_of_date:
            as_of_date = timezone.localdate()

        search_term = (request.query_params.get('search') or '').strip()

        qs = DepartmentActivityRecord.objects.filter(
            project_id=project_pk,
            department='warehouse',
            date__lte=as_of_date,
        )
        if search_term:
            qs = qs.filter(material_type__icontains=search_term)

        aggregates = (
            qs.values('material_type', 'unit')
            .annotate(
                total_in=Coalesce(Sum('quantity_in'), Value(Decimal('0'))),
                total_out=Coalesce(Sum('quantity_out'), Value(Decimal('0'))),
                last_movement_date=Max('date'),
            )
            .order_by('material_type', 'unit')
        )

        results = []
        for item in aggregates:
            tot_in = float(item['total_in'])
            tot_out = float(item['total_out'])
            results.append({
                'material_type': item['material_type'],
                'unit': item['unit'],
                'total_in': tot_in,
                'total_out': tot_out,
                'current_balance': round(tot_in - tot_out, 3),
                'last_movement_date': item['last_movement_date'].isoformat() if item['last_movement_date'] else None,
            })
        return Response(results, status=status.HTTP_200_OK)
