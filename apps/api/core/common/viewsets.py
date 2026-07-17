"""Shared ViewSet mixins for project-scoped form APIs."""
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from permissions.project import HasProjectPermission, IsProjectMember


class ProjectScopedViewSet(viewsets.ModelViewSet):
    """Base ViewSet: project tenancy, permissions, audit, soft delete."""

    lookup_url_kwarg = 'pk'
    view_permission = 'view_reports'
    edit_permission = 'edit_reports'

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated(), IsProjectMember(), HasProjectPermission()]
        return [IsAuthenticated(), HasProjectPermission()]

    @property
    def required_permission(self):
        if self.action in ('list', 'retrieve'):
            return self.view_permission
        return self.edit_permission

    def get_project_id(self):
        return self.kwargs['project_pk']

    def get_queryset(self):
        return self.queryset.filter(project_id=self.get_project_id())

    def post_save(self, instance):
        pass

    def post_delete(self, instance):
        pass

    def perform_create(self, serializer):
        serializer.save(
            project_id=self.get_project_id(),
            created_by=self.request.user,
            updated_by=self.request.user,
        )
        self.post_save(serializer.instance)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        self.post_save(serializer.instance)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.updated_by = request.user
        instance.save(update_fields=['is_deleted', 'deleted_at', 'updated_by', 'updated_at'])
        self.post_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
