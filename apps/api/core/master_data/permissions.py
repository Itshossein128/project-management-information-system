"""Write access for org-wide reference catalogs."""

from rest_framework import permissions

from authentication.permissions import IsBusinessSetup, IsHrOrAdmin


class IsOrgRefWriterOrReadOnly(permissions.BasePermission):
    """
    Organization units and managed contract types.

    Any authenticated user may read. Writes are limited to staff, superuser,
    and the groups that can open Organization references: admin, hr, and
    business-setup.
    """

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if IsHrOrAdmin().has_permission(request, view):
            return True
        return IsBusinessSetup().has_permission(request, view)
