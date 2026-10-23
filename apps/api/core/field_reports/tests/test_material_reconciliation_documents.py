"""Document-anchored material reconciliation tests (feature 033, task T034)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
import pytest

from field_reports.models import (
    DailyReport,
    DailyReportMaterial,
    ReconciliationStatus,
)
from field_reports.services.material_reconciliation import reconcile_report_materials
from projects.models import Project
from resources.models import InventoryTransaction, Material, TransactionType

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='reconcile_user',
        email='reconcile@example.com',
        password='testpass123',
    )


@pytest.mark.django_db
class TestMaterialReconciliationDocuments:
    def test_reconciliation_match_when_equal(self, db, user):
        """Reconciliation returns 'match' and persists resolved_document_id when recorded quantity equals document quantity."""
        project = Project.objects.create(
            project_code='PRJ-TEST-MATCH',
            project_name='Test Match',
            employer='Employer Co',
        )
        report = DailyReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            shift='full',
            work_front='Site A',
            site_status='active',
            prepared_by=user,
            created_by=user,
            updated_by=user,
        )
        doc_material = Material.objects.create(
            project=project,
            material_code='MAT-DOC-01',
            material_name='Doc Material',
        )
        doc = InventoryTransaction.objects.create(
            project=project,
            material=doc_material,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('25.0000'),
            document_ref='WD-2024-010',
            created_by=user,
        )
        row = DailyReportMaterial.objects.create(
            report=report,
            material_ref=doc_material,
            material_description='Doc Material',
            quantity=Decimal('25.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-2024-010',
            supplier='Supplier X',
            receipt_resolved=True,
        )

        result = reconcile_report_materials(report)
        items = result.get('items', [])
        match_items = [i for i in items if i.get('status') == 'match']
        assert len(match_items) == 1
        item = match_items[0]
        assert item['recorded_qty'] == '25.0000'
        assert item['document_qty'] == '25.0000'
        assert item['evidence']['basis'] == 'specific_document'
        assert item['evidence']['resolved_document_id'] == str(doc.id)

        row.refresh_from_db()
        assert row.reconciliation_status == ReconciliationStatus.MATCH
        assert row.reconciliation_document_id == str(doc.id)
        assert row.reconciliation_checked_at is not None

    def test_reconciliation_mismatch_when_differing(self, db, user):
        """Reconciliation returns 'mismatch' with both quantities when recorded quantity differs from document quantity."""
        project = Project.objects.create(
            project_code='PRJ-TEST-MISMATCH',
            project_name='Test Mismatch',
            employer='Employer Co',
        )
        report = DailyReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            shift='full',
            work_front='Site A',
            site_status='active',
            prepared_by=user,
            created_by=user,
            updated_by=user,
        )
        doc_material = Material.objects.create(
            project=project,
            material_code='MAT-DOC-02',
            material_name='Doc Material',
        )
        # Create warehouse document with quantity 30, while report row records 25
        doc = InventoryTransaction.objects.create(
            project=project,
            material=doc_material,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('30.0000'),
            document_ref='WD-2024-010',
            created_by=user,
        )
        row = DailyReportMaterial.objects.create(
            report=report,
            material_ref=doc_material,
            material_description='Doc Material',
            quantity=Decimal('25.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-2024-010',
            supplier='Supplier X',
            receipt_resolved=True,
        )

        result = reconcile_report_materials(report)
        items = result.get('items', [])
        mismatch_items = [i for i in items if i.get('status') == 'mismatch']
        assert len(mismatch_items) == 1
        item = mismatch_items[0]
        assert item['recorded_qty'] == '25.0000'
        assert item['consumed_qty'] == '25.0000'
        assert item['document_qty'] == '30.0000'
        assert item['evidence']['basis'] == 'specific_document'
        assert item['evidence']['resolved_document_id'] == str(doc.id)

        row.refresh_from_db()
        assert row.reconciliation_status == ReconciliationStatus.MISMATCH
        assert row.reconciliation_document_id == str(doc.id)

    def test_reconciliation_insufficient_data_when_no_or_unresolvable_document(
        self, db, user
    ):
        """Reconciliation returns 'insufficient_data' (never a fabricated match) when reference is missing or unresolvable, even if global balance is sufficient."""
        project = Project.objects.create(
            project_code='PRJ-TEST-NODOC',
            project_name='Test No Doc',
            employer='Employer Co',
        )
        report = DailyReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            shift='full',
            work_front='Site A',
            site_status='active',
            prepared_by=user,
            created_by=user,
            updated_by=user,
        )
        no_doc_material = Material.objects.create(
            project=project,
            material_code='MAT-NODOC-01',
            material_name='No Doc Material',
        )
        # Global balance has plenty of stock (100 kg), but the specific document is not referenced/found
        InventoryTransaction.objects.create(
            project=project,
            material=no_doc_material,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('100.0000'),
            document_ref='WD-OTHER-DOC',
            created_by=user,
        )
        row_missing_ref = DailyReportMaterial.objects.create(
            report=report,
            material_ref=no_doc_material,
            material_description='No Doc Material',
            quantity=Decimal('10.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='',
            receipt_resolved=False,
            supplier='Supplier Y',
        )
        row_unresolvable_ref = DailyReportMaterial.objects.create(
            report=report,
            material_ref=no_doc_material,
            material_description='Unresolvable Doc Material',
            quantity=Decimal('10.0000'),
            unit='kg',
            transaction_type='issue',
            warehouse_document_reference='WD-NONEXISTENT-999',
            receipt_resolved=False,
        )

        result = reconcile_report_materials(report)
        items = result.get('items', [])
        assert len(items) == 2
        for item in items:
            assert item['status'] == 'insufficient_data'
            assert item['document_qty'] is None
            assert item['evidence']['resolved_document_id'] is None
            assert item['evidence']['basis'] == 'specific_document'

        row_missing_ref.refresh_from_db()
        row_unresolvable_ref.refresh_from_db()
        assert row_missing_ref.reconciliation_status == ReconciliationStatus.INSUFFICIENT_DATA
        assert row_unresolvable_ref.reconciliation_status == ReconciliationStatus.INSUFFICIENT_DATA

    def test_global_balance_appears_only_as_cross_check(self, db, user):
        """Global balance appears only under a labeled 'cross_check' key, never as the reconciliation basis."""
        project = Project.objects.create(
            project_code='PRJ-TEST-CC',
            project_name='Test Cross Check',
            employer='Employer Co',
        )
        report = DailyReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            shift='full',
            work_front='Site A',
            site_status='active',
            prepared_by=user,
            created_by=user,
            updated_by=user,
        )
        doc_material_1 = Material.objects.create(
            project=project,
            material_code='MAT-CC-01',
            material_name='Doc Mat 1',
        )
        InventoryTransaction.objects.create(
            project=project,
            material=doc_material_1,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('25.0000'),
            document_ref='WD-2024-010',
            created_by=user,
        )
        DailyReportMaterial.objects.create(
            report=report,
            material_ref=doc_material_1,
            material_description='Doc Mat 1',
            quantity=Decimal('25.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-2024-010',
            receipt_resolved=True,
        )

        result = reconcile_report_materials(report)
        items = result.get('items', [])
        assert len(items) == 1
        item = items[0]
        assert item['evidence']['basis'] == 'specific_document'
        assert 'cross_check' in item
        assert item['cross_check']['advisory_only'] is True
        assert item['cross_check']['global_balance'] == '25.0000'
        assert 'available_balance' not in item
