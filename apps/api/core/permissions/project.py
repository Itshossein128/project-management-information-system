from rest_framework.permissions import SAFE_METHODS, BasePermission
from django.utils.translation import gettext_lazy as _

from config.exceptions import CodedValidationError
from master_data.models import ProjectMember


def _is_global_admin(user) -> bool:
    """Legacy helper. Prefer observation for reads and active_member_has_codename for writes.

    Remaining write callers are inventoried for A6-P4 replacement. Do not use this
    to grant project mutations or sensitive fields.
    """
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name='admin').exists()


def has_organizational_observation(user) -> bool:
    """Read-only project observation for superuser or the admin group.

    The staff flag and the hr group do not qualify. This does not grant writes,
    wages, person or stakeholder contacts, confidential files, or SoD break-glass.
    A6-P4 does not expand this exception.
    """
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='admin').exists()


def assert_same_project(request_project_id, related_project_id, *, field: str = 'project') -> None:
    """Reject related object ids whose project differs from the request project.

    Fail closed: if the related row is tied to a project but the request context
    has no project id, treat as a scope error (prevents ambiguous cross-project binds).
    """
    if related_project_id is None:
        return
    if request_project_id is None:
        raise CodedValidationError(
            detail=_('The related object does not belong to this project.'),
            code='project_scope_mismatch',
        )
    if str(request_project_id) != str(related_project_id):
        raise CodedValidationError(
            detail=_('The related object does not belong to this project.'),
            code='project_scope_mismatch',
        )


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
    """True if user has project-scoped permission codename (roles + overrides).

    Organizational observation does not satisfy write or sensitive codenames.
    Prefer ``active_member_has_codename`` for mutations.
    """
    return active_member_has_codename(user, project_id, codename)


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


def _get_any_member(user, project_id):
    """Membership row for user+project regardless of status (read paths only)."""
    if not user or not user.is_authenticated or not project_id:
        return None
    return (
        ProjectMember.objects.filter(project_id=project_id, user_id=user.id)
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
        if request.method in SAFE_METHODS and has_organizational_observation(request.user):
            return True
        if _get_active_member(request.user, project_id) is not None:
            return True
        # Inactive/suspended members may read their own effective-permissions snapshot (empty grants).
        if request.method in SAFE_METHODS:
            target_user_id = view.kwargs.get('user_id') or view.kwargs.get('pk')
            if target_user_id and str(request.user.id) == str(target_user_id):
                return _get_any_member(request.user, project_id) is not None
        return False

    def has_object_permission(self, request, view, obj):
        project_id = getattr(obj, 'project_id', None)
        if project_id is None and hasattr(obj, 'project'):
            project_id = obj.project_id
        if project_id is None:
            return True
        if request.method in SAFE_METHODS and has_organizational_observation(request.user):
            return True
        if _get_active_member(request.user, str(project_id)) is not None:
            return True
        if request.method in SAFE_METHODS:
            target_user_id = view.kwargs.get('user_id') or view.kwargs.get('pk')
            if target_user_id and str(request.user.id) == str(target_user_id):
                return _get_any_member(request.user, str(project_id)) is not None
            if isinstance(obj, ProjectMember) and obj.user_id == request.user.id:
                return True
        return False


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

        # Observation may satisfy general view_* reads only — never writes or
        # sensitive codenames (wage, contacts, approve_*).
        if (
            request.method in SAFE_METHODS
            and has_organizational_observation(request.user)
            and str(permission).startswith('view_')
            and permission
            not in (
                'view_wage',
                'view_sensitive_contacts',
                'view_person_contacts',
            )
        ):
            return True

        return active_member_has_codename(request.user, project_id, permission)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
