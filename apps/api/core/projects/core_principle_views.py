"""API views for FR-CORE capability toggles and fiscal period locks."""
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions.project import HasProjectPermission, IsProjectMember
from projects.capability_service import list_capability_settings, update_capability_setting
from projects.fiscal_service import create_fiscal_lock, deactivate_fiscal_lock
from projects.models import FiscalPeriodLock, Project, ProjectCapabilitySetting
from projects.serializers import (
    FiscalPeriodLockSerializer,
    ProjectCapabilitySettingSerializer,
)


class ProjectCapabilityListView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'view_project'

    @extend_schema(summary='List project capability settings', tags=['Core Principles'])
    def get(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        settings_list = list_capability_settings(project, request.user)
        return Response(ProjectCapabilitySettingSerializer(settings_list, many=True).data)


class ProjectCapabilityDetailView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_project'

    @extend_schema(summary='Update project capability setting', tags=['Core Principles'])
    def patch(self, request, project_pk=None, capability_key=None):
        project = get_object_or_404(Project, pk=project_pk)
        setting = update_capability_setting(
            project,
            capability_key,
            enabled=request.data.get('enabled'),
            mode=request.data.get('mode'),
            user=request.user,
        )
        return Response(ProjectCapabilitySettingSerializer(setting).data)

    def put(self, request, project_pk=None, capability_key=None):
        return self.patch(request, project_pk=project_pk, capability_key=capability_key)


class FiscalPeriodLockListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]

    @property
    def required_permission(self):
        if self.request.method == 'GET':
            return 'view_project'
        return 'edit_project'

    @extend_schema(summary='List fiscal period locks', tags=['Core Principles'])
    def get(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        locks = FiscalPeriodLock.objects.filter(project=project)
        return Response(FiscalPeriodLockSerializer(locks, many=True).data)

    @extend_schema(summary='Close a fiscal period', tags=['Core Principles'])
    def post(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = FiscalPeriodLockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        lock = create_fiscal_lock(
            project=project,
            period_start=data['period_start'],
            period_end=data['period_end'],
            reason=data['reason'],
            user=request.user,
        )
        return Response(FiscalPeriodLockSerializer(lock).data, status=status.HTTP_201_CREATED)


class FiscalPeriodLockDeactivateView(APIView):
    permission_classes = [IsAuthenticated, IsProjectMember, HasProjectPermission]
    required_permission = 'edit_project'

    @extend_schema(summary='Deactivate a fiscal period lock', tags=['Core Principles'])
    def post(self, request, project_pk=None, lock_id=None):
        project = get_object_or_404(Project, pk=project_pk)
        lock = get_object_or_404(FiscalPeriodLock, pk=lock_id, project=project)
        deactivate_fiscal_lock(lock, user=request.user, reason=request.data.get('reason', ''))
        return Response(FiscalPeriodLockSerializer(lock).data)
