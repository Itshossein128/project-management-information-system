"""REST CRUD for project meta and dynamic schema."""
from rest_framework import viewsets, permissions as drf_permissions
from common.mixins import ProjectNestedViewSetMixin
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsBusinessSetup, IsHrOrAdmin
from projects.permissions import IsProjectMember
from master_data.models import ProjectMember, ProjectPosition
from .models import TableDefinition, FieldDefinition, RelationDefinition
from .permissions import CanViewProjectMembers, IsVisitorReadOnly
from .serializers import (
    ProjectPositionSerializer,
    ProjectMemberReadSerializer,
    ProjectMemberCreateSerializer,
    ProjectMemberWriteSerializer,
    TableDefinitionSerializer,
    TableDefinitionListSerializer,
    TableDefinitionWithFieldsSerializer,
    FieldDefinitionSerializer,
    RelationDefinitionSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='List tables of a project', tags=['Project meta']),
    create=extend_schema(summary='Create table', tags=['Project meta']),
    retrieve=extend_schema(summary='Get table', tags=['Project meta']),
    update=extend_schema(summary='Update table', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch table', tags=['Project meta']),
    destroy=extend_schema(summary='Delete table', tags=['Project meta']),
)
class TableDefinitionViewSet(ProjectNestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = TableDefinitionSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'by_slug'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsBusinessSetup()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TableDefinitionListSerializer
        return TableDefinitionSerializer

    @extend_schema(summary='Get table by slug (with fields)', tags=['Project meta'])
    def by_slug(self, request, project_pk=None, table_slug=None):
        table = TableDefinition.objects.filter(project_id=project_pk, slug=table_slug).first()
        if table is None:
            raise NotFound('Table not found.')
        return Response(TableDefinitionWithFieldsSerializer(table).data)


@extend_schema_view(
    list=extend_schema(summary='List project positions', tags=['Project meta']),
    create=extend_schema(summary='Create position', tags=['Project meta']),
    retrieve=extend_schema(summary='Get position', tags=['Project meta']),
    update=extend_schema(summary='Update position', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch position', tags=['Project meta']),
    destroy=extend_schema(summary='Delete position', tags=['Project meta']),
)
class ProjectPositionViewSet(ProjectNestedViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ProjectPositionSerializer
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in drf_permissions.SAFE_METHODS:
            return [IsAuthenticated(), CanViewProjectMembers(), IsVisitorReadOnly()]
        return [IsAuthenticated(), IsHrOrAdmin(), IsVisitorReadOnly()]

    def get_queryset(self):
        return super().get_queryset().select_related('project')

    def perform_destroy(self, instance: ProjectPosition) -> None:
        if ProjectMember.objects.filter(position=instance).exists():
            raise ValidationError('Position is still assigned to members.')
        super().perform_destroy(instance)


@extend_schema_view(
    list=extend_schema(summary='List project members', tags=['Project meta']),
    create=extend_schema(summary='Add project member', tags=['Project meta']),
    retrieve=extend_schema(summary='Get member', tags=['Project meta']),
    update=extend_schema(summary='Update member', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch member', tags=['Project meta']),
    destroy=extend_schema(summary='Remove member', tags=['Project meta']),
)
class ProjectMemberViewSet(ProjectNestedViewSetMixin, viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in drf_permissions.SAFE_METHODS:
            return [IsAuthenticated(), CanViewProjectMembers(), IsVisitorReadOnly()]
        return [IsAuthenticated(), IsHrOrAdmin(), IsVisitorReadOnly()]

    def get_queryset(self):
        return super().get_queryset().select_related(
            'user', 'project', 'position'
        )

    def perform_create(self, serializer):
        # Disable mixin's perform_create logic
        super(viewsets.ModelViewSet, self).perform_create(serializer)

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectMemberCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ProjectMemberWriteSerializer
        return ProjectMemberReadSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_pk'] = self.kwargs.get('project_pk')
        return context


@extend_schema_view(
    list=extend_schema(summary='List fields of a table', tags=['Project meta']),
    create=extend_schema(summary='Create field', tags=['Project meta']),
    retrieve=extend_schema(summary='Get field', tags=['Project meta']),
    update=extend_schema(summary='Update field', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch field', tags=['Project meta']),
    destroy=extend_schema(summary='Delete field', tags=['Project meta']),
)
class FieldDefinitionViewSet(ProjectNestedViewSetMixin, viewsets.ModelViewSet):
    nested_url_kwarg = 'table_pk'
    nested_model_field = 'table_id'

    serializer_class = FieldDefinitionSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsBusinessSetup()]


@extend_schema_view(
    list=extend_schema(summary='List relations', tags=['Project meta']),
    create=extend_schema(summary='Create relation', tags=['Project meta']),
    retrieve=extend_schema(summary='Get relation', tags=['Project meta']),
    update=extend_schema(summary='Update relation', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch relation', tags=['Project meta']),
    destroy=extend_schema(summary='Delete relation', tags=['Project meta']),
)
class RelationDefinitionViewSet(viewsets.ModelViewSet):
    queryset = RelationDefinition.objects.all()
    serializer_class = RelationDefinitionSerializer
    permission_classes = [IsBusinessSetup]


# Backward-compatible aliases
BusinessJobPositionViewSet = ProjectPositionViewSet
UserBusinessAssignmentViewSet = ProjectMemberViewSet
