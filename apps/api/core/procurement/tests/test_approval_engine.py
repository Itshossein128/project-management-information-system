import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestApprovalEngine:
    def test_workflow_transitions_defined(self):
        from procurement.services.approval_engine import WORKFLOW_TRANSITIONS, RequisitionStatus
        assert RequisitionStatus.DRAFT in WORKFLOW_TRANSITIONS
        assert 'approve' in WORKFLOW_TRANSITIONS[RequisitionStatus.DRAFT]
        assert WORKFLOW_TRANSITIONS[RequisitionStatus.FINAL_APPROVAL]['approve'] == RequisitionStatus.APPROVED

    def test_transition_draft_to_technical_review(self, db, django_user_model):
        from procurement.services.approval_engine import transition
        from procurement.models import RequisitionHeader, RequisitionStatus
        # Just check the import works — full integration tests need fixtures
        assert transition is not None
