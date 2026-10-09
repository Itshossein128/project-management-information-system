"""FR-RPT: minimum role set present in constants."""

from permissions.constants import DEFAULT_ROLE_DESCRIPTIONS, DEFAULT_ROLE_PERMISSIONS


REQUIRED = (
    'executive_approver',
    'project_controls',
    'site_specialist',
    'supervisor_consultant',
    'hr_officer',
    'project_manager',
    'finance_manager',
    'viewer',
)


def test_fr_rpt_roles_in_defaults():
    for name in REQUIRED:
        assert name in DEFAULT_ROLE_PERMISSIONS, name
        assert name in DEFAULT_ROLE_DESCRIPTIONS, name


def test_executive_and_controls_have_dashboard():
    assert 'view_dashboard' in DEFAULT_ROLE_PERMISSIONS['executive_approver']
    assert 'view_dashboard' in DEFAULT_ROLE_PERMISSIONS['project_controls']


def test_viewer_has_no_approve_permissions():
    viewer = DEFAULT_ROLE_PERMISSIONS['viewer']
    assert not any(p.startswith('approve_') for p in viewer)
