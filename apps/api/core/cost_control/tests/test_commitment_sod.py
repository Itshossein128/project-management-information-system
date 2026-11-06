"""A6-P4 SoD on commitment approval paths."""

import pytest
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from config.exceptions import CodedValidationError
from cost_control.cbs_services import approve_commitment
from cost_control.models import Commitment, CommitmentStatus
from master_data.models import RoleAccessChange
from permissions.role_services import record_access_change
from permissions.sod import assert_not_self_final_approve

User = get_user_model()


@pytest.mark.django_db
def test_creator_cannot_self_approve():
    creator = User.objects.create_user(username='c1', mobile='+989120000101', password='x')
    other = User.objects.create_user(username='c2', mobile='+989120000102', password='x')
    with pytest.raises(CodedValidationError) as exc:
        assert_not_self_final_approve(creator.id, creator, project=None)
    assert exc.value.default_code == 'sod_self_approve'
    assert assert_not_self_final_approve(creator.id, other, project=None).allowed is True


@pytest.mark.django_db
def test_approve_commitment_requires_actor(project, user):
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='C-ACTOR',
        amount=Decimal('10.00'),
        commitment_date=date(2024, 1, 1),
        status=CommitmentStatus.DRAFT,
        created_by=user,
    )
    with pytest.raises(ValidationError) as exc:
        approve_commitment(commitment)
    assert exc.value.detail['code'] == 'sod_actor_required'


@pytest.mark.django_db
def test_break_glass_records_access_change(project, user):
    admin = User.objects.create_superuser(
        username='sod_commit_admin',
        mobile='+989129999001',
        password='x',
    )
    decision = assert_not_self_final_approve(
        admin.id,
        admin,
        break_glass_reason='Emergency finalize',
        project=None,
    )
    assert decision.used_break_glass is True
    record_access_change(
        actor=admin,
        project=project,
        subject_user=user,
        role=None,
        action='sod_break_glass',
        before={'status': 'draft'},
        after={'reason': decision.reason, 'exception': True, 'record_id': 'x'},
    )
    assert RoleAccessChange.objects.filter(action='sod_break_glass', project=project).exists()


@pytest.mark.django_db
def test_approve_commitment_rejects_non_draft(project, user, wbs):
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='C-STAT',
        amount=Decimal('10.00'),
        commitment_date=date(2024, 1, 1),
        status=CommitmentStatus.CLOSED,
        wbs=wbs,
        created_by=user,
        updated_by=user,
    )
    with pytest.raises(ValidationError) as exc:
        approve_commitment(commitment, user=user)
    assert exc.value.detail['code'] == 'invalid_status_transition'


@pytest.mark.django_db
def test_approve_commitment_superuser_break_glass_self_approve_records_audit(
    project, user, wbs,
):
    """Superuser may break-glass self-approve only when reason is provided and audit succeeds."""
    admin = User.objects.create_superuser(
        username='sod_co_super',
        mobile='+989129999102',
        password='x',
    )
    commitment = Commitment.objects.create(
        project=project,
        commitment_number='C-BG',
        amount=Decimal('20.00'),
        commitment_date=date(2024, 1, 2),
        status=CommitmentStatus.DRAFT,
        wbs=wbs,
        created_by=admin,
        updated_by=admin,
    )
    approve_commitment(
        commitment,
        user=admin,
        break_glass_reason='Emergency board directive',
    )
    commitment.refresh_from_db()
    assert commitment.status == CommitmentStatus.APPROVED
    assert RoleAccessChange.objects.filter(
        action='sod_break_glass',
        project=project,
    ).exists()
