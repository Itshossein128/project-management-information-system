"""REST CRUD for blueprint projects."""
import logging

from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsBusinessSetup
from events.publisher import EventPublisher
from master_data.models import MemberStatus, ProjectMember
from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from projects.serializers import (
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)
from projects.services import create_project_with_creator
from business_meta.services import create_project_from_template, get_available_templates

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary='List projects', tags=['Projects']),
    create=extend_schema(summary='Create project', tags=['Projects']),
    retrieve=extend_schema(summary='Get project', tags=['Projects']),
    partial_update=extend_schema(summary='Patch project', tags=['Projects']),
)
class ProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    lookup_field = 'pk'
    lookup_url_kwarg = 'project_pk'

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember()]
        if self.action in ('update', 'partial_update'):
            return [IsAuthenticated(), HasProjectPermission()]
        if self.action in ('templates', 'from_template'):
            return [IsBusinessSetup()]
        return [IsAuthenticated(), IsProjectMember()]

    def get_required_permission(self):
        if self.action in ('update', 'partial_update'):
            return 'edit_project'
        return ''

    @property
    def required_permission(self):
        return self.get_required_permission()

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'create':
            return ProjectCreateSerializer
        if self.action in ('update', 'partial_update'):
            return ProjectUpdateSerializer
        return ProjectDetailSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Project.objects.select_related('project_manager').annotate(
            member_count=Count('members', filter=Q(members__status=MemberStatus.ACTIVE)),
        )
        if user.is_superuser or user.groups.filter(name='admin').exists():
            return qs
        active_project_ids = ProjectMember.objects.filter(
            user=user,
            status=MemberStatus.ACTIVE,
        ).values_list('project_id', flat=True)
        return qs.filter(id__in=active_project_ids)

    def perform_create(self, serializer):
        project = create_project_with_creator(
            creator=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = project
        try:
            EventPublisher().publish(
                'schedule.updated',
                {'project_id': str(project.id), 'action': 'created'},
                project_id=str(project.id),
            )
        except Exception:
            logger.exception('Failed to publish schedule.updated for project %s', project.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = ProjectDetailSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(summary='List available templates', tags=['Projects'])
    @action(detail=False, methods=['get'], url_path='templates')
    def templates(self, request):
        return Response(get_available_templates())

    @extend_schema(summary='Create project from template', tags=['Projects'])
    @action(detail=False, methods=['post'], url_path='from_template')
    def from_template(self, request):
        name = request.data.get('name') or request.data.get('project_name')
        code = request.data.get('slug') or request.data.get('project_code')
        template = request.data.get('template')
        if not name or not code or not template:
            return Response(
                {'error': 'name, slug (project_code), and template are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            project = create_project_from_template(
                name=name,
                project_code=code,
                template_id=template,
                creator=request.user,
            )
            return Response(ProjectDetailSerializer(project).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.exception('Failed to create project from template')
            error_message = str(e)
            if 'Unknown template' in error_message:
                safe_message = 'Unknown template. Please choose a valid template.'
            elif 'already exists' in error_message:
                safe_message = 'A project with this code already exists.'
            else:
                safe_message = 'Failed to create project from template. Please check the provided data.'
            return Response({'error': safe_message}, status=status.HTTP_400_BAD_REQUEST)
