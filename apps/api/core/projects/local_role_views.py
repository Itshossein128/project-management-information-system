"""Project-local roles and recent access-change records."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from master_data.models import Role, RoleAccessChange
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from permissions.project import ActiveMemberPermission, IsProjectMember
from permissions.role_services import (
    RoleInUse,
    assignment_impact,
    delete_custom_role,
    is_system_role,
    record_access_change,
    set_role_permissions,
)
from projects.role_serializers import (
    RoleCreateSerializer,
    RoleDetailSerializer,
    RolePermissionsSerializer,
    RoleUpdateSerializer,
)


def _project_id(view) -> str:
    return str(view.kwargs['project_pk'])


@extend_schema_view(
    list=extend_schema(summary='List roles assignable in this project', tags=['Project roles']),
    create=extend_schema(summary='Create a role local to this project', tags=['Project roles']),
    partial_update=extend_schema(summary='Update a local role', tags=['Project roles']),
    destroy=extend_schema(summary='Delete a local custom role', tags=['Project roles']),
)
class LocalRoleViewSet(viewsets.ViewSet):
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action in ('list', 'impact'):
            return [IsAuthenticated(), IsProjectMember()]
        return [IsAuthenticated(), ActiveMemberPermission()]

    def _local_role(self, pk, project_id):
        return get_object_or_404(
            Role.objects.filter(project_id=project_id).prefetch_related('role_permissions'),
            pk=pk,
        )

    def list(self, request, project_pk=None):
        roles = Role.objects.filter(
            Q(project_id=project_pk) | Q(project_id__isnull=True),
        ).prefetch_related('role_permissions').order_by('role_name')
        return Response(RoleDetailSerializer(roles, many=True).data)

    def create(self, request, project_pk=None):
        from projects.models import Project

        project = get_object_or_404(Project, pk=project_pk)
        serializer = RoleCreateSerializer(data=request.data, context={'project': project})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if data['role_name'] in DEFAULT_ROLE_PERMISSIONS:
            return Response(
                {
                    'error': {
                        'code': 'forbidden',
                        'message': _('Built-in role names cannot be reused for a project role.'),
                        'details': {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        role = Role.objects.create(
            role_name=data['role_name'],
            description=data.get('description', ''),
            project_id=project_pk,
        )
        if data.get('permissions'):
            set_role_permissions(role, data['permissions'], actor=request.user)
        record_access_change(
            actor=request.user,
            project=project,
            subject_user=None,
            role=role,
            action='role_created',
            before={},
            after={'role_name': role.role_name, 'description': role.description},
        )
        role = self._local_role(role.pk, project_pk)
        return Response(RoleDetailSerializer(role).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, project_pk=None, pk=None):
        role = self._local_role(pk, project_pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System roles cannot be modified.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = RoleUpdateSerializer(data=request.data, partial=True, context={'role': role})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        before = {'role_name': role.role_name, 'description': role.description}
        if 'role_name' in data:
            role.role_name = data['role_name']
        if 'description' in data:
            role.description = data['description']
        role.save()
        after = {'role_name': role.role_name, 'description': role.description}
        if before != after:
            record_access_change(
                actor=request.user,
                project=role.project,
                subject_user=None,
                role=role,
                action='role_renamed',
                before=before,
                after=after,
            )
        return Response(RoleDetailSerializer(self._local_role(role.pk, project_pk)).data)

    def destroy(self, request, project_pk=None, pk=None):
        role = self._local_role(pk, project_pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System roles cannot be deleted.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            delete_custom_role(role, actor=request.user)
        except RoleInUse as exc:
            scoped = assignment_impact(role, project_id=project_pk)
            return Response(
                {
                    'error': {
                        'code': 'role_in_use',
                        'message': _('This role is still assigned and was not deleted.'),
                        'details': scoped or exc.impact,
                    },
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='impact')
    def impact(self, request, project_pk=None, pk=None):
        role = self._local_role(pk, project_pk)
        return Response(assignment_impact(role, project_id=project_pk))

    @action(detail=True, methods=['put', 'patch'], url_path='permissions')
    def permissions(self, request, project_pk=None, pk=None):
        role = self._local_role(pk, project_pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System role permissions cannot be modified.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = RolePermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_role_permissions(role, serializer.validated_data['permissions'], actor=request.user)
        return Response(RoleDetailSerializer(self._local_role(role.pk, project_pk)).data)


class ProjectAccessChangeListView(APIView):
    permission_classes = [IsAuthenticated, ActiveMemberPermission]

    @extend_schema(summary='Recent role and permission changes in this project', tags=['Project roles'])
    def get(self, request, project_pk=None):
        rows = RoleAccessChange.objects.filter(project_id=project_pk).select_related(
            'actor',
            'subject_user',
        )[:50]
        return Response(
            [
                {
                    'id': str(row.id),
                    'action': row.action,
                    'role_name': row.role_name,
                    'actor_name': row.actor.full_name if row.actor_id else '',
                    'subject_name': (
                        row.subject_user.full_name if row.subject_user_id
                        else (row.after or {}).get('invited_email')
                        or (row.after or {}).get('invited_mobile')
                        or ''
                    ),
                    'before': row.before,
                    'after': row.after,
                    'created_at': row.created_at.isoformat(),
                }
                for row in rows
            ],
        )
