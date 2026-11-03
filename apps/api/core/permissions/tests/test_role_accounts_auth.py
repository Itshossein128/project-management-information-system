"""R.0.03 — reference role accounts authenticate and carry expected permissions."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient

from business_meta.management.commands.seed_test_roles import run_seed_test_roles
from master_data.models import ProjectMember
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from permissions.services import get_role_permission_codenames
from permissions.test_accounts import (
    DEV_PASSWORD,
    REFERENCE_FIXTURES,
    REFERENCE_PROJECT_CODES,
    TEST_ROLE_ACCOUNTS,
)
from projects.models import Project

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _disable_login_ratelimit(settings):
    """Anon login is rate-limited; 11 sequential logins would 429 in one suite."""
    settings.RATELIMIT_ENABLE = False
    cache.clear()


@pytest.fixture
def seeded_test_roles():
    """Light seed: reference projects + 11 role accounts (no full demo graph)."""
    return run_seed_test_roles(with_demo=False)


def test_catalog_has_eleven_accounts():
    assert len(TEST_ROLE_ACCOUNTS) == 11
    mobiles = [a.mobile for a in TEST_ROLE_ACCOUNTS]
    assert len(set(mobiles)) == 11
    assert mobiles[0] == '+10000000001'
    assert mobiles[-1] == '+10000000011'


def test_reference_fixtures_exist_on_disk():
    from pathlib import Path

    root = Path(__file__).resolve().parents[5]
    for label, rel in REFERENCE_FIXTURES:
        path = root / rel
        assert path.is_file() and path.stat().st_size > 0, f'{label} missing: {path}'


def test_all_reference_projects_exist_after_seed(seeded_test_roles):
    codes = set(
        Project.objects.filter(project_code__in=REFERENCE_PROJECT_CODES).values_list(
            'project_code', flat=True
        )
    )
    assert codes == set(REFERENCE_PROJECT_CODES)
    assert set(seeded_test_roles['projects']) == set(REFERENCE_PROJECT_CODES)
    assert len(seeded_test_roles['users']) == 11


@pytest.mark.parametrize('account', TEST_ROLE_ACCOUNTS, ids=lambda a: a.key)
def test_role_account_login_and_permissions(seeded_test_roles, account):
    user = User.objects.get(mobile=account.mobile)
    assert user.check_password(DEV_PASSWORD)

    if account.is_superuser:
        assert user.is_superuser is True
        assert user.is_staff is True

    if account.auth_group:
        assert user.groups.filter(name=account.auth_group).exists()
    else:
        assert user.groups.count() == 0

    assert account.project_role is not None
    expected = set(DEFAULT_ROLE_PERMISSIONS[account.project_role])

    members = list(
        ProjectMember.objects.filter(user=user)
        .select_related('project')
        .prefetch_related('member_roles__role__role_permissions')
    )
    assert {m.project.project_code for m in members} == set(REFERENCE_PROJECT_CODES)

    for member in members:
        actual = get_role_permission_codenames(member)
        assert actual == expected, (
            f'{account.key} on {member.project.project_code}: '
            f'missing={sorted(expected - actual)} extra={sorted(actual - expected)}'
        )

    client = APIClient()
    response = client.post(
        reverse('authentication:login'),
        {'phone_number': account.mobile, 'password': DEV_PASSWORD},
        format='json',
    )
    assert response.status_code == 200, response.content
    body = response.json()
    assert body.get('access'), f'{account.key} missing access token'
    assert body.get('refresh'), f'{account.key} missing refresh token'
    user_payload = body['user']
    assert (
        user_payload.get('phone_number') == account.mobile
        or user_payload.get('mobile') == account.mobile
    )
