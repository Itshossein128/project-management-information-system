"""Tests for procurement workflow timeline service and serializer enrichment."""
import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from procurement.models import (
    ApprovalAction,
    ApprovalLog,
    Block,
    RequisitionHeader,
    RequisitionItem,
    RequisitionScope,
    RequisitionStatus,
)
from procurement.serializers import RequisitionHeaderListSerializer, RequisitionHeaderSerializer
from procurement.services.approval_engine import transition
from procurement.services.requisition_service import partial_approve_items
from procurement.services.workflow_timeline_service import (
    build_workflow_timeline,
    compute_workflow_progress,
    get_next_approver,
    log_requisition_created,
)
from procurement.views.report_views import AuditTrailReportView
from resources.models import Material


@pytest.fixture
def material(db, project):
    return Material.objects.create(
        project=project,
        material_code='MAT-WF',
        material_name='Cement',
        estimated_total_qty=1000,
    )


@pytest.fixture
def standard_block(db, project, user):
    return Block.objects.create(
        project=project,
        block_code='BLK-WF',
        block_name='Workflow Block',
        budget=50000,
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
        status=RequisitionStatus.DRAFT,
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


def _advance_to(requisition, target_status, user):
    """Approve through workflow until target_status is reached."""
    safety = 0
    while requisition.status != target_status and safety < 20:
        requisition.refresh_from_db()
        if requisition.status == target_status:
            break
        if requisition.status in (RequisitionStatus.APPROVED, RequisitionStatus.REJECTED):
            break
        transition(requisition, 'approve', user)
        requisition.refresh_from_db()
        safety += 1
    return requisition


@pytest.mark.django_db
class TestWorkflowTimelineService:
    def test_create_requisition_logs_create_action(self, block_requisition, user):
        log_requisition_created(block_requisition, user)
        log = ApprovalLog.objects.filter(
            requisition=block_requisition,
            action=ApprovalAction.CREATE,
        ).first()
        assert log is not None
        assert log.step_to == RequisitionStatus.DRAFT

    def test_block_full_approve_chain_eight_steps(self, block_requisition, user):
        log_requisition_created(block_requisition, user)
        _advance_to(block_requisition, RequisitionStatus.APPROVED, user)
        block_requisition.refresh_from_db()

        timeline = build_workflow_timeline(block_requisition)
        assert len(timeline) == 8
        assert compute_workflow_progress(block_requisition) == '8/8'
        assert all(step['state'] == 'completed' for step in timeline if not step['skipped'])

    def test_workshop_scope_skips_workshop_approval(self, db, project, user, material):
        from procurement.services.workshop_block_service import ensure_workshop_block

        workshop_block = ensure_workshop_block(project, created_by=user)
        req = RequisitionHeader.objects.create(
            project=project,
            block=workshop_block,
            scope=RequisitionScope.WORKSHOP,
            requested_by=user,
            request_date=timezone.localdate(),
            status=RequisitionStatus.DRAFT,
            created_by=user,
        )
        RequisitionItem.objects.create(
            header=req,
            line_number=1,
            material=material,
            requested_qty=5,
            created_by=user,
        )
        log_requisition_created(req, user)
        _advance_to(req, RequisitionStatus.APPROVED, user)
        req.refresh_from_db()

        timeline = build_workflow_timeline(req)
        workshop_step = next(s for s in timeline if s['code'] == RequisitionStatus.WORKSHOP_APPROVAL)
        assert workshop_step['state'] == 'skipped'
        assert compute_workflow_progress(req) == '7/7'

    def test_partial_approve_log_has_details(self, block_requisition, user):
        _advance_to(block_requisition, RequisitionStatus.FINAL_APPROVAL, user)
        item = block_requisition.items.first()
        partial_approve_items(
            block_requisition,
            [{'item_id': str(item.id), 'approved_qty': 8}],
            user,
        )
        log = ApprovalLog.objects.filter(
            requisition=block_requisition,
            action=ApprovalAction.PARTIAL_APPROVE,
        ).latest('performed_at')
        assert log.details is not None
        assert len(log.details) == 1
        assert log.details[0]['material_code'] == 'MAT-WF'

    def test_list_serializer_next_approver_at_technical_review(self, block_requisition, user):
        log_requisition_created(block_requisition, user)
        transition(block_requisition, 'approve', user)
        block_requisition.refresh_from_db()
        assert block_requisition.status == RequisitionStatus.TECHNICAL_REVIEW

        data = RequisitionHeaderListSerializer(block_requisition).data
        assert data['next_approver_role'] == 'technical_office'
        assert data['next_approver_role_label'] == 'دفتر فنی'

    def test_detail_serializer_timeline_current_matches_status(self, block_requisition, user):
        log_requisition_created(block_requisition, user)
        transition(block_requisition, 'approve', user)
        block_requisition.refresh_from_db()

        data = RequisitionHeaderSerializer(block_requisition).data
        current_steps = [s for s in data['workflow_timeline'] if s['state'] == 'current']
        assert len(current_steps) == 1
        assert current_steps[0]['code'] == block_requisition.status

    def test_audit_report_includes_requisition_number(self, block_requisition, user, project):
        log_requisition_created(block_requisition, user)
        transition(block_requisition, 'approve', user)

        rf = APIRequestFactory()
        req = rf.get(f'/api/v1/projects/{project.id}/reports/audit-trail/')
        force_authenticate(req, user=user)
        response = AuditTrailReportView.as_view()(req, project_pk=str(project.id))

        assert response.status_code == 200
        logs = response.data['logs']
        assert len(logs) >= 1
        assert logs[0]['requisition_number'] == block_requisition.requisition_number

    def test_get_next_approver_null_when_approved(self, block_requisition, user):
        _advance_to(block_requisition, RequisitionStatus.APPROVED, user)
        block_requisition.refresh_from_db()
        assert get_next_approver(block_requisition) is None
