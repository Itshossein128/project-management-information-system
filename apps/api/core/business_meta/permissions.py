"""
Permissions for project-scoped assignment and position APIs.
"""
from rest_framework import permissions

from authentication.permissions import IsHrOrAdmin
from master_data.models import ProjectMember


class IsHrOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return IsHrOrAdmin().has_permission(request, view)


class CanViewProjectMembers(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        u = request.user
        if u.is_superuser or u.is_staff:
            return True
        if u.groups.filter(name__in=('admin', 'hr', 'business-setup')).exists():
            return True
        project_id = view.kwargs.get('project_pk')
        if not project_id:
            return True
        return ProjectMember.objects.filter(project_id=project_id, user_id=u.id).exists()

    def has_object_permission(self, request, view, obj) -> bool:
        u = request.user
        if u.is_superuser or u.is_staff or u.groups.filter(
            name__in=('admin', 'hr', 'business-setup')
        ).exists():
            return True
        project_id = getattr(obj, 'project_id', None)
        return ProjectMember.objects.filter(project_id=project_id, user_id=u.id).exists()


# Backward-compatible alias
CanViewBusinessAssignments = CanViewProjectMembers


class IsVisitorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        u = request.user
        if u.groups.filter(name='visitor').exists() and not u.groups.filter(
            name__in=('admin', 'hr')
        ).exists():
            return False
        return True
