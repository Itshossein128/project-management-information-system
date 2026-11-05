"""REST CRUD for project meta and dynamic schema."""
from django.db.models import Q
from rest_framework import viewsets, permissions as drf_permissions
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsBusinessSetup, IsHrOrAdmin
from common.mixins import ProjectNestedViewSetMixin
from permissions.project import ActiveMemberPermission
from projects.permissions import IsProjectMember
from master_data.models import ProjectMember, ProjectPosition
from .models import TableDefinition, FieldDefinition, RelationDefinition
from .permissions import CanViewProjectMembers, IsVisitorReadOnly
from .serializers import (
    ProjectPositionSerializer,
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
    queryset = TableDefinition.objects.all()
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
    queryset = ProjectPosition.objects.select_related('project')
    serializer_class = ProjectPositionSerializer
    http_method_names = ['get', 'post', 'patch', 'put', 'delete', 'head', 'options']

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        if (
            self.request.method in drf_permissions.SAFE_METHODS
            and self.request.query_params.get('selectable') == '1'
        ):
            return ProjectPosition.objects.filter(is_active=True).filter(
                Q(project_id=project_pk) | Q(project__isnull=True),
            )
        return super().get_queryset()

    def get_permissions(self):
        if self.request.method in drf_permissions.SAFE_METHODS:
            return [IsAuthenticated(), CanViewProjectMembers(), IsVisitorReadOnly()]
        write_permission = ActiveMemberPermission()
        write_permission.codename = 'manage_members'
        return [IsAuthenticated(), write_permission, IsVisitorReadOnly()]

    def perform_destroy(self, instance: ProjectPosition) -> None:
        if ProjectMember.objects.filter(position=instance).exists():
            raise ValidationError('Position is still assigned to members.')
        super().perform_destroy(instance)


@extend_schema_view(
    list=extend_schema(summary='List fields of a table', tags=['Project meta']),
    create=extend_schema(summary='Create field', tags=['Project meta']),
    retrieve=extend_schema(summary='Get field', tags=['Project meta']),
    update=extend_schema(summary='Update field', tags=['Project meta']),
    partial_update=extend_schema(summary='Patch field', tags=['Project meta']),
    destroy=extend_schema(summary='Delete field', tags=['Project meta']),
)
class FieldDefinitionViewSet(ProjectNestedViewSetMixin, viewsets.ModelViewSet):
    queryset = FieldDefinition.objects.all()
    serializer_class = FieldDefinitionSerializer
    nested_url_kwarg = 'table_pk'
    nested_model_field = 'table_id'

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


# Backward-compatible alias
BusinessJobPositionViewSet = ProjectPositionViewSet
