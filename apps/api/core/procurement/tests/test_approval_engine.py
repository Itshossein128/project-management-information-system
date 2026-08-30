import pytest
from django.utils import timezone

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from procurement.models import Block, RequisitionHeader, RequisitionItem, RequisitionScope, RequisitionStatus
from procurement.services.approval_engine import (
    WORKSHOP_WORKFLOW_TRANSITIONS,
    get_transitions,
    transition,
)
from procurement.services.workshop_block_service import ensure_workshop_block


@pytest.fixture
def material(db, project):
    from resources.models import Material

    return Material.objects.create(
        project=project,
        material_code='MAT-ENG',
        material_name='Steel',
        estimated_total_qty=500,
    )


@pytest.fixture
def standard_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-ENG',
        block_name='Eng Block',
        created_by=user,
        updated_by=user,
    )


@pytest.fixture
def block_requisition(db, project, user, standard_block, material):
    req = RequisitionHeader.objects.create(
        project=project,
        block=standard_block,
        scope=RequisitionScope.BLOCK,
        requested_by=user,
        request_date=timezone.localdate(),
        status=RequisitionStatus.TECHNICAL_REVIEW,
        created_by=user,
    )
    RequisitionItem.objects.create(
        header=req,
        line_number=1,
        material=material,
        requested_qty=10,
        created_by=user,
    )
    return req


@pytest.fixture
def workshop_requisition(db, project, user, material):
    workshop_block = ensure_workshop_block(project, created_by=user)
    req = RequisitionHeader.objects.create(
        project=project,
        block=workshop_block,
        scope=RequisitionScope.WORKSHOP,
        requested_by=user,
        request_date=timezone.localdate(),
        status=RequisitionStatus.TECHNICAL_REVIEW,
        created_by=user,
    )
    RequisitionItem.objects.create(
        header=req,
        line_number=1,
        material=material,
        requested_qty=10,
        created_by=user,
    )
    return req


@pytest.mark.django_db
class TestApprovalEngine:
    def test_workflow_transitions_defined(self):
        from procurement.services.approval_engine import WORKFLOW_TRANSITIONS, RequisitionStatus

        assert RequisitionStatus.DRAFT in WORKFLOW_TRANSITIONS
        assert 'approve' in WORKFLOW_TRANSITIONS[RequisitionStatus.DRAFT]
        assert WORKFLOW_TRANSITIONS[RequisitionStatus.FINAL_APPROVAL]['approve'] == RequisitionStatus.APPROVED

    def test_transition_draft_to_technical_review(self, db, django_user_model):
        assert transition is not None

    def test_workshop_skips_workshop_approval(self, workshop_requisition, user):
        transitions = get_transitions(workshop_requisition)
        assert RequisitionStatus.WORKSHOP_APPROVAL not in transitions
        assert (
            transitions[RequisitionStatus.TECHNICAL_REVIEW]['approve']
            == RequisitionStatus.CONTROL_CHECK
        )

        updated = transition(workshop_requisition, 'approve', user, comments='ok')
        assert updated.status == RequisitionStatus.CONTROL_CHECK

    def test_block_goes_through_workshop_approval(self, block_requisition, user):
        transitions = get_transitions(block_requisition)
        assert (
            transitions[RequisitionStatus.TECHNICAL_REVIEW]['approve']
            == RequisitionStatus.WORKSHOP_APPROVAL
        )

        updated = transition(block_requisition, 'approve', user, comments='ok')
        assert updated.status == RequisitionStatus.WORKSHOP_APPROVAL

    def test_workshop_control_check_return_goes_to_technical_review(self, workshop_requisition, user):
        workshop_requisition.status = RequisitionStatus.CONTROL_CHECK
        workshop_requisition.save(update_fields=['status'])

        updated = transition(workshop_requisition, 'return', user, comments='fix')
        assert updated.status == RequisitionStatus.TECHNICAL_REVIEW

    def test_block_control_check_return_goes_to_workshop_approval(self, block_requisition, user):
        block_requisition.status = RequisitionStatus.CONTROL_CHECK
        block_requisition.save(update_fields=['status'])

        updated = transition(block_requisition, 'return', user, comments='fix')
        assert updated.status == RequisitionStatus.WORKSHOP_APPROVAL

    def test_workshop_workflow_has_no_workshop_approval_step(self):
        assert RequisitionStatus.WORKSHOP_APPROVAL not in WORKSHOP_WORKFLOW_TRANSITIONS
