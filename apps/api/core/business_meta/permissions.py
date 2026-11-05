"""
Permissions for project-scoped assignment and position APIs.
"""
from rest_framework import permissions

from authentication.permissions import IsHrOrAdmin
from master_data.models import ProjectMember
from permissions.project import _get_active_member, has_organizational_observation


class IsHrOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return IsHrOrAdmin().has_permission(request, view)


class CanViewProjectMembers(permissions.BasePermission):
    """Reads require an active membership or the named observation exception.

    Unsafe methods keep the previous shortcut so non-position callers that still
    use this class for writes are not redesigned in this phase. Position writes
    do not use this class.
    """

    def _legacy_write_allowed(self, user, project_id) -> bool:
        if user.is_superuser or user.is_staff:
            return True
        if user.groups.filter(name__in=('admin', 'hr', 'business-setup')).exists():
            return True
        if not project_id:
            return True
        return ProjectMember.objects.filter(project_id=project_id, user_id=user.id).exists()

    def _read_allowed(self, user, project_id) -> bool:
        if has_organizational_observation(user):
            return True
        if not project_id:
            return True
        return _get_active_member(user, project_id) is not None

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        project_id = view.kwargs.get('project_pk')
        if request.method not in permissions.SAFE_METHODS:
            return self._legacy_write_allowed(request.user, project_id)
        return self._read_allowed(request.user, project_id)

    def has_object_permission(self, request, view, obj) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        project_id = getattr(obj, 'project_id', None)
        if request.method not in permissions.SAFE_METHODS:
            return self._legacy_write_allowed(request.user, project_id)
        return self._read_allowed(request.user, project_id)


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
