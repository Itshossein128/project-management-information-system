"""
REST CRUD for business meta. Protected by IsBusinessSetup.
"""
from rest_framework import viewsets, status, permissions as drf_permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view
from authentication.permissions import IsBusinessSetup, IsHrOrAdmin

from .models import (
    Business,
    UserBusinessAssignment,
    BusinessJobPosition,
    TableDefinition,
    FieldDefinition,
    RelationDefinition,
)
from .permissions import CanViewBusinessAssignments, IsVisitorReadOnly
from .services import create_business_from_template, get_available_templates
from .serializers import (
    BusinessSerializer,
    BusinessJobPositionSerializer,
    UserBusinessAssignmentReadSerializer,
    UserBusinessAssignmentCreateSerializer,
    UserBusinessAssignmentWriteSerializer,
    TableDefinitionSerializer,
    TableDefinitionListSerializer,
    TableDefinitionWithFieldsSerializer,
    FieldDefinitionSerializer,
    RelationDefinitionSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='List businesses', tags=['Business meta']),
    create=extend_schema(summary='Create business', tags=['Business meta']),
    retrieve=extend_schema(summary='Get business', tags=['Business meta']),
    update=extend_schema(summary='Update business', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch business', tags=['Business meta']),
    destroy=extend_schema(summary='Delete business', tags=['Business meta']),
)
# Class representing BusinessViewSet
class BusinessViewSet(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    # Function to handle get permissions
    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsBusinessSetup()]

    # Function to handle get serializer context
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['business_pk'] = self.kwargs.get('business_pk')
        return context

    @extend_schema(
        summary='List available templates',
        description='Returns template ids and names for creating a business from a template.',
        tags=['Business meta'],
    )
    @action(detail=False, methods=['get'], url_path='templates')
    # Function to handle templates
    def templates(self, request):
        return Response(get_available_templates())

    @extend_schema(
        summary='Create business from template',
        description='Creates a new business with tables and fields defined by the template (e.g. warehouse).',
        request={
            'application/json': {
                'type': 'object',
                'required': ['name', 'slug', 'template'],
                'properties': {
                    'name': {'type': 'string', 'description': 'Business display name'},
                    'slug': {'type': 'string', 'description': 'Unique slug (lowercase, letters, numbers, underscores)'},
                    'template': {'type': 'string', 'enum': ['warehouse'], 'description': 'Template identifier'},
                },
            }
        },
        responses={
            201: BusinessSerializer,
            400: {'description': 'Bad request (unknown template or duplicate slug)'},
        },
        tags=['Business meta'],
    )
    @action(detail=False, methods=['post'], url_path='from_template')
    # Function to handle from template
    def from_template(self, request):
        name = request.data.get('name')
        slug = request.data.get('slug')
        template = request.data.get('template')
        if not name or not slug or not template:
            return Response(
                {'error': 'name, slug, and template are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            business = create_business_from_template(name=name, slug=slug, template_id=template)
            serializer = BusinessSerializer(business)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(summary='List tables of a business', tags=['Business meta']),
    create=extend_schema(summary='Create table', tags=['Business meta']),
    retrieve=extend_schema(summary='Get table', tags=['Business meta']),
    update=extend_schema(summary='Update table', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch table', tags=['Business meta']),
    destroy=extend_schema(summary='Delete table', tags=['Business meta']),
)
# Class representing TableDefinitionViewSet
class TableDefinitionViewSet(viewsets.ModelViewSet):
    serializer_class = TableDefinitionSerializer

    # Function to handle get permissions
    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'by_slug'):
            return [IsAuthenticated()]
        return [IsBusinessSetup()]

    # Function to handle get queryset
    def get_queryset(self):
        business_pk = self.kwargs.get('business_pk')
        if business_pk is not None:
            return TableDefinition.objects.filter(business_id=business_pk)
        return TableDefinition.objects.all()

    # Function to handle get serializer class
    def get_serializer_class(self):
        if self.action == 'list':
            return TableDefinitionListSerializer
        return TableDefinitionSerializer

    # Function to handle perform create
    def perform_create(self, serializer):
        business_pk = self.kwargs.get('business_pk')
        if business_pk is not None:
            serializer.save(business_id=business_pk)
        else:
            serializer.save()

    @extend_schema(summary='Get table by slug (with fields)', tags=['Business meta'])
    # Function to handle by slug
    def by_slug(self, request, business_pk=None, table_slug=None):
        from rest_framework.exceptions import NotFound
        table = TableDefinition.objects.filter(business_id=business_pk, slug=table_slug).first()
        if table is None:
            raise NotFound('Table not found.')
        serializer = TableDefinitionWithFieldsSerializer(table)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(summary='List job positions for a business', tags=['Business meta']),
    create=extend_schema(summary='Create job position', tags=['Business meta']),
    retrieve=extend_schema(summary='Get job position', tags=['Business meta']),
    update=extend_schema(summary='Update job position', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch job position', tags=['Business meta']),
    destroy=extend_schema(summary='Delete job position', tags=['Business meta']),
)
# Class representing BusinessJobPositionViewSet
class BusinessJobPositionViewSet(viewsets.ModelViewSet):
    """Per-business job titles (not system roles)."""
    serializer_class = BusinessJobPositionSerializer
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    # Function to handle get permissions
    def get_permissions(self):
        if self.request.method in drf_permissions.SAFE_METHODS:
            return [IsAuthenticated(), CanViewBusinessAssignments(), IsVisitorReadOnly()]
        return [IsAuthenticated(), IsHrOrAdmin(), IsVisitorReadOnly()]

    # Function to handle get queryset
    def get_queryset(self):
        business_pk = self.kwargs.get('business_pk')
        return BusinessJobPosition.objects.filter(business_id=business_pk).select_related('business')

    # Function to handle perform create
    def perform_create(self, serializer):
        business_pk = self.kwargs.get('business_pk')
        serializer.save(business_id=business_pk)

    # Function to handle perform destroy
    def perform_destroy(self, instance: BusinessJobPosition) -> None:
        if UserBusinessAssignment.objects.filter(job_position=instance).exists():
            raise ValidationError(
                'This job position is still assigned to one or more users; reassign or remove them first.'
            )
        super().perform_destroy(instance)


@extend_schema_view(
    list=extend_schema(summary='List user–business assignments', tags=['Business meta']),
    create=extend_schema(summary='Assign user to business', tags=['Business meta']),
    retrieve=extend_schema(summary='Get assignment', tags=['Business meta']),
    update=extend_schema(summary='Replace assignment', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch assignment', tags=['Business meta']),
    destroy=extend_schema(summary='Remove assignment', tags=['Business meta']),
)
# Class representing UserBusinessAssignmentViewSet
class UserBusinessAssignmentViewSet(viewsets.ModelViewSet):
    """
    User–business assignments with wage, tools, dates, status.
    Read: member of business or HR/admin. Write: HR/admin (visitors read-only).
    """
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    # Function to handle get permissions
    def get_permissions(self):
        if self.request.method in drf_permissions.SAFE_METHODS:
            return [IsAuthenticated(), CanViewBusinessAssignments(), IsVisitorReadOnly()]
        return [IsAuthenticated(), IsHrOrAdmin(), IsVisitorReadOnly()]

    # Function to handle get queryset
    def get_queryset(self):
        business_pk = self.kwargs.get('business_pk')
        return (
            UserBusinessAssignment.objects.filter(business_id=business_pk)
            .select_related('user', 'business', 'job_position')
        )

    # Function to handle get serializer class
    def get_serializer_class(self):
        if self.action == 'create':
            return UserBusinessAssignmentCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserBusinessAssignmentWriteSerializer
        return UserBusinessAssignmentReadSerializer

    # Function to handle get serializer context
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['business_pk'] = self.kwargs.get('business_pk')
        return context


@extend_schema_view(
    list=extend_schema(summary='List fields of a table', tags=['Business meta']),
    create=extend_schema(summary='Create field', tags=['Business meta']),
    retrieve=extend_schema(summary='Get field', tags=['Business meta']),
    update=extend_schema(summary='Update field', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch field', tags=['Business meta']),
    destroy=extend_schema(summary='Delete field', tags=['Business meta']),
)
# Class representing FieldDefinitionViewSet
class FieldDefinitionViewSet(viewsets.ModelViewSet):
    serializer_class = FieldDefinitionSerializer
    permission_classes = [IsBusinessSetup]

    # Function to handle get queryset
    def get_queryset(self):
        table_pk = self.kwargs.get('table_pk')
        if table_pk is not None:
            return FieldDefinition.objects.filter(table_id=table_pk)
        return FieldDefinition.objects.all()

    # Function to handle perform create
    def perform_create(self, serializer):
        table_pk = self.kwargs.get('table_pk')
        if table_pk is not None:
            serializer.save(table_id=table_pk)
        else:
            serializer.save()


@extend_schema_view(
    list=extend_schema(summary='List relations', tags=['Business meta']),
    create=extend_schema(summary='Create relation', tags=['Business meta']),
    retrieve=extend_schema(summary='Get relation', tags=['Business meta']),
    update=extend_schema(summary='Update relation', tags=['Business meta']),
    partial_update=extend_schema(summary='Patch relation', tags=['Business meta']),
    destroy=extend_schema(summary='Delete relation', tags=['Business meta']),
)
# Class representing RelationDefinitionViewSet
class RelationDefinitionViewSet(viewsets.ModelViewSet):
    queryset = RelationDefinition.objects.all()
    serializer_class = RelationDefinitionSerializer
    permission_classes = [IsBusinessSetup]
