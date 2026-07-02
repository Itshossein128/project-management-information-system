"""
Data API: CRUD for dynamic table rows (Django DB / SQLite). Enforce access and validate payload against table schema.
Excel export/import for table rows.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from projects.mixins import PROJECT_MEMBER_PERMISSIONS
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Project, TableDefinition, DynamicTableRow
from .services import validate_row_data
from .excel_io import export_table_to_xlsx, import_rows_from_xlsx


def get_project_and_table(project_pk, table_slug):
    """Return (Project, TableDefinition) or (None, None) if not found."""
    try:
        business = Project.objects.get(pk=project_pk)
        table = TableDefinition.objects.get(project=business, slug=table_slug)
        return business, table
    except (Project.DoesNotExist, TableDefinition.DoesNotExist):
        return None, None


def serialize_row(row):
    """Build API response dict: id, field values, created_at, updated_at."""
    out = {'id': row.pk, **row.data}
    out['created_at'] = row.created_at.isoformat().replace('+00:00', 'Z') if row.created_at else None
    out['updated_at'] = row.updated_at.isoformat().replace('+00:00', 'Z') if row.updated_at else None
    return out


def parse_row_id(row_id):
    """Return integer PK or None if invalid."""
    try:
        return int(row_id)
    except (TypeError, ValueError):
        return None


class DynamicRowsView(APIView):
    """GET list, POST create for rows of a dynamic table."""
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    @extend_schema(
        summary='List rows',
        description='Paginated list of rows. Use query params matching field slugs for equality filter (e.g. ?name=foo).',
        parameters=[
            OpenApiParameter('page', int, description='Page number (1-based)'),
            OpenApiParameter('page_size', int, description='Page size'),
        ],
        tags=['Dynamic data'],
    )
    def get(self, request, project_pk, table_slug):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        allowed_slugs = {f.slug for f in table.fields.all()}
        filter_kwargs = {'table': table}
        for key, value in request.query_params.items():
            if key in ('page', 'page_size'):
                continue
            if key in allowed_slugs:
                filter_kwargs[f'data__{key}'] = value

        qs = DynamicTableRow.objects.filter(**filter_kwargs)
        total = qs.count()

        page = max(1, int(request.query_params.get('page', 1)))
        page_size = min(100, max(1, int(request.query_params.get('page_size', 20))))
        start = (page - 1) * page_size
        rows_qs = qs[start : start + page_size]

        rows = [serialize_row(r) for r in rows_qs]

        return Response({
            'results': rows,
            'count': total,
            'total': total,
            'page': page,
            'page_size': page_size,
        })

    @extend_schema(
        summary='Create row',
        description='Create a row. Body must match table field definitions.',
        request={'application/json': {'type': 'object'}},
        responses={201: {'type': 'object', 'properties': {'id': {'type': 'string'}, 'data': {'type': 'object'}}}},
        tags=['Dynamic data'],
    )
    def post(self, request, project_pk, table_slug):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        field_defs = list(table.fields.all().order_by('ordering', 'name'))
        cleaned, errors = validate_row_data(field_defs, request.data)
        if errors:
            return Response({'error': 'Validation failed.', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        row = DynamicTableRow.objects.create(table=table, data=cleaned)
        return Response(serialize_row(row), status=status.HTTP_201_CREATED)


class DynamicRowsExportView(APIView):
    """GET export table rows as .xlsx file."""
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    @extend_schema(
        summary='Export rows to Excel',
        description='Download all rows of this table as .xlsx. First row is headers (field names).',
        tags=['Dynamic data'],
    )
    def get(self, request, project_pk, table_slug):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        xlsx_bytes = export_table_to_xlsx(table)
        filename = f"{table.slug}_export.xlsx"
        response = HttpResponse(xlsx_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class DynamicRowsImportView(APIView):
    """POST import rows from .xlsx file (multipart)."""
    permission_classes = PROJECT_MEMBER_PERMISSIONS
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary='Import rows from Excel',
        description='Upload .xlsx with first row = headers (field names). Returns created count and per-row errors.',
        request={'multipart/form-data': {'type': 'object', 'properties': {'file': {'type': 'string', 'format': 'binary'}}}},
        tags=['Dynamic data'],
    )
    def post(self, request, project_pk, table_slug):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        if not (file_obj.name or '').lower().endswith('.xlsx'):
            return Response({'error': 'File must be .xlsx'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_bytes = file_obj.read()
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.exception("Failed to read imported Excel file")
            return Response({'error': 'Failed to read file. Please check the file format and try again.'}, status=status.HTTP_400_BAD_REQUEST)

        created, errors = import_rows_from_xlsx(table, file_bytes)
        return Response({'created': created, 'errors': errors})


class DynamicRowDetailView(APIView):
    """GET, PUT, PATCH, DELETE a single row by id."""
    permission_classes = PROJECT_MEMBER_PERMISSIONS

    @extend_schema(summary='Get row', tags=['Dynamic data'])
    def get(self, request, project_pk, table_slug, row_id):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        pk = parse_row_id(row_id)
        if pk is None:
            return Response({'error': 'Invalid row id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            row = DynamicTableRow.objects.get(pk=pk, table=table)
        except DynamicTableRow.DoesNotExist:
            return Response({'error': 'Row not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_row(row))

    @extend_schema(summary='Update row (full)', tags=['Dynamic data'])
    def put(self, request, project_pk, table_slug, row_id):
        return self._update(request, project_pk, table_slug, row_id, partial=False)

    @extend_schema(summary='Update row (partial)', tags=['Dynamic data'])
    def patch(self, request, project_pk, table_slug, row_id):
        return self._update(request, project_pk, table_slug, row_id, partial=True)

    @extend_schema(summary='Delete row', tags=['Dynamic data'])
    def delete(self, request, project_pk, table_slug, row_id):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        pk = parse_row_id(row_id)
        if pk is None:
            return Response({'error': 'Invalid row id.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = DynamicTableRow.objects.filter(pk=pk, table=table).delete()
        if not deleted:
            return Response({'error': 'Row not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _update(self, request, project_pk, table_slug, row_id, partial):
        business, table = get_project_and_table(project_pk, table_slug)
        if business is None or table is None:
            return Response({'error': 'Project or table not found.'}, status=status.HTTP_404_NOT_FOUND)

        pk = parse_row_id(row_id)
        if pk is None:
            return Response({'error': 'Invalid row id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            row = DynamicTableRow.objects.get(pk=pk, table=table)
        except DynamicTableRow.DoesNotExist:
            return Response({'error': 'Row not found.'}, status=status.HTTP_404_NOT_FOUND)

        field_defs = list(table.fields.all().order_by('ordering', 'name'))
        data = request.data if isinstance(request.data, dict) else {}
        if partial:
            data = {**row.data, **data}

        cleaned, errors = validate_row_data(field_defs, data)
        if errors:
            return Response({'error': 'Validation failed.', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

        row.data = cleaned
        row.save(update_fields=['data', 'updated_at'])
        return Response(serialize_row(row))
