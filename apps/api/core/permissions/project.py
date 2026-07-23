from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from master_data.models import ProjectMember


def _is_global_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='admin').exists()


def _get_project_id(request, view) -> str | None:
    project_id = getattr(request, 'project_id', None)
    if project_id is not None:
        return str(project_id)
    for key in ('project_pk', 'project_id'):
        if key in view.kwargs:
            return str(view.kwargs[key])
    return None


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
