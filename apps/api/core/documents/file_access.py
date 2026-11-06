"""Presign and visibility rules for document module file keys (A6-P4)."""

from __future__ import annotations

from documents.models import AccessLevel, ProjectDocument
from permissions.project import active_member_has_codename
from documents.services.upload_service import presign_get_url


def user_may_view_document_file(user, doc: ProjectDocument) -> bool:
    """Active member with view_documents, respecting RESTRICTED allowlist/uploader."""
    if not user or not user.is_authenticated:
        return False
    pid = doc.project_id
    if not active_member_has_codename(user, pid, 'view_documents'):
        return False
    if doc.access_level in (AccessLevel.PUBLIC, AccessLevel.PROJECT):
        return True
    if doc.access_level == AccessLevel.RESTRICTED:
        if doc.uploaded_by_id == user.id:
            return True
        return doc.restricted_to.filter(pk=user.id).exists()
    return False


def presign_document_storage_value(user, doc: ProjectDocument, storage_value: str) -> str:
    if not storage_value or not user_may_view_document_file(user, doc):
        return ''
    return presign_get_url(storage_value)
