"""Receipts-only main table, consumption details, and document-anchored reconciliation (feature 033, task T034)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
import pytest

from common.reporting_units import SpecialtyUnit
from field_reports.models import (
    DailyReport,
    DailyReportDerivedSource,
    DailyReportMaterial,
    ReconciliationStatus,
)
from field_reports.serializers import DailyReportDetailSerializer
from field_reports.services.daily_report_aggregation import (
    compute_aggregation_fingerprint,
    rebuild_daily_report_summary,
)
from field_reports.services.material_reconciliation import reconcile_report_materials
from projects.models import Project
from resources.models import InventoryTransaction, Material, TransactionType
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportMaterial,
    MaterialTransactionKind,
    SubReportStatus,
)

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)

@pytest.mark.django_db
def test_unclassified_unit_material_never_becomes_a_receipt(project, user):
    source = DisciplineSubReport.objects.create(
        project=project, report_date=REPORT_DATE, unit=SpecialtyUnit.WAREHOUSE,
        discipline='civil', status=SubReportStatus.SUBMITTED, created_by=user,
    )
    DisciplineSubReportMaterial.objects.create(
        sub_report=source, material_description='نوع نامعلوم', quantity=Decimal('5'),
        unit='kg', transaction_type=None,
    )
    summary = rebuild_daily_report_summary(project.id, REPORT_DATE, user=user)
    row = summary.material_entries.get(material_description='نوع نامعلوم')
    assert row.transaction_type == 'unknown'
    assert row.receipt_resolved is False
    payload = DailyReportDetailSerializer(summary).data['materials_summary']
    assert not payload['main_table']
    assert payload['details'][0]['transaction_type'] == 'unknown'


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
    )


@pytest.fixture
def material(db):
    """A project-scoped material."""
    project = Project.objects.create(
        project_code='PRJ-TEST',
        project_name='Test Project',
        employer='Employer Co',
    )
    return Material.objects.create(
        project=project,
        material_code='MAT-001',
        material_name='Test Material',
    )


# ---------------------------------------------------------------------------
# §3.4: receipts-only main table + consumption details
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReceiptsOnlySummary:
    def test_main_table_contains_only_resolved_receipts(self, db, user):
        """The daily report summary's main table shows ONLY resolved receipt rows."""
        project = Project.objects.create(
            project_code='PRJ-TEST-2',
            project_name='Test Project 2',
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

        resolved_material = Material.objects.create(
            project=project,
            material_code='MAT-RES-01',
            material_name='Resolved Beams',
        )
        unresolved_material = Material.objects.create(
            project=project,
            material_code='MAT-UNRES-01',
            material_name='Unresolved Beams',
        )

        resolved_row = DailyReportMaterial.objects.create(
            report=report,
            material_ref=resolved_material,
            material_description='Resolved Beams',
            quantity=Decimal('10.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-2024-001',
            supplier='Supplier A',
            receipt_resolved=True,
        )
        unresolved_row = DailyReportMaterial.objects.create(
            report=report,
            material_ref=unresolved_material,
            material_description='Unresolved Beams',
            quantity=Decimal('5.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-MISSING-999',
            receipt_resolved=False,
            supplier='Supplier B',
        )

        data = DailyReportDetailSerializer(report).data

        main_table_materials = data['materials_summary']['main_table']
        resolved_ids = [
            str(m['id']) for m in main_table_materials
            if m.get('receipt_resolved') is True
        ]
        unresolved_ids = [
            str(m['id']) for m in main_table_materials
            if m.get('receipt_resolved') is not True
        ]

        assert len(unresolved_ids) == 0, (
            f"Unresolved receipts should not appear in main table, "
            f"but found: {unresolved_ids}"
        )
        assert len(resolved_ids) == 1
        assert resolved_ids[0] == str(resolved_row.id)
        grouped = {item['material_description']: item for item in data['materials_summary']['grouped_summary']}
        assert grouped['Resolved Beams']['total_received'] == 10
        assert 'Unresolved Beams' not in grouped

        # Unresolved row is in details, never silently lost
        detail_ids = [str(m['id']) for m in data['materials_summary']['details']]
        assert str(unresolved_row.id) in detail_ids

    def test_consumption_rows_present_in_details_payload(self, db, user):
        """Consumption rows must always be present in the details payload and excluded from main_table (FR-022)."""
        project = Project.objects.create(
            project_code='PRJ-TEST-3',
            project_name='Test Project 3',
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

        receipt_material = Material.objects.create(
            project=project,
            material_code='MAT-REC-01',
            material_name='Receipt Material',
        )
        consumption_material = Material.objects.create(
            project=project,
            material_code='MAT-CON-01',
            material_name='Consumption Material',
        )

        DailyReportMaterial.objects.create(
            report=report,
            material_ref=receipt_material,
            material_description='Receipt Material',
            quantity=Decimal('10.0000'),
            unit='kg',
            transaction_type='receipt',
            warehouse_document_reference='WD-2024-001',
            receipt_resolved=True,
        )
        consumption_row = DailyReportMaterial.objects.create(
            report=report,
            material_ref=consumption_material,
            material_description='Consumption Material',
            quantity=Decimal('3.0000'),
            unit='kg',
            transaction_type='issue',
            consumption_location='Block B Floor 2',
            warehouse_document_reference='',
            receipt_resolved=False,
        )

        data = DailyReportDetailSerializer(report).data

        main_ids = [str(m['id']) for m in data['materials_summary']['main_table']]
        assert str(consumption_row.id) not in main_ids

        details = data['materials_summary']['details']
        issue_rows = [
            m for m in details if m.get('transaction_type') in ('issue', 'consumption')
        ]
        assert len(issue_rows) == 1
        assert issue_rows[0]['consumption_location'] == 'Block B Floor 2'

    def test_rebuild_derives_receipt_resolution_and_provenance(self, db, user):
        """Aggregation derives receipt_resolved from project warehouse documents and preserves provenance (T036)."""
        project = Project.objects.create(
            project_code='PRJ-TEST-REBUILD-MAT',
            project_name='Rebuild Materials Project',
            employer='Employer Co',
        )
        steel = Material.objects.create(
            project=project,
            material_code='MAT-STEEL-10',
            material_name='Rebar 18',
        )
        # Create project warehouse document for WD-2024-100
        doc = InventoryTransaction.objects.create(
            project=project,
            material=steel,
            tx_date=REPORT_DATE,
            tx_type=TransactionType.IN,
            quantity=Decimal('40.0000'),
            document_ref='WD-2024-100',
            created_by=user,
        )

        sr = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.WAREHOUSE,
            legacy_discipline=SpecialtyUnit.WAREHOUSE,
            discipline='civil',
            status=SubReportStatus.APPROVED,
            is_current=True,
            version_number=1,
            created_by=user,
            updated_by=user,
            submitted_by=user,
            approved_by=user,
        )
        r_resolved = DisciplineSubReportMaterial.objects.create(
            sub_report=sr,
            transaction_type=MaterialTransactionKind.RECEIPT,
            material_ref=steel,
            material_description='Rebar 18',
            quantity=Decimal('40.0000'),
            unit='ton',
            supplier='Esfahan Steel',
            warehouse_document_reference='WD-2024-100',
        )
        r_unresolved = DisciplineSubReportMaterial.objects.create(
            sub_report=sr,
            transaction_type=MaterialTransactionKind.RECEIPT,
            material_ref=steel,
            material_description='Rebar 18 Unverified',
            quantity=Decimal('10.0000'),
            unit='ton',
            supplier='Other Supplier',
            warehouse_document_reference='WD-UNKNOWN-999',
        )
        r_consumption = DisciplineSubReportMaterial.objects.create(
            sub_report=sr,
            transaction_type=MaterialTransactionKind.CONSUMPTION,
            material_ref=steel,
            material_description='Rebar 18 Issued',
            quantity=Decimal('15.0000'),
            unit='ton',
            consumption_location='Tower A Foundation',
        )

        summary = rebuild_daily_report_summary(project.id, REPORT_DATE, user=user)
        derived_rows = list(summary.material_entries.filter(is_deleted=False).order_by('id'))
        assert len(derived_rows) == 3

        data = DailyReportDetailSerializer(summary).data
        assert len(data['materials_summary']['main_table']) == 1
        main_item = data['materials_summary']['main_table'][0]
        assert main_item['warehouse_document_reference'] == 'WD-2024-100'
        assert main_item['supplier'] == 'Esfahan Steel'
        assert main_item['receipt_evidence'] == 'resolved'
        assert main_item['reconciliation_status'] == ReconciliationStatus.MATCH
        assert main_item['reconciliation_document_id'] == str(doc.id)

        assert len(data['materials_summary']['details']) == 2
        assert 'grouped_summary' in data['materials_summary']
        assert len(data['materials_summary']['grouped_summary']) >= 1
        assert 'aggregated_at_jalali' in data['aggregation']
        assert data['aggregation']['aggregated_at_jalali'] is not None

        # Provenance recorded for all 3 derived material rows
        sources = DailyReportDerivedSource.objects.filter(
            daily_report=summary, derived_kind='material'
        )
        assert sources.count() == 3
        source_row_ids = {s.source_row_id for s in sources}
        assert source_row_ids == {
            str(r_resolved.id),
            str(r_unresolved.id),
            str(r_consumption.id),
        }

        # Fingerprint changes when supplier or document reference changes
        fp_before = compute_aggregation_fingerprint(None, [sr])
        r_resolved.warehouse_document_reference = 'WD-2024-101'
        r_resolved.save()
        sr.refresh_from_db()
        fp_after = compute_aggregation_fingerprint(None, [sr])
        assert fp_before != fp_after
