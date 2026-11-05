from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from master_data.models import ProjectMember


def _is_global_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='admin').exists()


def has_organizational_observation(user) -> bool:
    """Read-only project observation for superuser or the admin group.

    The staff flag and the hr group do not qualify. This does not grant writes.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='admin').exists()


def active_member_has_codename(user, project_id, codename: str) -> bool:
    """Project permission that never treats a global admin as a writer."""
    member = _get_active_member(user, project_id)
    if member is None:
        return False
    return member.has_permission(codename)


def _get_project_id(request, view) -> str | None:
    project_id = getattr(request, 'project_id', None)
    if project_id is not None:
        return str(project_id)
    for key in ('project_pk', 'project_id'):
        if key in view.kwargs:
            return str(view.kwargs[key])
    return None


def member_has_codename(user, project_id, codename: str) -> bool:
    """True if user has project-scoped permission codename (roles + overrides)."""
    if _is_global_admin(user):
        return True
    member = _get_active_member(user, project_id)
    if member is None:
        return False
    return member.has_permission(codename)


def _get_active_member(user, project_id):
    if not user or not user.is_authenticated or not project_id:
        return None
    return (
        ProjectMember.objects.filter(
            project_id=project_id,
            user_id=user.id,
            status='active',
        )
        .prefetch_related(
            'member_roles__role__role_permissions',
            'permission_overrides',
        )
        .first()
    )


class IsProjectMember(BasePermission):
    message = _('You are not an active member of this project.')

    def has_permission(self, request, view):
        project_id = _get_project_id(request, view)
        if not project_id:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_global_admin(request.user):
            return True
        return _get_active_member(request.user, project_id) is not None

    def has_object_permission(self, request, view, obj):
        project_id = getattr(obj, 'project_id', None)
        if project_id is None and hasattr(obj, 'project'):
            project_id = obj.project_id
        if project_id is None:
            return True
        if _is_global_admin(request.user):
            return True
        return _get_active_member(request.user, str(project_id)) is not None


class ActiveMemberPermission(BasePermission):
    """Selected-path write check. Does not use the global-admin bypass."""

    codename = 'manage_members'
    message = _('You do not have permission to perform this action.')

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        project_id = _get_project_id(request, view)
        if not project_id:
            return False
        codename = self.codename or getattr(view, 'required_permission', '')
        if not codename:
            return False
        return active_member_has_codename(request.user, project_id, codename)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class HasProjectPermission(BasePermission):
    """Check project-scoped permission via roles and member overrides."""

    required_permission: str = ''

    def has_permission(self, request, view):
        permission = getattr(view, 'required_permission', None) or self.required_permission
        if not permission:
            return False

        project_id = _get_project_id(request, view)
        if not project_id:
            return False
        if not request.user or not request.user.is_authenticated:
            return False
        if _is_global_admin(request.user):
            return True

        member = _get_active_member(request.user, project_id)
        if member is None:
            return False
        return member.has_permission(permission)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
