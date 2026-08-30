"""Procurement RBAC permissions."""
from rest_framework.permissions import BasePermission

from procurement.services.approval_engine import get_required_role


def has_procurement_step_role(user, project_id, required_role: str) -> bool:
    """Check if a user has the required role for a procurement step."""
    if not user or not user.is_authenticated:
        return False

    # Superuser, staff, or admin group override
    if user.is_superuser or getattr(user, 'is_staff', False) or user.groups.filter(name='admin').exists():
        return True

    allowed_roles = [required_role]
    if '_or_' in required_role:
        allowed_roles.extend(required_role.split('_or_'))

    # Check Django Group names
    if user.groups.filter(name__in=allowed_roles).exists():
        return True

    # Check ProjectMemberRole for the given project
    if project_id:
        from master_data.models import ProjectMemberRole

        has_role = ProjectMemberRole.objects.filter(
            member__project_id=project_id,
            member__user=user,
            member__status='active',
            role__role_name__in=allowed_roles,
        ).exists()
        if has_role:
            return True

    return False


class ProcurementStepPermission(BasePermission):
    """Verify that request.user has the required role for the requisition's current approval step."""

    message = 'You do not have the required role to perform actions at this approval step.'

    def _check_permission_for_requisition(self, user, requisition) -> bool:
        if not requisition:
            return True

        required_role = get_required_role(requisition)
        if not required_role:
            return True

        return has_procurement_step_role(user, requisition.project_id, required_role)

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        pk = view.kwargs.get('pk') or view.kwargs.get('id')
        project_pk = view.kwargs.get('project_pk') or view.kwargs.get('project_id')

        if pk:
            from procurement.models import RequisitionHeader

            qs = RequisitionHeader.objects.filter(id=pk, is_deleted=False)
            if project_pk:
                qs = qs.filter(project_id=project_pk)
            requisition = qs.first()
            if requisition:
                return self._check_permission_for_requisition(request.user, requisition)

        return True

    def has_object_permission(self, request, view, obj) -> bool:
        return self._check_permission_for_requisition(request.user, obj)
