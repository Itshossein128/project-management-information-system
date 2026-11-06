"""Project-local roles and recent access-change records."""

from datetime import datetime

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date, parse_datetime
from django.utils.translation import gettext as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from master_data.models import ProjectPosition, Role, RoleAccessChange
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from permissions.project import (
    ActiveMemberPermission,
    IsProjectMember,
    active_member_has_codename,
    has_organizational_observation,
)
from permissions.role_services import (
    RoleInUse,
    access_change_origin,
    assignment_impact,
    delete_custom_role,
    is_system_role,
    record_access_change,
    redact_history_payload,
    set_role_permissions,
)
from projects.models import Project
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


def _parse_bound(raw: str | None, *, end: bool):
    if not raw:
        return None
    parsed = parse_datetime(raw)
    if parsed is not None:
        return parsed
    day = parse_date(raw)
    if day is None:
        return None
    if end:
        return datetime.combine(day, datetime.max.time())
    return datetime.combine(day, datetime.min.time())


def _history_page(request):
    try:
        page = max(int(request.query_params.get('page') or 1), 1)
    except ValueError:
        page = 1
    try:
        page_size = int(request.query_params.get('page_size') or 50)
    except ValueError:
        page_size = 50
    return page, min(max(page_size, 1), 100)


def _history_queryset(request, queryset):
    subject = request.query_params.get('subject')
    actor = request.query_params.get('actor')
    since = _parse_bound(request.query_params.get('since'), end=False)
    until = _parse_bound(request.query_params.get('until'), end=True)
    if subject:
        queryset = queryset.filter(subject_user_id=subject)
    if actor:
        queryset = queryset.filter(actor_id=actor)
    if since is not None:
        queryset = queryset.filter(created_at__gte=since)
    if until is not None:
        queryset = queryset.filter(created_at__lte=until)
    return queryset


def _history_name_lookups(rows):
    role_ids = set()
    position_ids = set()
    for row in rows:
        for payload in (row.before or {}, row.after or {}):
            if not isinstance(payload, dict):
                continue
            role_ids.update(str(item) for item in payload.get('role_ids') or [])
            position_ids.update(str(item) for item in payload.get('position_ids') or [])
    roles = {
        str(item.id): item.role_name
        for item in Role.objects.filter(id__in=role_ids)
    } if role_ids else {}
    positions = {
        str(item.id): item.position_name
        for item in ProjectPosition.objects.filter(id__in=position_ids)
    } if position_ids else {}
    return roles, positions


def _with_display_names(payload, roles, positions):
    named = dict(payload)
    role_ids = named.get('role_ids')
    if isinstance(role_ids, list):
        named['role_names'] = [roles.get(str(item), str(item)) for item in role_ids]
    position_ids = named.get('position_ids')
    if isinstance(position_ids, list):
        named['position_names'] = [positions.get(str(item), str(item)) for item in position_ids]
    return named


def _serialize_change(row, roles=None, positions=None) -> dict:
    roles = roles or {}
    positions = positions or {}
    before = _with_display_names(redact_history_payload(row.before or {}), roles, positions)
    after = _with_display_names(redact_history_payload(row.after or {}), roles, positions)
    unknown = []
    if row.actor_id is None and row.action not in {'login_succeeded', 'recovery_requested'}:
        unknown.append('actor')
    return {
        'id': str(row.id),
        'action': row.action,
        'origin': access_change_origin(row.action),
        'role_name': row.role_name,
        'actor_name': row.actor.full_name if row.actor_id else '',
        'subject_name': (
            row.subject_user.full_name if row.subject_user_id
            else (after or {}).get('invited_email')
            or (after or {}).get('invited_mobile')
            or ''
        ),
        'project_id': str(row.project_id) if row.project_id else None,
        'before': before,
        'after': after,
        'unknown': unknown,
        'created_at': row.created_at.isoformat(),
    }


def _paged_history(request, queryset):
    page, page_size = _history_page(request)
    queryset = _history_queryset(request, queryset).select_related('actor', 'subject_user')
    count = queryset.count()
    start = (page - 1) * page_size
    rows = list(queryset.order_by('-created_at')[start:start + page_size])
    roles, positions = _history_name_lookups(rows)
    return Response({
        'count': count,
        'page': page,
        'page_size': page_size,
        'results': [_serialize_change(row, roles, positions) for row in rows],
    })


class ProjectAccessChangeListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Role and permission changes in this project', tags=['Project roles'])
    def get(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        allowed = active_member_has_codename(request.user, project.id, 'manage_members')
        if not allowed and not has_organizational_observation(request.user):
            return Response(
                {'error': {'code': 'forbidden', 'message': _('You cannot view this access history.'), 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        return _paged_history(request, RoleAccessChange.objects.filter(project_id=project.id))


class OrganizationAccessChangeListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Organization access history, including global role changes', tags=['Project roles'])
    def get(self, request):
        if not has_organizational_observation(request.user):
            return Response(
                {'error': {'code': 'forbidden', 'message': _('You cannot view this access history.'), 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = RoleAccessChange.objects.all()
        project_filter = request.query_params.get('project')
        if project_filter:
            queryset = queryset.filter(project_id=project_filter)
        return _paged_history(request, queryset)
