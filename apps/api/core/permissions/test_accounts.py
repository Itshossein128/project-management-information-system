"""Reference role accounts for the isolated test environment (R.0.03).

Phone numbers and passwords are intentional non-secret fixtures for local
test/staging only. Project roles map to ``DEFAULT_ROLE_PERMISSIONS`` keys.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

DEV_PASSWORD = 'devpass123'

# Demo + client reference project codes that receive membership for every role.
REFERENCE_PROJECT_CODES: tuple[str, ...] = ('acme', 'buildco', 'shiraz')

SHIRAZ_PROJECT_NAME = 'پروژه ۲۰۰۰ واحدی کمیل‌آباد شیراز'


@dataclass(frozen=True)
class TestRoleAccount:
    """One seeded login used by verify scripts and auth tests."""

    key: str
    mobile: str
    username: str
    full_name: str
    # Django auth Group name (global). None = no global group.
    auth_group: str | None
    # master_data Role.role_name aligned with DEFAULT_ROLE_PERMISSIONS. None for
    # pure global accounts that only need membership without a project role
    # (admin still gets project_manager for scoped endpoint smoke).
    project_role: str | None
    is_superuser: bool = False
    is_staff: bool = False


# Ordered catalog — 11 accounts required by R.0.03 DoD.
TEST_ROLE_ACCOUNTS: tuple[TestRoleAccount, ...] = (
    TestRoleAccount(
        key='admin',
        mobile='+10000000001',
        username='10000000001',
        full_name='Admin User',
        auth_group='admin',
        project_role='project_manager',
        is_superuser=True,
        is_staff=True,
    ),
    TestRoleAccount(
        key='hr',
        mobile='+10000000002',
        username='10000000002',
        full_name='HR Manager',
        auth_group='hr',
        project_role='hr_officer',
    ),
    TestRoleAccount(
        key='visitor',
        mobile='+10000000003',
        username='10000000003',
        full_name='Visitor User',
        auth_group='visitor',
        project_role='viewer',
    ),
    TestRoleAccount(
        key='worker',
        mobile='+10000000004',
        username='10000000004',
        full_name='Field Worker',
        auth_group=None,
        project_role='field_supervisor',
    ),
    TestRoleAccount(
        key='project_manager',
        mobile='+10000000005',
        username='10000000005',
        full_name='Project Manager',
        auth_group='manager',
        project_role='project_manager',
    ),
    TestRoleAccount(
        key='project_controls',
        mobile='+10000000006',
        username='10000000006',
        full_name='Planning Engineer / Project Controls',
        auth_group='engineer',
        project_role='project_controls',
    ),
    TestRoleAccount(
        key='site_supervisor',
        mobile='+10000000007',
        username='10000000007',
        full_name='Site Superintendent',
        auth_group=None,
        project_role='site_supervisor',
    ),
    TestRoleAccount(
        key='finance_manager',
        mobile='+10000000008',
        username='10000000008',
        full_name='Finance Manager',
        auth_group='accountant',
        project_role='finance_manager',
    ),
    TestRoleAccount(
        key='document_controller',
        mobile='+10000000009',
        username='10000000009',
        full_name='Document Controller',
        auth_group=None,
        project_role='document_controller',
    ),
    TestRoleAccount(
        key='executive_approver',
        mobile='+10000000010',
        username='10000000010',
        full_name='Executive Approver',
        auth_group=None,
        project_role='executive_approver',
    ),
    TestRoleAccount(
        key='procurement_officer',
        mobile='+10000000011',
        username='10000000011',
        full_name='Procurement & Contracts Officer',
        auth_group=None,
        project_role='procurement_officer',
    ),
)

TEST_ROLE_ACCOUNTS_BY_KEY: Mapping[str, TestRoleAccount] = {
    account.key: account for account in TEST_ROLE_ACCOUNTS
}

TEST_ROLE_ACCOUNTS_BY_MOBILE: Mapping[str, TestRoleAccount] = {
    account.mobile: account for account in TEST_ROLE_ACCOUNTS
}

# Client fixture paths relative to repository root (R.0.01 / R.0.03).
REFERENCE_FIXTURES: tuple[tuple[str, str], ...] = (
    ('plan.mpp', 'real-data/plan.mpp'),
    (
        'shiraz_daily_report',
        'real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.xlsx',
    ),
)
