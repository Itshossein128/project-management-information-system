"""
Excel import/export and PDF report endpoints for department activity records.
"""
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from business_meta.models import Project
from common.validators import validate_xlsx_upload
from business_meta.permissions import CanViewBusinessAssignments, IsHrOrAdminOrReadOnly, IsVisitorReadOnly

from .department_activity_io import (
    department_display_label,
    export_activities_to_xlsx,
    generate_activity_report_pdf,
    import_activities_from_xlsx,
)
from .department_activity_services import (
    get_department_activity_queryset,
    get_report_date_range,
    require_valid_department,
)
from .models import DepartmentActivityRecord


class _DepartmentActivityDataBase(APIView):
    permission_classes = [
        IsAuthenticated,
        CanViewBusinessAssignments,
        IsVisitorReadOnly,
        IsHrOrAdminOrReadOnly,
    ]

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
            'Download activity rows as .xlsx. Requires `department`. '
            'Supports the same optional filters as the list endpoint.'
        ),
        parameters=[
            OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True),
            OpenApiParameter(name='date_from', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='date_to', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='location', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='activity_description', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='contractor', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='unit', type=OpenApiTypes.STR, required=False),
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
        xlsx_bytes = export_activities_to_xlsx(list(qs))
        filename = f'{department}_activity_export.xlsx'
        response = HttpResponse(
            xlsx_bytes,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response


class DepartmentActivityImportView(_DepartmentActivityDataBase):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary='Import department activity records from Excel',
        description='Upload .xlsx with activity columns. Requires `department` query parameter.',
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
        return Response({'created': created, 'errors': errors})


class _DepartmentActivityReportView(_DepartmentActivityDataBase):
    period: str = 'daily'
    period_label: str = 'Daily report'

    @extend_schema(tags=['Project activity records'])
    def get(self, request, project_pk: int):
        business = self._get_business(project_pk)
        if business is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        department = self._require_department(request)
        if isinstance(department, Response):
            return department

        date_from, date_to = get_report_date_range(self.period)
        qs = DepartmentActivityRecord.objects.filter(
            project_id=project_pk,
            department=department,
            date__gte=date_from,
            date__lte=date_to,
        ).order_by('date', '-created_at')
        records = list(qs)

        pdf_bytes = generate_activity_report_pdf(
            business=business,
            department=department,
            department_label=department_display_label(department),
            period_label=self.period_label,
            date_from=date_from,
            date_to=date_to,
            records=records,
        )
        filename = f'{department}_{self.period}_report_{date_from}_{date_to}.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        return response


class DepartmentActivityDailyReportView(_DepartmentActivityReportView):
    period = 'daily'
    period_label = 'Daily report'

    @extend_schema(
        summary='Download daily department activity PDF',
        description='PDF for the previous calendar day for the given department.',
        parameters=[OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True)],
        tags=['Project activity records'],
    )
    def get(self, request, project_pk: int):
        return super().get(request, project_pk)


class DepartmentActivityWeeklyReportView(_DepartmentActivityReportView):
    period = 'weekly'
    period_label = 'Weekly report'

    @extend_schema(
        summary='Download weekly department activity PDF',
        description='PDF for the rolling last 7 days (including today) for the given department.',
        parameters=[OpenApiParameter(name='department', type=OpenApiTypes.STR, required=True)],
        tags=['Project activity records'],
    )
    def get(self, request, project_pk: int):
        return super().get(request, project_pk)
