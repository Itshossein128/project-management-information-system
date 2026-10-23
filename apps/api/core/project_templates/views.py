from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from permissions.project import HasProjectPermission, IsProjectMember, member_has_codename
from projects.models import Project
from project_templates.models import ProjectReportingConfiguration, ProjectTemplate
from project_templates.models import (
    LaborTitleCatalog,
    LaborTitleCatalogTitle,
    ProjectReportingConfiguration,
    ProjectTemplate,
)
from project_templates.serializers import (
    LaborTitleCatalogCreateSerializer,
    LaborTitleCatalogSerializer,
    LaborTitleCatalogTitleSerializer,
    ProjectReportingConfigurationActivateSerializer,
    ProjectReportingConfigurationPreviewSerializer,
    ProjectReportingConfigurationSerializer,
    ProjectTemplateCreateSerializer,
    ProjectTemplateDetailSerializer,
    ProjectTemplateListSerializer,
    SaveAsTemplateSerializer,
)
from project_templates.services import (
    ReportingConfigurationConflict,
    activate_project_reporting_configuration,
    apply_template_to_project,
    create_labor_catalog,
    preview_project_reporting_configuration,
    save_project_as_template,
    update_labor_catalog,
)


class ProjectTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProjectTemplate.objects.all().order_by('template_name')
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectTemplateDetailSerializer
        if self.action in ('create', 'update', 'partial_update'):
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

        if self.action == 'list':
            qs = qs.prefetch_related('wbs_nodes', 'required_units')

        if self.action == 'retrieve':
            # ⚡ Bolt: Add prefetch_related to avoid N+1 queries when loading nested WBS trees and roles
            qs = qs.prefetch_related('wbs_nodes__activities', 'template_roles__role', 'required_units')

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

        # Enforce target-project membership + edit_project (contracts/report-template-api.md)
        if not (request.user.is_superuser or request.user.groups.filter(name='admin').exists()):
            if not member_has_codename(request.user, project.id, 'edit_project'):
                return Response(
                    {'error': {'code': 'permission_denied', 'message': 'Project membership and edit_project permission required.', 'details': {}}},
                    status=status.HTTP_403_FORBIDDEN,
                )

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


def _can_manage_templates(request) -> bool:
    """Project-template-management permission (contract reporting-configuration
    catalog-api.md §4, Constitution IV): server-enforced, template-scoped.
    The template surface is global, so management is a global authority (the
    same authority the existing system-template guards already use).
    """
    user = request.user
    return bool(user and user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='admin').exists()
    ))


def _template_denied():
    return Response(
        {'error': {'code': 'permission_denied', 'message': 'Project template management permission required.', 'details': {}}},
        status=status.HTTP_403_FORBIDDEN,
    )


class LaborCatalogViewSet(viewsets.ViewSet):
    """Draft labor-title catalog CRUD on a project template (033 contract §1).

    Routes are nested under ``/project-templates/{pk}/labor-catalogs/`` and
    every lookup is template-scoped: a catalog id from another template
    resolves nothing (Constitution I).
    """

    permission_classes = [IsAuthenticated]
    pagination_class = None

    _create_serializer_error_template = 'labor_catalog_invalid'

    def _template(self, request, pk):
        template = get_object_or_404(ProjectTemplate, pk=pk)
        if not _can_manage_templates(request):
            raise PermissionDenied('Project template management permission required.')
        return template

    def _catalog(self, request, pk, catalog_pk):
        template = self._template(request, pk)
        return get_object_or_404(LaborTitleCatalog, pk=catalog_pk, template=template)

    def list(self, request, pk=None):
        template = self._template(request, pk)
        catalogs = (
            template.labor_catalogs.all()
            .prefetch_related('titles')
            .order_by('-created_at')
        )
        return Response(LaborTitleCatalogSerializer(catalogs, many=True).data)

    def create(self, request, pk=None):
        template = self._template(request, pk)
        serializer = LaborTitleCatalogCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        try:
            catalog = create_labor_catalog(
                template,
                version_name=data['version_name'],
                notes=data.get('notes', ''),
                titles=data.get('titles') or [],
            )
        except ValueError as exc:
            code, _, message = str(exc).partition(': ')
            return Response(
                {code if code else 'labor_catalog_invalid': message or str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            LaborTitleCatalogSerializer(catalog).data,
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, pk=None, catalog_pk=None):
        catalog = self._catalog(request, pk, catalog_pk)
        return Response(LaborTitleCatalogSerializer(catalog).data)

    def partial_update(self, request, pk=None, catalog_pk=None):
        catalog = self._catalog(request, pk, catalog_pk)
        serializer = LaborTitleCatalogCreateSerializer(
            data={**catalog_data_for_update(catalog), **request.data},
            partial=True,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        update_labor_catalog(
            catalog,
            version_name=data.get('version_name'),
            notes=data.get('notes'),
        )
        return Response(LaborTitleCatalogSerializer(catalog).data)


def catalog_data_for_update(catalog) -> dict:
    """Existing values supplied as fallback payload for partial updates."""
    return {'version_name': catalog.version_name, 'notes': catalog.notes}


class LaborCatalogTitleAPIView(APIView):
    """CRUD for title rows inside one catalog: ``…/labor-catalogs/{id}/titles/``."""

    permission_classes = [IsAuthenticated]
    pagination_class = None

    def _catalog(self, request, pk, catalog_pk):
        template = get_object_or_404(ProjectTemplate, pk=pk)
        if not _can_manage_templates(request):
            raise PermissionDenied('Project template management permission required.')
        return get_object_or_404(LaborTitleCatalog, pk=catalog_pk, template=template)

    def get(self, request, pk, catalog_pk):
        catalog = self._catalog(request, pk, catalog_pk)
        titles = catalog.titles.all().order_by('category', 'display_order', 'title_code')
        return Response(LaborTitleCatalogTitleSerializer(titles, many=True).data)

    def post(self, request, pk, catalog_pk):
        catalog = self._catalog(request, pk, catalog_pk)
        serializer = LaborTitleCatalogTitleSerializer(data=request.data, context={'catalog': catalog})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        title = serializer.save(catalog=catalog)
        return Response(LaborTitleCatalogTitleSerializer(title).data, status=status.HTTP_201_CREATED)


class LaborCatalogTitleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _title(self, request, pk, catalog_pk, title_pk):
        template = get_object_or_404(ProjectTemplate, pk=pk)
        if not _can_manage_templates(request):
            raise PermissionDenied('Project template management permission required.')
        catalog = get_object_or_404(LaborTitleCatalog, pk=catalog_pk, template=template)
        return get_object_or_404(LaborTitleCatalogTitle, pk=title_pk, catalog=catalog)

    def get(self, request, pk, catalog_pk, title_pk):
        title = self._title(request, pk, catalog_pk, title_pk)
        return Response(LaborTitleCatalogTitleSerializer(title).data)

    def put(self, request, pk, catalog_pk, title_pk):
        return self._update(request, pk, catalog_pk, title_pk, partial=False)

    def patch(self, request, pk, catalog_pk, title_pk):
        return self._update(request, pk, catalog_pk, title_pk, partial=True)

    def _update(self, request, pk, catalog_pk, title_pk, *, partial):
        title = self._title(request, pk, catalog_pk, title_pk)
        serializer = LaborTitleCatalogTitleSerializer(
            title, data=request.data, partial=partial, context={'catalog': title.catalog},
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if 'title_code' in serializer.validated_data:
            serializer.validated_data['title_code'] = serializer.validated_data['title_code']
        saved = serializer.save(catalog=title.catalog)
        return Response(LaborTitleCatalogTitleSerializer(saved).data)

    def delete(self, request, pk, catalog_pk, title_pk):
        title = self._title(request, pk, catalog_pk, title_pk)
        title.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectReportingConfigurationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def _get_project(self, request, project_id):
        return get_object_or_404(Project, pk=project_id)

    def _check_permission(self, request, project, codename: str):
        if not member_has_codename(request.user, project.id, codename):
            raise PermissionDenied(f'Permission {codename} required.')

    def list(self, request, project_id=None, project_pk=None):
        resolved_project_id = project_id or project_pk or self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        project = self._get_project(request, resolved_project_id)
        self._check_permission(request, project, 'view_reports')

        date_str = request.query_params.get('date')
        if date_str:
            config = (
                ProjectReportingConfiguration.objects.filter(
                    project=project,
                    effective_from__lte=date_str,
                )
                .prefetch_related('required_units', 'source_template')
                .order_by('-effective_from')
                .first()
            )
            if config is not None:
                return Response(ProjectReportingConfigurationSerializer(config).data)
            return Response(
                {
                    'state': 'configuration_incomplete',
                    'configuration': None,
                    'required_units': [],
                    'message_code': 'daily_report_template_required',
                },
                status=status.HTTP_200_OK,
            )

        configs = (
            ProjectReportingConfiguration.objects.filter(project=project)
            .prefetch_related('required_units', 'source_template')
            .order_by('-effective_from')
        )
        return Response(ProjectReportingConfigurationSerializer(configs, many=True).data)

    def create(self, request, project_id=None, project_pk=None):
        resolved_project_id = project_id or project_pk or self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        project = self._get_project(request, resolved_project_id)
        self._check_permission(request, project, 'edit_project')

        serializer = ProjectReportingConfigurationActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        template = get_object_or_404(ProjectTemplate, pk=data['template_id'])
        try:
            config = activate_project_reporting_configuration(
                project=project,
                template=template,
                effective_from=data['effective_from'],
                user=request.user,
                confirm_backdated=data.get('confirm_backdated', False),
                reason=data.get('reason', ''),
            )
        except ReportingConfigurationConflict as exc:
            return Response(
                {'error': {'code': exc.code, 'message': str(exc), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ProjectReportingConfigurationSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['post'], url_path='preview')
    def preview(self, request, project_id=None, project_pk=None):
        resolved_project_id = project_id or project_pk or self.kwargs.get('project_pk') or self.kwargs.get('project_id')
        project = self._get_project(request, resolved_project_id)
        self._check_permission(request, project, 'edit_project')

        serializer = ProjectReportingConfigurationPreviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        template = get_object_or_404(ProjectTemplate, pk=data['template_id'])
        preview_data = preview_project_reporting_configuration(
            project=project,
            template=template,
            effective_from=data['effective_from'],
        )
        return Response(preview_data, status=status.HTTP_200_OK)
