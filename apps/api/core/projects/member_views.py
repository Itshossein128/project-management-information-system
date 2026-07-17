"""Project member management APIs (Sprint 2 C-01)."""
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from master_data.models import MemberStatus, ProjectMember, Role
from permissions.project import HasProjectPermission, IsProjectMember
from permissions.services import set_permission_override
from projects.member_serializers import (
    EffectivePermissionsSerializer,
    PermissionOverrideSerializer,
    ProjectMemberCreateSerializer,
    ProjectMemberListSerializer,
    ProjectMemberUpdateSerializer,
    RoleSerializer,
)
from projects.services import assign_roles_to_member

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
            # GET: any project member; POST/DELETE: manage_members required
            if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
                return [IsAuthenticated(), IsProjectMember()]
            return [IsAuthenticated(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        return 'manage_members'

    def _get_project_id(self):
        return self.kwargs['project_pk']

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
            .prefetch_related('member_roles__role')
            .order_by('-joined_at')
        )
        return Response(ProjectMemberListSerializer(members, many=True).data)

    def create(self, request, project_pk=None):
        serializer = ProjectMemberCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role_ids = data['role_ids']

        user_id = data.get('user_id')
        email = (data.get('email') or '').strip()

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            if ProjectMember.objects.filter(project_id=project_pk, user=user).exists():
                return Response(
                    {'error': {'code': 'validation_error', 'message': 'User is already a member.', 'details': {}}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            member = ProjectMember.objects.create(
                project_id=project_pk,
                user=user,
                status=MemberStatus.ACTIVE,
            )
        else:
            if ProjectMember.objects.filter(
                project_id=project_pk,
                invited_email__iexact=email,
                status=MemberStatus.INVITED,
            ).exists():
                return Response(
                    {'error': {'code': 'validation_error', 'message': 'Invitation already sent.', 'details': {}}},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            member = ProjectMember.objects.create(
                project_id=project_pk,
                user=None,
                invited_email=email,
                status=MemberStatus.INVITED,
            )

        assign_roles_to_member(member, role_ids)
        return Response(ProjectMemberListSerializer(member).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, project_pk=None, user_id=None):
        member = self._get_member_by_user(user_id)
        serializer = ProjectMemberUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if 'role_ids' in data:
            assign_roles_to_member(member, data['role_ids'])
        if 'status' in data:
            member.status = data['status']
            member.save(update_fields=['status'])

        member.refresh_from_db()
        return Response(ProjectMemberListSerializer(member).data)

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
            set_permission_override(member, codename, None)
            member = self._get_member_by_user(user_id)
            return Response(EffectivePermissionsSerializer.from_member(member))

        serializer = PermissionOverrideSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_permission_override(
            member,
            serializer.validated_data['permission_codename'],
            serializer.validated_data['is_granted'],
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
    """Search users by name or email for member invitation."""

    permission_classes = [IsAuthenticated]

    @extend_schema(summary='Search users for member assignment', tags=['Project members'])
    def get(self, request):
        q = (request.query_params.get('q') or request.query_params.get('search') or '').strip()
        if len(q) < 2:
            return Response([])

        users = User.objects.filter(
            Q(full_name__icontains=q)
            | Q(email__icontains=q)
            | Q(mobile__icontains=q)
            | Q(username__icontains=q)
        ).order_by('full_name')[:20]

        results = [
            {
                'user_id': str(u.id),
                'full_name': u.full_name,
                'email': u.email or '',
                'mobile': u.mobile or '',
            }
            for u in users
        ]
        return Response(results)
