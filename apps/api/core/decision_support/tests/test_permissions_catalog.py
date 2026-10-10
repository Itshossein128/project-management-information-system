from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS


def test_decision_support_permissions_in_catalog():
    assert 'view_decision_support' in PERMISSIONS
    assert 'edit_decision_support' in PERMISSIONS
    assert 'view_decision_support' in DEFAULT_ROLE_PERMISSIONS['project_manager']
    assert 'edit_decision_support' in DEFAULT_ROLE_PERMISSIONS['project_manager']
    assert 'view_decision_support' in DEFAULT_ROLE_PERMISSIONS['planning_engineer']
    assert 'edit_decision_support' in DEFAULT_ROLE_PERMISSIONS['planning_engineer']
    assert 'view_decision_support' in DEFAULT_ROLE_PERMISSIONS['viewer']
    assert 'edit_decision_support' not in DEFAULT_ROLE_PERMISSIONS['viewer']
