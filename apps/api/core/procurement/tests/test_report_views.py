import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate

from procurement.models import (
    ApprovalAction,
    ApprovalLog,
    Block,
    ItemStatus,
    RequisitionHeader,
    RequisitionItem,
)
from procurement.views.report_views import (
    AuditTrailReportView,
    LiquidityDashboardView,
    MaterialDeviationReportView,
    ProcurementStatusReportView,
)
from projects.models import Project
from resources.models import Material

User = get_user_model()


@pytest.mark.django_db
class TestProcurementReportViews:
    def test_procurement_status_report_returns_200(self):
        user = User.objects.create(username="testuser", full_name="Test User")
        project = Project.objects.create(project_name="Test Project", project_code="PRJ-TEST")

        rf = APIRequestFactory()
        req = rf.get(f"/api/v1/projects/{project.id}/reports/procurement-status/")
        force_authenticate(req, user=user)

        view = ProcurementStatusReportView.as_view()
        response = view(req, project_pk=str(project.id))

        assert response.status_code == 200
        assert response.data["project_id"] == str(project.id)
        assert isinstance(response.data["summary"], list)

    def test_liquidity_dashboard_view_structure(self):
        user = User.objects.create(username="liquidity_user", full_name="Liquidity User")
        project = Project.objects.create(project_name="Liquidity Project", project_code="PRJ-LIQ")
        block = Block.objects.create(project=project, block_code="BLK-01", block_name="Block 1", budget=100000.0, created_by=user)
        material = Material.objects.create(project=project, material_code="MAT-01", material_name="Concrete")
        
        req_header = RequisitionHeader.objects.create(
            project=project,
            block=block,
            requested_by=user,
            request_date="2026-01-01",
            created_by=user,
        )
        RequisitionItem.objects.create(
            header=req_header,
            line_number=1,
            material=material,
            requested_qty=2000.0,
            status=ItemStatus.PENDING,
            created_by=user,
        )

        rf = APIRequestFactory()
        req = rf.get(f"/api/v1/projects/{project.id}/reports/liquidity/")
        force_authenticate(req, user=user)

        view = LiquidityDashboardView.as_view()
        response = view(req, project_pk=str(project.id))

        assert response.status_code == 200
        assert response.data["project_id"] == str(project.id)
        assert "liquidity_status" in response.data
        liquidity_status = response.data["liquidity_status"]
        assert len(liquidity_status) == 1
        item = liquidity_status[0]
        assert item["block_code"] == "BLK-01"
        assert item["block_name"] == "Block 1"
        assert item["budget"] == 100000.0
        assert item["total_requested_value"] == 2000.0
        assert item["remaining_liquidity"] == 98000.0

    def test_material_deviation_report_view_structure(self):
        user = User.objects.create(username="deviation_user", full_name="Deviation User")
        project = Project.objects.create(project_name="Deviation Project", project_code="PRJ-DEV")
        block = Block.objects.create(project=project, block_code="BLK-02", block_name="Block 2", budget=50000.0, created_by=user)
        material = Material.objects.create(
            project=project,
            material_code="MAT-02",
            material_name="Steel Rebar",
            estimated_total_qty=100.0,
        )
        
        req_header = RequisitionHeader.objects.create(
            project=project,
            block=block,
            requested_by=user,
            request_date="2026-01-01",
            created_by=user,
        )
        RequisitionItem.objects.create(
            header=req_header,
            line_number=1,
            material=material,
            requested_qty=120.0,
            status=ItemStatus.APPROVED,
            created_by=user,
        )

        rf = APIRequestFactory()
        req = rf.get(f"/api/v1/projects/{project.id}/reports/material-deviation/")
        force_authenticate(req, user=user)

        view = MaterialDeviationReportView.as_view()
        response = view(req, project_pk=str(project.id))

        assert response.status_code == 200
        assert response.data["project_id"] == str(project.id)
        assert "deviation_data" in response.data
        deviation_data = response.data["deviation_data"]
        assert len(deviation_data) == 1
        item = deviation_data[0]
        assert item["block_code"] == "BLK-02"
        assert item["material_name"] == "Steel Rebar"
        assert item["estimated_qty"] == 100.0
        assert item["requested_qty"] == 120.0
        assert item["deviation_qty"] == 20.0
        assert pytest.approx(item["deviation_percent"], 0.1) == 20.0

    def test_audit_trail_report_view_structure(self):
        user = User.objects.create(username="audit_user", full_name="Audit User")
        project = Project.objects.create(project_name="Audit Project", project_code="PRJ-AUD")
        block = Block.objects.create(project=project, block_code="BLK-03", block_name="Block 3", created_by=user)
        req_header = RequisitionHeader.objects.create(
            project=project,
            block=block,
            requested_by=user,
            request_date="2026-01-01",
            created_by=user,
        )

        ApprovalLog.objects.create(
            requisition=req_header,
            step_from="draft",
            step_to="technical_review",
            action=ApprovalAction.APPROVE,
            performed_by=user,
        )
        ApprovalLog.objects.create(
            requisition=req_header,
            step_from="technical_review",
            step_to="rejected",
            action=ApprovalAction.REJECT,
            performed_by=user,
        )

        rf = APIRequestFactory()
        req = rf.get(f"/api/v1/projects/{project.id}/reports/audit-trail/")
        force_authenticate(req, user=user)

        view = AuditTrailReportView.as_view()
        response = view(req, project_pk=str(project.id))

        assert response.status_code == 200
        assert response.data["project_id"] == str(project.id)
        assert "summary" in response.data
        summary = response.data["summary"]
        assert summary["total_actions"] == 2
        assert summary["approved_actions"] == 1
        assert summary["rejected_actions"] == 1
        assert len(response.data["logs"]) == 2
        assert response.data["logs"][0]["requisition_number"] == req_header.requisition_number
        assert response.data["logs"][0]["requisition_scope"] == req_header.scope

