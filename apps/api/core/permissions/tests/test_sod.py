"""FR-RPT / A6-P4: segregation of duties helper."""

import pytest
from django.contrib.auth import get_user_model

from config.exceptions import CodedValidationError
from master_data.models import RoleAccessChange
from permissions.sod import assert_not_self_final_approve

User = get_user_model()


@pytest.mark.django_db
def test_sod_same_user_raises():
    u = User.objects.create_user(username='sod1', mobile='+989100000001', password='x')
    with pytest.raises(CodedValidationError) as exc:
        assert_not_self_final_approve(u.id, u, project=None)
    assert exc.value.default_code == 'sod_self_approve'


@pytest.mark.django_db
def test_sod_different_user_passes():
    a = User.objects.create_user(username='sod_a', mobile='+989100000002', password='x')
    b = User.objects.create_user(username='sod_b', mobile='+989100000003', password='x')
    decision = assert_not_self_final_approve(a.id, b, project=None)
    assert decision.allowed is True
    assert decision.used_break_glass is False


@pytest.mark.django_db
def test_sod_null_creator_blocked_without_break_glass():
    u = User.objects.create_user(username='sod_n', mobile='+989100000004', password='x')
    with pytest.raises(CodedValidationError) as exc:
        assert_not_self_final_approve(None, u, project=None)
    assert exc.value.default_code == 'sod_missing_creator'


@pytest.mark.django_db
def test_sod_superuser_does_not_auto_bypass():
    admin = User.objects.create_superuser(
        username='sod_admin',
        mobile='+989100000006',
        password='x',
    )
    with pytest.raises(CodedValidationError) as exc:
        assert_not_self_final_approve(admin.id, admin, project=None)
    assert exc.value.default_code == 'sod_self_approve'


@pytest.mark.django_db
def test_sod_superuser_break_glass_with_reason():
    admin = User.objects.create_superuser(
        username='sod_admin2',
        mobile='+989100000008',
        password='x',
    )
    decision = assert_not_self_final_approve(
        admin.id,
        admin,
        break_glass_reason='Emergency close for blocked payment',
        project=None,
    )
    assert decision.allowed is True
    assert decision.used_break_glass is True
    assert decision.reason.startswith('Emergency')


@pytest.mark.django_db
def test_sod_null_creator_break_glass_unknown_creator():
    admin = User.objects.create_superuser(
        username='sod_admin3',
        mobile='+989100000009',
        password='x',
    )
    decision = assert_not_self_final_approve(
        None,
        admin,
        break_glass_reason='unknown_creator',
        project=None,
    )
    assert decision.used_break_glass is True


@pytest.mark.django_db
def test_sod_self_approve_records_role_access_change(project, user, other_user):
    with pytest.raises(CodedValidationError):
        assert_not_self_final_approve(
            user.id,
            user,
            project=project,
            record_id='00000000-0000-0000-0000-000000000001',
            record_type='test',
        )
    row = RoleAccessChange.objects.filter(action='sod_refusal', actor=user).first()
    assert row is not None
    assert row.project_id == project.id


@pytest.mark.django_db
def test_sod_missing_creator_records_role_access_change(project, user):
    with pytest.raises(CodedValidationError):
        assert_not_self_final_approve(
            None,
            user,
            project=project,
            record_type='test',
        )
    assert RoleAccessChange.objects.filter(action='sod_refusal', actor=user).exists()
