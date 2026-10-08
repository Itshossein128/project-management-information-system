"""REST CRUD for blueprint projects."""
import logging

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsBusinessSetup
from events.publisher import EventPublisher
from master_data.models import MemberStatus, ProjectMember
from permissions.project import HasProjectPermission, IsProjectMember
from projects import change_request_service, charter_service, lifecycle_service
from projects.models import Project, ProjectChangeRequest
from projects.serializers import (
    ProjectChangeRequestSerializer,
    ProjectCreateSerializer,
    ProjectDetailSerializer,
    ProjectKickoffCharterSerializer,
    ProjectListSerializer,
    ProjectUpdateSerializer,
)
from projects.services import create_project_with_creator
from business_meta.services import create_project_from_template, get_available_templates

logger = logging.getLogger(__name__)


def _detail(project):
    return ProjectDetailSerializer(project).data


@extend_schema_view(
    list=extend_schema(summary='List projects', tags=['Projects']),
    create=extend_schema(summary='Create project', tags=['Projects']),
    retrieve=extend_schema(summary='Get project', tags=['Projects']),
    partial_update=extend_schema(summary='Patch project', tags=['Projects']),
    destroy=extend_schema(summary='Delete project', tags=['Projects']),
)
class ProjectViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    lookup_field = 'pk'
    lookup_url_kwarg = 'project_pk'

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember()]
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), HasProjectPermission()]
        if self.action in ('templates', 'from_template'):
            return [IsBusinessSetup()]
        if self.action in (
            'submit', 'reject', 'suspend', 'resume', 'complete', 'archive',
        ):
            return [IsAuthenticated(), HasProjectPermission()]
        if self.action == 'approve':
            return [IsAuthenticated(), HasProjectPermission()]
        return [IsAuthenticated(), IsProjectMember()]

    def get_required_permission(self):
        if self.action == 'approve':
            return 'approve_project'
        if self.action in (
            'update', 'partial_update', 'destroy',
            'submit', 'reject', 'suspend', 'resume', 'complete', 'archive',
        ):
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
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        lifecycle_service.assert_not_archived_mutable(instance, request.user)
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        lifecycle_service.assert_not_archived_mutable(instance, request.user)
        return super().destroy(request, *args, **kwargs)

    def _lifecycle(self, request, fn, **kwargs):
        project = self.get_object()
        project = fn(project, request.user, **kwargs)
        return Response(_detail(project))

    @extend_schema(summary='Submit project for approval', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.submit_for_approval)

    @extend_schema(summary='Approve project to active', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.approve)

    @extend_schema(summary='Reject project approval', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, project_pk=None):
        return self._lifecycle(
            request,
            lifecycle_service.reject,
            reason=request.data.get('reason', ''),
        )

    @extend_schema(summary='Suspend project', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='suspend')
    def suspend(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.suspend)

    @extend_schema(summary='Resume suspended project', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='resume')
    def resume(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.resume)

    @extend_schema(summary='Mark project completed', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.complete)

    @extend_schema(summary='Archive project', tags=['Projects'])
    @action(detail=True, methods=['post'], url_path='archive')
    def archive(self, request, project_pk=None):
        return self._lifecycle(request, lifecycle_service.archive)

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


class ProjectKickoffCharterView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_project' if self.request.method == 'GET' else 'edit_project'

    def get(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        charter = charter_service.get_charter(project)
        if charter is None:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectKickoffCharterSerializer(charter).data)

    def put(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        ser = ProjectKickoffCharterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        charter = charter_service.upsert_charter(
            project, request.user, partial=False, **ser.validated_data,
        )
        return Response(ProjectKickoffCharterSerializer(charter).data)

    def patch(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        ser = ProjectKickoffCharterSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        charter = charter_service.upsert_charter(
            project, request.user, partial=True, **ser.validated_data,
        )
        return Response(ProjectKickoffCharterSerializer(charter).data)


class ProjectChangeRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_project' if self.request.method == 'GET' else 'edit_project'

    def get(self, request, project_pk=None):
        qs = change_request_service.list_change_requests(project_pk)
        return Response(ProjectChangeRequestSerializer(qs, many=True).data)

    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        cr = change_request_service.create_change_request(
            project=project,
            user=request.user,
            reason=request.data.get('reason', ''),
            proposed_changes=request.data.get('proposed_changes') or {},
        )
        return Response(ProjectChangeRequestSerializer(cr).data, status=status.HTTP_201_CREATED)


class ProjectChangeRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        return 'view_project' if self.request.method == 'GET' else 'edit_project'

    def get_object(self, project_pk, pk):
        return get_object_or_404(
            ProjectChangeRequest, pk=pk, project_id=project_pk, is_deleted=False,
        )

    def get(self, request, project_pk=None, pk=None):
        cr = self.get_object(project_pk, pk)
        return Response(ProjectChangeRequestSerializer(cr).data)

    def patch(self, request, project_pk=None, pk=None):
        cr = self.get_object(project_pk, pk)
        cr = change_request_service.update_change_request(
            cr,
            request.user,
            reason=request.data.get('reason', cr.reason),
            proposed_changes=request.data.get('proposed_changes', cr.proposed_changes),
        )
        return Response(ProjectChangeRequestSerializer(cr).data)


class ProjectChangeRequestActionView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    def get_required_permission(self):
        action_name = self.kwargs.get('action_name')
        if action_name in ('approve', 'reject'):
            return 'approve_project'
        return 'edit_project'

    @property
    def required_permission(self):
        return self.get_required_permission()

    def post(self, request, project_pk=None, pk=None, action_name=None):
        cr = get_object_or_404(
            ProjectChangeRequest, pk=pk, project_id=project_pk, is_deleted=False,
        )
        notes = request.data.get('decision_notes', '')
        if action_name == 'submit':
            cr = change_request_service.submit_change_request(cr, request.user)
        elif action_name == 'approve':
            cr = change_request_service.approve_change_request(cr, request.user, notes)
        elif action_name == 'reject':
            cr = change_request_service.reject_change_request(cr, request.user, notes)
        elif action_name == 'cancel':
            cr = change_request_service.cancel_change_request(cr, request.user)
        else:
            return Response({'detail': 'Unknown action'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectChangeRequestSerializer(cr).data)
