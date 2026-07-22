"""Tests for material balance, consumption, and daily-report inventory auto-post."""

import pytest
from django.utils import timezone
from rest_framework import status

from field_reports.models import (
    DailyReport,
    DailyReportMaterial,
    MaterialTransactionType,
    ReportStatus,
)
from field_reports.tasks import _auto_create_inventory_from_report
from resources.models import InventoryTransaction, Material, TransactionType
from resources.services.balance_service import compute_material_balance, running_balance
from resources.services.consumption_service import material_consumption_report


@pytest.fixture
def material(db, project):
    return Material.objects.create(
        project=project,
        material_code='CEM-01',
        material_name='سیمان',
        estimated_total_qty=1000,
        min_stock_level=50,
    )


@pytest.mark.django_db
class TestBalanceService:
    def test_running_balance_math(self, material, user, project):
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-01',
            tx_type=TransactionType.IN,
            quantity=100,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-02',
            tx_type=TransactionType.OUT,
            quantity=30,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-03',
            tx_type=TransactionType.WASTE,
            quantity=10,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-04',
            tx_type=TransactionType.ADJUST,
            quantity=5,
            created_by=user,
            updated_by=user,
        )

        balance = compute_material_balance(material)
        assert balance['total_received'] == 100
        assert balance['total_issued'] == 40
        assert balance['current_balance'] == 65
        assert balance['is_low_stock'] is False

        series = running_balance(material.id, project_id=project.id)
        assert series[-1]['running_balance'] == 65
        assert balance['total_adjusted'] == 5

    def test_running_balance_requires_project_material(self, material, user, project, auth_client):
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-01',
            tx_type=TransactionType.IN,
            quantity=100,
            created_by=user,
            updated_by=user,
        )
        ok = auth_client.get(
            f'/api/v1/projects/{project.id}/inventory-transactions/balance/?material_id={material.id}'
        )
        assert ok.status_code == status.HTTP_200_OK
        assert ok.data[-1]['running_balance'] == 100

        foreign = Material.objects.create(
            project=project,
            material_code='OTHER-MAT',
            material_name='Other mat',
        )
        # material belonging to another project id under this project's path
        from projects.models import Project

        other_project = Project.objects.create(project_code='P-OTHER', project_name='Other')
        foreign.project = other_project
        foreign.save(update_fields=['project'])
        missing = auth_client.get(
            f'/api/v1/projects/{project.id}/inventory-transactions/balance/?material_id={foreign.id}'
        )
        assert missing.status_code == status.HTTP_404_NOT_FOUND

    def test_balance_detail_404_for_foreign_material(self, material, auth_client, project):
        from projects.models import Project

        other = Project.objects.create(project_code='P-X', project_name='X')
        foreign = Material.objects.create(
            project=other,
            material_code='X-01',
            material_name='Foreign',
        )
        resp = auth_client.get(f'/api/v1/projects/{project.id}/material-balance/{foreign.id}/')
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_low_stock_flag(self, material, user, project):
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-01',
            tx_type=TransactionType.IN,
            quantity=60,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-02',
            tx_type=TransactionType.OUT,
            quantity=15,
            created_by=user,
            updated_by=user,
        )
        balance = compute_material_balance(material)
        assert balance['current_balance'] == 45
        assert balance['is_low_stock'] is True

    def test_consumption_vs_planned(self, material, user, project, activity):
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            activity=activity,
            tx_date='2024-08-01',
            tx_type=TransactionType.IN,
            quantity=500,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            activity=activity,
            tx_date='2024-08-02',
            tx_type=TransactionType.OUT,
            quantity=200,
            created_by=user,
            updated_by=user,
        )
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-03',
            tx_type=TransactionType.WASTE,
            quantity=50,
            created_by=user,
            updated_by=user,
        )

        report = material_consumption_report(project.id)
        mat_row = report['materials'][0]
        assert mat_row['consumption_pct'] == 20.0
        assert mat_row['waste_pct'] == 10.0

        act_row = report['activities'][0]
        assert act_row['planned_quantity'] == 100.0
        assert act_row['total_issued'] == 200.0


@pytest.mark.django_db
class TestInventoryAutoPost:
    def test_auto_post_from_approved_report(self, project, user, material):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-10',
            status=ReportStatus.APPROVED,
            created_by=user,
            updated_by=user,
            approved_by=user,
            approved_at=timezone.now(),
        )
        DailyReportMaterial.objects.create(
            report=report,
            material_ref=material,
            material_description='سیمان',
            transaction_type=MaterialTransactionType.RECEIPT,
            quantity=25,
            unit_cost=100,
        )
        DailyReportMaterial.objects.create(
            report=report,
            material_ref=material,
            material_description='سیمان',
            transaction_type=MaterialTransactionType.ISSUE,
            quantity=10,
            unit_cost=100,
        )

        _auto_create_inventory_from_report(report)

        txs = InventoryTransaction.objects.filter(daily_report=report)
        assert txs.count() == 2
        assert txs.filter(tx_type=TransactionType.IN).exists()
        assert txs.filter(tx_type=TransactionType.OUT).exists()

        balance = compute_material_balance(material)
        assert balance['current_balance'] == 15


@pytest.mark.django_db
class TestInventoryTransactionAPI:
    def test_cannot_edit_daily_report_linked_tx(self, auth_client, project, material, user):
        report = DailyReport.objects.create(
            project=project,
            report_date='2024-08-10',
            created_by=user,
            updated_by=user,
        )
        tx = InventoryTransaction.objects.create(
            project=project,
            material=material,
            daily_report=report,
            tx_date='2024-08-10',
            tx_type=TransactionType.IN,
            quantity=10,
            created_by=user,
            updated_by=user,
        )
        base = f'/api/v1/projects/{project.id}/inventory-transactions/{tx.id}/'
        patch = auth_client.patch(base, {'quantity': 20}, format='json')
        assert patch.status_code == status.HTTP_400_BAD_REQUEST
        delete = auth_client.delete(base)
        assert delete.status_code == status.HTTP_400_BAD_REQUEST

    def test_consumption_endpoint(self, auth_client, project, material, user):
        InventoryTransaction.objects.create(
            project=project,
            material=material,
            tx_date='2024-08-01',
            tx_type=TransactionType.IN,
            quantity=100,
            created_by=user,
            updated_by=user,
        )
        url = f'/api/v1/projects/{project.id}/material-balance/consumption/'
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert 'materials' in resp.data
        assert 'activities' in resp.data
