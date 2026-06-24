"""
Permissions for business-scoped assignment and job position APIs.
"""
from rest_framework import permissions

from authentication.permissions import IsHrOrAdmin


class IsHrOrAdminOrReadOnly(permissions.BasePermission):
    """
    Read (safe methods) for authenticated users who may view business data.
    Write for HR, admin, staff, or superuser (IsHrOrAdmin).
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return IsHrOrAdmin().has_permission(request, view)


class CanViewBusinessAssignments(permissions.BasePermission):
    """
    List/retrieve assignments for a business: HR/admin/staff/superuser,
    or any user with an assignment in that business, or `visitor` (read-only in combination with safe method).
    """
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        u = request.user
        if u.is_superuser or u.is_staff:
            return True
        if u.groups.filter(name__in=('admin', 'hr')).exists():
            return True
        if u.groups.filter(name='business-setup').exists():
            return True
        business_id = view.kwargs.get('business_pk')
        if not business_id:
            return True
        from business_meta.models import UserBusinessAssignment
        return UserBusinessAssignment.objects.filter(
            business_id=business_id,
            user_id=u.id,
        ).exists()

    def has_object_permission(self, request, view, obj) -> bool:
        u = request.user
        if u.is_superuser or u.is_staff or u.groups.filter(
            name__in=('admin', 'hr', 'business-setup')
        ).exists():
            return True
        from business_meta.models import UserBusinessAssignment
        return UserBusinessAssignment.objects.filter(
            business_id=obj.business_id,
            user_id=u.id,
        ).exists()


class IsVisitorReadOnly(permissions.BasePermission):
    """
    Users in the `visitor` group may not use unsafe HTTP methods.
    """
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


def assignment_view_permissions():
    """
    For ViewSet: safe methods need CanViewBusinessAssignments + IsVisitorReadOnly; unsafe need IsHrOrAdmin + IsVisitorReadOnly.
    """
    from rest_framework.permissions import IsAuthenticated
    return [IsAuthenticated, CanViewBusinessAssignments, IsVisitorReadOnly, IsHrOrAdmin]


# Expose a getter used from get_permissions that branches on method
