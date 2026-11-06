"""A6-P4 creator attribution repair uses real domain rows (no mock records)."""

import pytest

from config.exceptions import CodedValidationError
from cost_control.cbs_services import create_cbs_node
from master_data.models import RoleAccessChange
from permissions.sod import repair_missing_creator


@pytest.mark.django_db
def test_repair_cbs_node_sets_creator_and_audits(project, user, other_user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='CR-NODE',
        cbs_name='Repair test',
        created_by=None,
    )
    node.refresh_from_db()
    assert node.created_by_id is None

    repair_missing_creator(
        record=node,
        field_name='created_by',
        creator=other_user,
        actor=user,
        project=project,
        record_type='cbs_node',
    )
    node.refresh_from_db()
    assert node.created_by_id == other_user.id
    assert RoleAccessChange.objects.filter(
        action='sod_creator_repaired',
        project=project,
    ).exists()


@pytest.mark.django_db
def test_repair_rejects_actor_assigning_self_as_creator(project, user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='CR-SELF',
        cbs_name='Self assign',
        created_by=None,
    )

    with pytest.raises(CodedValidationError) as exc:
        repair_missing_creator(
            record=node,
            field_name='created_by',
            creator=user,
            actor=user,
            project=project,
            record_type='cbs_node',
        )
    assert exc.value.default_code == 'sod_creator_repair_invalid'


@pytest.mark.django_db
def test_repair_rejects_when_creator_already_set(project, user, other_user):
    node = create_cbs_node(
        project_id=project.id,
        cbs_code='CR-SET',
        cbs_name='Already set',
        created_by=user,
    )
    with pytest.raises(CodedValidationError) as exc:
        repair_missing_creator(
            record=node,
            field_name='created_by',
            creator=other_user,
            actor=user,
            project=project,
            record_type='cbs_node',
        )
    assert exc.value.default_code == 'sod_creator_already_set'

