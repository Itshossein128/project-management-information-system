"""FR-COL: view_sensitive_contacts permission registration."""

from permissions.constants import ALL_PERMISSION_CODENAMES, DEFAULT_ROLE_PERMISSIONS, PERMISSIONS


def test_view_sensitive_contacts_in_permissions_catalog():
    assert 'view_sensitive_contacts' in PERMISSIONS
    assert 'view_sensitive_contacts' in ALL_PERMISSION_CODENAMES


def test_view_sensitive_contacts_granted_to_pm_and_document_controller():
    assert 'view_sensitive_contacts' in DEFAULT_ROLE_PERMISSIONS['project_manager']
    assert 'view_sensitive_contacts' in DEFAULT_ROLE_PERMISSIONS['document_controller']
