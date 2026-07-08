from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from permissions.project import HasProjectPermission, IsProjectMember
from projects.models import Project
from project_templates.models import ProjectTemplate
from project_templates.serializers import (
    ProjectTemplateCreateSerializer,
    ProjectTemplateDetailSerializer,
    ProjectTemplateListSerializer,
    SaveAsTemplateSerializer,
)
from project_templates.services import apply_template_to_project, save_project_as_template


class ProjectTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProjectTemplate.objects.all().order_by('template_name')
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectTemplateDetailSerializer
        if self.action == 'create':
            return ProjectTemplateCreateSerializer
        return ProjectTemplateListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        project_type = self.request.query_params.get('project_type')
        is_system = self.request.query_params.get('is_system')
        if project_type:
            qs = qs.filter(project_type=project_type)
        if is_system is not None:
            qs = qs.filter(is_system=is_system.lower() in ('1', 'true', 'yes'))
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, is_system=False)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {'error': {'code': 'permission_denied', 'message': 'System templates cannot be edited.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_system:
            return Response(
                {'error': {'code': 'permission_denied', 'message': 'System templates cannot be deleted.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @extend_schema(summary='Apply template to project', tags=['Project templates'])
    @action(detail=True, methods=['post'], url_path=r'apply/(?P<project_id>[^/.]+)')
    def apply(self, request, pk=None, project_id=None):
        template = self.get_object()
        project = get_object_or_404(Project, pk=project_id)
        force = request.query_params.get('force', 'false').lower() in ('1', 'true', 'yes')
        try:
            result = apply_template_to_project(template, project, force=force, user=request.user)
        except ValueError as exc:
            return Response(
                {'error': {'code': 'validation_error', 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(result)


class SaveProjectAsTemplateView(APIView):
    permission_classes = [IsAuthenticated, HasProjectPermission]
    required_permission = 'edit_wbs'

    @extend_schema(summary='Save project WBS as template', tags=['Project templates'])
    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = SaveAsTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        is_system = data.get('is_system', False)
        if is_system and not (request.user.is_superuser or request.user.groups.filter(name='admin').exists()):
            return Response(
                {'error': {'code': 'permission_denied', 'message': 'Only admins can create system templates.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        template = save_project_as_template(
            project,
            template_name=data['template_name'],
            description=data.get('description', ''),
            project_type=data.get('project_type', 'other'),
            created_by=request.user,
            is_system=is_system,
        )
        return Response(ProjectTemplateDetailSerializer(template).data, status=status.HTTP_201_CREATED)
