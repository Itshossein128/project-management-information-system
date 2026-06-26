"""REST CRUD for blueprint projects."""
import logging

from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsBusinessSetup
from events.publisher import EventPublisher
from master_data.models import ProjectMember
from projects.models import Project
from projects.permissions import IsProjectMember
from projects.serializers import ProjectSerializer
from business_meta.services import create_project_from_template, get_available_templates

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary='List projects', tags=['Projects']),
    create=extend_schema(summary='Create project', tags=['Projects']),
    retrieve=extend_schema(summary='Get project', tags=['Projects']),
    update=extend_schema(summary='Update project', tags=['Projects']),
    partial_update=extend_schema(summary='Patch project', tags=['Projects']),
    destroy=extend_schema(summary='Delete project', tags=['Projects']),
)
class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsBusinessSetup()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='admin').exists():
            return Project.objects.all()
        member_project_ids = ProjectMember.objects.filter(user=user).values_list('project_id', flat=True)
        return Project.objects.filter(Q(id__in=member_project_ids) | Q(project_manager=user))

    def perform_create(self, serializer):
        project = serializer.save()
        try:
            EventPublisher().publish(
                'schedule.updated',
                {'project_id': str(project.id), 'action': 'created'},
                project_id=str(project.id),
            )
        except Exception:
            logger.exception('Failed to publish schedule.updated for project %s', project.id)

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
            project = create_project_from_template(name=name, project_code=code, template_id=template)
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
