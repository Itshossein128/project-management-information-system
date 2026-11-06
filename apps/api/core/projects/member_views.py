"""Project member management APIs (Sprint 2 C-01)."""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from master_data.models import ProjectMember, Role
from permissions.project import ActiveMemberPermission, IsProjectMember
from permissions.services import set_permission_override
from projects.member_serializers import (
    EffectivePermissionsSerializer,
    PermissionOverrideSerializer,
    ProjectMemberCreateSerializer,
    ProjectMemberListSerializer,
    ProjectMemberUpdateSerializer,
    RoleSerializer,
)
from projects.services import (
    AlreadyMember,
    InvitationInvalid,
    PositionSelectionError,
    RoleProjectMismatch,
    UnknownRoles,
    assign_roles_to_member,
    cancel_invitation,
    change_member_status,
    connect_invitation,
    create_project_member,
    missing_role_ids,
    replace_member_positions,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(summary='List project members', tags=['Project members']),
    create=extend_schema(summary='Add project member', tags=['Project members']),
    partial_update=extend_schema(summary='Update member roles/status', tags=['Project members']),
)
class ProjectMemberViewSet(viewsets.ViewSet):
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), IsProjectMember()]
        if self.action == 'permissions':
            # GET: any project member; POST/DELETE: active manage_members, no global bypass
            if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
                return [IsAuthenticated(), IsProjectMember()]
            return [IsAuthenticated(), ActiveMemberPermission()]
        return [IsAuthenticated(), ActiveMemberPermission()]

    @property
    def required_permission(self):
        return 'manage_members'

    def _get_project_id(self):
        return self.kwargs['project_pk']

    def _unknown_role_response(self, missing):
        return Response(
            {
                'error': {
                    'code': 'unknown_role',
                    'message': _('One or more selected roles do not exist.'),
                    'details': {'role_ids': [str(item) for item in missing]},
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _get_member_by_user(self, user_id):
        return get_object_or_404(
            ProjectMember.objects.select_related('user').prefetch_related(
                'member_roles__role',
                'permission_overrides',
            ),
            project_id=self._get_project_id(),
            user_id=user_id,
        )

    def list(self, request, project_pk=None):
        members = (
            ProjectMember.objects.filter(project_id=project_pk)
            .select_related('user')
            .prefetch_related('member_roles__role', 'positions')
            .order_by('-joined_at')
        )
        return Response(
            ProjectMemberListSerializer(
                members,
                many=True,
                context={'request': request, 'view': self},
            ).data
        )

    def _already_member_response(self):
        return Response(
            {
                'error': {
                    'code': 'already_member',
                    'message': _('This person already has a membership in this project.'),
                    'details': {},
                },
            },
            status=status.HTTP_409_CONFLICT,
        )

    def create(self, request, project_pk=None):
        missing = missing_role_ids((request.data or {}).get('role_ids') or [])
        if missing:
            return self._unknown_role_response(missing)
        serializer = ProjectMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_id = data.get('user_id')
        if user_id and not User.objects.filter(pk=user_id).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            member = create_project_member(
                project_id=project_pk,
                actor=request.user,
                user_id=user_id,
                email=data.get('email') or '',
                mobile=data.get('mobile') or '',
                role_ids=data['role_ids'],
                position_ids=data.get('position_ids') or [],
            )
        except AlreadyMember:
            return self._already_member_response()
        except UnknownRoles as exc:
            return self._unknown_role_response(exc.missing_ids)
        except RoleProjectMismatch as exc:
            return Response(
                {
                    'error': {
                        'code': 'role_project_mismatch',
                        'message': _('This role does not belong to this project.'),
                        'details': {'role_ids': [str(item) for item in exc.role_ids]},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PositionSelectionError as exc:
            return Response(
                {
                    'error': {
                        'code': 'position_not_selectable',
                        'message': _('One or more job titles cannot be selected for this project.'),
                        'details': {'position_ids': [str(item) for item in exc.position_ids]},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            ProjectMemberListSerializer(member, context={'request': request, 'view': self}).data,
            status=status.HTTP_201_CREATED,
        )

    def connect_invitation(self, request, project_pk=None, member_id=None):
        user_id = (request.data or {}).get('user_id')
        if not user_id or not User.objects.filter(pk=user_id).exists():
            return Response(
                {'error': {'code': 'validation_error', 'message': _('A person is required.'), 'details': {}}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            member = connect_invitation(
                project_id=project_pk,
                member_id=member_id,
                user_id=user_id,
                actor=request.user,
                role_ids=(request.data or {}).get('role_ids'),
                position_ids=(request.data or {}).get('position_ids'),
            )
        except ProjectMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except InvitationInvalid:
            return Response(
                {
                    'error': {
                        'code': 'invitation_invalid',
                        'message': _('This invitation can no longer be used.'),
                        'details': {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AlreadyMember:
            return self._already_member_response()
        return Response(ProjectMemberListSerializer(member, context={'request': request, 'view': self}).data)

    def cancel_invitation(self, request, project_pk=None, member_id=None):
        try:
            member = cancel_invitation(project_id=project_pk, member_id=member_id, actor=request.user)
        except ProjectMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except InvitationInvalid:
            return Response(
                {
                    'error': {
                        'code': 'invitation_invalid',
                        'message': _('This invitation can no longer be used.'),
                        'details': {},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(ProjectMemberListSerializer(member, context={'request': request, 'view': self}).data)

    def partial_update(self, request, project_pk=None, user_id=None):
        member = self._get_member_by_user(user_id)
        raw_roles = (request.data or {}).get('role_ids', None)
        if raw_roles is not None:
            missing = missing_role_ids(raw_roles)
            if missing:
                return self._unknown_role_response(missing)
        serializer = ProjectMemberUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            with transaction.atomic():
                if 'role_ids' in data:
                    assign_roles_to_member(member, data['role_ids'], actor=request.user)
                if 'position_ids' in data:
                    replace_member_positions(member, data['position_ids'], actor=request.user)
                if 'status' in data:
                    change_member_status(member, data['status'], request.user)
        except UnknownRoles as exc:
            return self._unknown_role_response(exc.missing_ids)
        except RoleProjectMismatch as exc:
            return Response(
                {
                    'error': {
                        'code': 'role_project_mismatch',
                        'message': _('This role does not belong to this project.'),
                        'details': {'role_ids': [str(item) for item in exc.role_ids]},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PositionSelectionError as exc:
            return Response(
                {
                    'error': {
                        'code': 'position_not_selectable',
                        'message': _('One or more job titles cannot be selected for this project.'),
                        'details': {'position_ids': [str(item) for item in exc.position_ids]},
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        member.refresh_from_db()
        return Response(ProjectMemberListSerializer(member, context={'request': request, 'view': self}).data)

    @extend_schema(summary='Get member effective permissions', tags=['Project members'])
    @action(detail=True, methods=['get', 'post', 'delete'], url_path='permissions')
    def permissions(self, request, project_pk=None, user_id=None):
        member = self._get_member_by_user(user_id)
        if request.method == 'GET':
            return Response(EffectivePermissionsSerializer.from_member(member))

        if request.method == 'DELETE':
            codename = (request.query_params.get('permission_codename') or '').strip()
            if not codename:
                return Response(
                    {'error': {'code': 'validation_error', 'message': 'permission_codename is required.', 'details': {}}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            set_permission_override(member, codename, None, actor=request.user)
            member = self._get_member_by_user(user_id)
            return Response(EffectivePermissionsSerializer.from_member(member))

        serializer = PermissionOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_permission_override(
            member,
            serializer.validated_data['permission_codename'],
            serializer.validated_data['is_granted'],
            actor=request.user,
        )
        member = self._get_member_by_user(user_id)
        return Response(EffectivePermissionsSerializer.from_member(member))


class RoleListView(APIView):
    """Deprecated: use RoleViewSet at /api/v1/roles/. Kept for import compatibility."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List project roles', tags=['Project members'])
    def get(self, request):
        from projects.role_views import RoleViewSet

        return RoleViewSet().list(request)


class UserLookupView(APIView):
    """Search users by name for member invitation (A6-P4 person-directory policy)."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Search users for member assignment', tags=['Project members'])
    def get(self, request):
        from permissions.project import active_member_has_codename

        from authentication.permissions import IsOrganizationalAccountAdmin

        project_id = (
            request.query_params.get('project_id')
            or request.query_params.get('project')
            or ''
        ).strip()
        is_account_admin = IsOrganizationalAccountAdmin().has_permission(request, self)
        if project_id:
            if not active_member_has_codename(request.user, project_id, 'manage_members'):
                return Response(
                    {
                        'error': {
                            'code': 'permission_denied',
                            'message': _(
                                'You do not have permission to search people for this project.'
                            ),
                            'details': {},
                        }
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            can_see_contacts = active_member_has_codename(
                request.user, project_id, 'view_person_contacts'
            )
        elif is_account_admin:
            # Full organization directory search for explicit account administrators.
            can_see_contacts = True
        else:
            return Response(
                {
                    'error': {
                        'code': 'permission_denied',
                        'message': _('You do not have permission to search people.'),
                        'details': {},
                    }
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        q = (request.query_params.get('q') or request.query_params.get('search') or '').strip()
        if len(q) < 2:
            return Response([])

        base_q = (
            Q(full_name__icontains=q)
            | Q(username__icontains=q)
        )
        if can_see_contacts:
            base_q |= Q(email__icontains=q) | Q(mobile__icontains=q)
        users = User.objects.filter(base_q).order_by('full_name')[:20]
        results = []
        for u in users:
            row = {
                'user_id': str(u.id),
                'full_name': u.full_name,
            }
            if can_see_contacts:
                row['email'] = u.email or ''
                row['mobile'] = u.mobile or ''
            elif getattr(u, 'organization', None):
                # Non-sensitive disambiguator for duplicate display names.
                row['organization_label'] = u.organization
            results.append(row)
        return Response(results)
