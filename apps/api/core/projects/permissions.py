from rest_framework.permissions import BasePermission

from master_data.models import ProjectMember


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        project_id = getattr(request, 'project_id', None) or view.kwargs.get('project_pk')
        if not project_id:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
            return True
        return ProjectMember.objects.filter(
            project_id=project_id,
            user_id=request.user.id,
            status='active',
        ).exists()

    def has_object_permission(self, request, view, obj):
        project_id = getattr(obj, 'project_id', None)
        if project_id is None and hasattr(obj, 'project'):
            project_id = obj.project_id
        if project_id is None:
            return True
        if request.user.is_superuser or request.user.groups.filter(name='admin').exists():
            return True
        return ProjectMember.objects.filter(
            project_id=project_id,
            user_id=request.user.id,
            status='active',
        ).exists()
