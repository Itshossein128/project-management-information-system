"""System-wide project role management (UI-15)."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from authentication.permissions import IsHrOrAdmin
from master_data.models import Role
from permissions.constants import PERMISSIONS
from permissions.role_services import is_system_role, set_role_permissions
from projects.role_serializers import (
    RoleCreateSerializer,
    RoleDetailSerializer,
    RolePermissionsSerializer,
    RoleUpdateSerializer,
)


@extend_schema_view(
    list=extend_schema(summary='List project roles', tags=['Roles']),
    create=extend_schema(summary='Create custom project role', tags=['Roles']),
    retrieve=extend_schema(summary='Get project role', tags=['Roles']),
    partial_update=extend_schema(summary='Update custom project role', tags=['Roles']),
    destroy=extend_schema(summary='Delete custom project role', tags=['Roles']),
)
class RoleViewSet(viewsets.ViewSet):
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsHrOrAdmin()]

    def _get_role(self, pk):
        return get_object_or_404(
            Role.objects.prefetch_related('role_permissions'),
            pk=pk,
        )

    def list(self, request):
        roles = Role.objects.prefetch_related('role_permissions').order_by('role_name')
        return Response(RoleDetailSerializer(roles, many=True).data)

    def create(self, request):
        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role = Role.objects.create(
            role_name=data['role_name'],
            description=data.get('description', ''),
        )
        if data.get('permissions'):
            set_role_permissions(role, data['permissions'])
        role = self._get_role(role.pk)
        return Response(RoleDetailSerializer(role).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        role = self._get_role(pk)
        return Response(RoleDetailSerializer(role).data)

    def partial_update(self, request, pk=None):
        role = self._get_role(pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System roles cannot be modified.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = RoleUpdateSerializer(data=request.data, partial=True, context={'role': role})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        if 'role_name' in data:
            role.role_name = data['role_name']
        if 'description' in data:
            role.description = data['description']
        role.save()
        role = self._get_role(role.pk)
        return Response(RoleDetailSerializer(role).data)

    def destroy(self, request, pk=None):
        role = self._get_role(pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System roles cannot be deleted.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(summary='Set permissions on custom role', tags=['Roles'])
    @action(detail=True, methods=['put', 'patch'], url_path='permissions')
    def permissions(self, request, pk=None):
        role = self._get_role(pk)
        if is_system_role(role):
            return Response(
                {'error': {'code': 'forbidden', 'message': 'System role permissions cannot be modified.', 'details': {}}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = RolePermissionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_role_permissions(role, serializer.validated_data['permissions'])
        role = self._get_role(role.pk)
        return Response(RoleDetailSerializer(role).data)


class PermissionCatalogView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary='List all project permission codenames', tags=['Roles'])
    def get(self, request):
        return Response(
            [
                {'codename': codename, 'label': label}
                for codename, label in sorted(PERMISSIONS.items())
            ],
        )
