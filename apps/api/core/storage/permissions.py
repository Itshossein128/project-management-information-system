from typing import cast

from rest_framework import permissions

from authentication.models import User
from storage.models import StoredFile
from storage.services import user_may_download_stored_file


class CanAccessStoredFile(permissions.BasePermission):
    """Uploader (confirm) or active member with source permission + allowlist (download).

    Organizational observation does not grant download without active membership
    and the correct view_* codename for the file source (A6-P4).
    """

    def has_permission(self, request, view) -> bool:
        user = cast(User, request.user)
        if not user or not user.is_authenticated:
            return False
        file_id = view.kwargs.get('file_id')
        if not file_id:
            return False
        try:
            stored = StoredFile.objects.prefetch_related('restricted_allowlist').get(pk=file_id)
        except StoredFile.DoesNotExist:
            return True
        if getattr(view, 'require_uploader', False) and stored.uploaded_by_id != user.pk:
            return False
        return user_may_download_stored_file(user, stored)
