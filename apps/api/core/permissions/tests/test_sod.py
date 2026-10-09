"""FR-RPT: segregation of duties helper."""

import pytest
from django.contrib.auth import get_user_model

from config.exceptions import CodedValidationError
from permissions.sod import assert_not_self_final_approve

User = get_user_model()


@pytest.mark.django_db
def test_sod_same_user_raises():
    u = User.objects.create_user(username='sod1', mobile='+989100000001', password='x')
    with pytest.raises(CodedValidationError) as exc:
        assert_not_self_final_approve(u.id, u)
    assert exc.value.default_code == 'sod_self_approve'


@pytest.mark.django_db
def test_sod_different_user_passes():
    a = User.objects.create_user(username='sod_a', mobile='+989100000002', password='x')
    b = User.objects.create_user(username='sod_b', mobile='+989100000003', password='x')
    assert_not_self_final_approve(a.id, b)


@pytest.mark.django_db
def test_sod_null_creator_passes():
    u = User.objects.create_user(username='sod_n', mobile='+989100000004', password='x')
    assert_not_self_final_approve(None, u)


@pytest.mark.django_db
def test_sod_superuser_break_glass():
    creator = User.objects.create_user(username='sod_c', mobile='+989100000005', password='x')
    admin = User.objects.create_superuser(
        username='sod_admin',
        mobile='+989100000006',
        password='x',
    )
    assert_not_self_final_approve(creator.id, admin)
