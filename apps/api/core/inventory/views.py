from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from config.pagination import DefaultPageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import pandas as pd
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework.permissions import IsAuthenticated

from business_meta.permissions import CanViewBusinessAssignments, IsVisitorReadOnly, IsHrOrAdminOrReadOnly

from .department_activity_services import get_department_activity_queryset
from .models import (
    Item,
    Category,
    SpaceMaterialRequest,
    DepartmentActivityRecord,
)
from .serializers import (
    ItemSerializer,
    SpaceMaterialRequestSerializer,
    DepartmentActivityRecordSerializer,
)


class DepartmentActivityRecordPagination(DefaultPageNumberPagination):
    """Department activity grids use the shared default pagination."""


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing inventory items.
    
    Provides CRUD operations for items and Excel import/export functionality.
    """
    queryset = Item.objects.select_related('category').all()
    serializer_class = ItemSerializer

    @extend_schema(
        summary="Export items to Excel",
        description="Download all items as an Excel file (.xlsx)",
        responses={
            200: OpenApiResponse(
                description="Excel file containing all items",
                response=OpenApiTypes.BINARY,
            )
        },
        tags=['Items']
    )
    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export all items to Excel file"""
        items = Item.objects.all().values('id', 'name', 'quantity', 'category__name')
        df = pd.DataFrame(list(items))
        df.rename(columns={'category__name': 'category'}, inplace=True)
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=items.xlsx'
        df.to_excel(response, index=False, engine='openpyxl')
        return response

    @extend_schema(
        summary="Import items from Excel",
        description="Upload an Excel file to import items. The file must contain columns: name, quantity, category",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Excel file (.xlsx) with columns: name, quantity, category'
                    }
                },
                'required': ['file']
            }
        },
        responses={
            201: OpenApiResponse(
                description="Items imported successfully",
                response={
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'imported_count': {'type': 'integer'},
                        'errors': {'type': 'array', 'items': {'type': 'string'}, 'nullable': True}
                    }
                }
            ),
            400: OpenApiResponse(
                description="Bad request - missing file or invalid format",
                response={
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            )
        },
        tags=['Items']
    )
    @action(detail=False, methods=['post'])
    def import_items(self, request):
        """Import items from Excel file"""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        try:
            df = pd.read_excel(file, engine='openpyxl')
            
            # Validate required columns
            required_columns = ['name', 'quantity', 'category']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            imported_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    category_name = row['category']
                    category, created = Category.objects.get_or_create(name=category_name)
                    
                    Item.objects.create(
                        name=row['name'],
                        quantity=int(row['quantity']),
                        category=category
                    )
                    imported_count += 1
                except Exception as e:
                    errors.append(f'Row {index + 2}: {str(e)}')  # +2 because Excel rows start at 1 and header is row 1
            
            return Response({
                'message': f'Successfully imported {imported_count} items',
                'imported_count': imported_count,
                'errors': errors if errors else None
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Error processing file: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    list=extend_schema(
        summary='List space material requests for a business (grid)',
        description=(
            'Grid endpoint for listing space material requests inside a business. '
            'Supports simple filtering via query parameters.'
        ),
        parameters=[
            OpenApiParameter(name='block_number', type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name='floor_number', type=OpenApiTypes.INT, required=False),
            OpenApiParameter(name='unit_number', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='space_name', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='material_code', type=OpenApiTypes.STR, required=False),
        ],
        tags=['Project inventory'],
    ),
    create=extend_schema(
        summary='Create space material request for a business (form)',
        description='Form endpoint to create a new space material request under a business.',
        tags=['Project inventory'],
    ),
    retrieve=extend_schema(summary='Get space material request', tags=['Project inventory']),
    update=extend_schema(summary='Update space material request', tags=['Project inventory']),
    partial_update=extend_schema(summary='Patch space material request', tags=['Project inventory']),
    destroy=extend_schema(summary='Delete space material request', tags=['Project inventory']),
)
class SpaceMaterialRequestViewSet(viewsets.ModelViewSet):
    """
    Project-scoped CRUD for SpaceMaterialRequest.
    """

    serializer_class = SpaceMaterialRequestSerializer
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        # Read: authenticated users who can view business data; Write: HR/admin; Visitors read-only.
        return [
            IsAuthenticated(),
            CanViewBusinessAssignments(),
            IsVisitorReadOnly(),
            IsHrOrAdminOrReadOnly(),
        ]

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        qs = SpaceMaterialRequest.objects.all()
        if project_pk is not None:
            qs = qs.filter(project_id=project_pk)

        # Grid filters
        params = self.request.query_params
        block_number = params.get('block_number')
        floor_number = params.get('floor_number')
        unit_number = params.get('unit_number')
        space_name = params.get('space_name')
        material_code = params.get('material_code')

        if block_number not in (None, ''):
            qs = qs.filter(block_number=block_number)
        if floor_number not in (None, ''):
            qs = qs.filter(floor_number=floor_number)
        if unit_number:
            qs = qs.filter(unit_number__icontains=unit_number)
        if space_name:
            qs = qs.filter(space_name__icontains=space_name)
        if material_code:
            qs = qs.filter(material_code__icontains=material_code)

        # ⚡ Bolt: added 'project' to select_related to prevent N+1 query when serializing project_id
        return qs.select_related('business', 'project')

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('project_pk')
        serializer.save(project_id=project_pk)


@extend_schema_view(
    list=extend_schema(
        summary='List department activity records for a business (grid)',
        description=(
            'Grid endpoint for listing per-department activity records inside a business. '
            'Supports a `department` filter (required for department pages) plus search and '
            'simple field filters. `date_from` and `date_to` are inclusive bounds (YYYY-MM-DD).'
        ),
        parameters=[
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.STR,
                required=False,
                description='Department slug; one of: buildings, mechanical, security, machinery, warehouse, electrical.',
            ),
            OpenApiParameter(name='date_from', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='date_to', type=OpenApiTypes.DATE, required=False),
            OpenApiParameter(name='location', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='activity_description', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='contractor', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(name='unit', type=OpenApiTypes.STR, required=False),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                required=False,
                description='Free-text search across location, activity_description, contractor, unit.',
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                required=False,
                description='Field to order by, prefix with `-` for desc. E.g. `-date`, `location`, `activity_description`.',
            ),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, required=False),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                required=False,
                description='Page size (default 20, max 100).',
            ),
        ],
        tags=['Project activity records'],
    ),
    create=extend_schema(
        summary='Create department activity record',
        description='Form endpoint to create a new activity record under a business.',
        tags=['Project activity records'],
    ),
    retrieve=extend_schema(summary='Get department activity record', tags=['Project activity records']),
    update=extend_schema(summary='Update department activity record', tags=['Project activity records']),
    partial_update=extend_schema(summary='Patch department activity record', tags=['Project activity records']),
    destroy=extend_schema(summary='Delete department activity record', tags=['Project activity records']),
)
class DepartmentActivityRecordViewSet(viewsets.ModelViewSet):
    """
    Project-scoped CRUD for `DepartmentActivityRecord`.

    Frontend per-department pages call this endpoint with `?department=<slug>`
    so the same model serves all six department grids.
    """

    serializer_class = DepartmentActivityRecordSerializer
    pagination_class = DepartmentActivityRecordPagination
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    _ALLOWED_ORDERING_FIELDS = {
        'date',
        '-date',
        'created_at',
        '-created_at',
        'updated_at',
        '-updated_at',
        'location',
        '-location',
        'activity_description',
        '-activity_description',
        'contractor',
        '-contractor',
        'unit',
        '-unit',
    }

    def get_permissions(self):
        return [
            IsAuthenticated(),
            CanViewBusinessAssignments(),
            IsVisitorReadOnly(),
            IsHrOrAdminOrReadOnly(),
        ]

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        if project_pk is None:
            return DepartmentActivityRecord.objects.none()
        return get_department_activity_queryset(project_pk, self.request.query_params)

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('project_pk')
        serializer.save(project_id=project_pk)