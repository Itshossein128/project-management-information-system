from typing import cast

from rest_framework import permissions

from authentication.models import User
from master_data.models import ProjectMember
from storage.models import StoredFile


class CanAccessStoredFile(permissions.BasePermission):
    """Uploader (confirm) or project member (download) with admin override."""

    def has_permission(self, request, view) -> bool:
        user = cast(User, request.user)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.groups.filter(name='admin').exists():
            return True
        file_id = view.kwargs.get('file_id')
        if not file_id:
            return False
        try:
            stored = StoredFile.objects.get(pk=file_id)
        except StoredFile.DoesNotExist:
            return True
        if getattr(view, 'require_uploader', False) and stored.uploaded_by_id != user.pk:
            return False
        return ProjectMember.objects.filter(
            project_id=stored.project_id,
            user_id=user.pk,
            status='active',
        ).exists()
