"""Tests for Phase 8 / US6: Migrate legacy reports without losing history.

Covering:
- T061: Mapping rules (civil/finishing -> buildings, plumbing/hvac/mechanical -> mechanical,
        electrical -> electrical; no inference for machinery/warehouse/security);
        100% accounting in UnitReportMigrationTrace; MigrationExecutor forward/reverse/forward drill.
- T062: Collision resolution via latest business change time and stable UUID tie-breaker;
        exact duplicates as duplicate_alias; unknown disciplines quarantined with stable reason codes.
- T063: Preservation of linked_daily_report; rollback from trace ledger.
"""
from __future__ import annotations

import json
import uuid
from datetime import date, timedelta
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone
from rest_framework.test import APIClient

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport
from inventory.models import DepartmentActivityRecord
from sub_reports.models import (
    Discipline,
    DisciplineSubReport,
    DisciplineSubReportActivity,
    MigrationDisposition,
    SubReportStatus,
    UnitReportEventType,
    UnitReportMigrationQuarantine,
    UnitReportMigrationTrace,
    UnitReportStatusEvent,
)
from sub_reports.services.migration import (
    LEGACY_DISCIPLINE_TO_CANONICAL_UNIT,
    migrate_legacy_sub_reports,
    rollback_unit_report_migration,
)

User = get_user_model()


@pytest.fixture(autouse=True)
def ensure_basic_roles(db):
    from master_data.models import Role
    for r in ('project_manager', 'viewer', 'site_supervisor'):
        Role.objects.get_or_create(role_name=r)


def _create_legacy_sub_report(
    project,
    user,
    *,
    discipline: str = 'civil',
    report_date: str = '2026-10-21',
    status: str = SubReportStatus.DRAFT,
    **kwargs,
) -> DisciplineSubReport:
    """Create a legacy-style sub-report where canonical unit is NULL."""
    defaults = {
        'project': project,
        'discipline': discipline,
        'report_date': report_date,
        'unit': None,
        'legacy_discipline': '',
        'lineage_id': None,
        'version_number': 1,
        'is_current': kwargs.pop('is_current', False),
        'status': status,
        'created_by': user,
    }
    defaults.update(kwargs)
    return DisciplineSubReport.objects.create(**defaults)


@pytest.mark.django_db(transaction=True)
class TestMigrationMappingAndAccounting:
    """T061: Mapping rules and 100% accounting in UnitReportMigrationTrace."""

    def test_legacy_discipline_mapping_rules(self, project, user):
        """civil/finishing -> buildings; plumbing/hvac/mechanical -> mechanical; electrical -> electrical.

        No inference for machinery, warehouse, or security.
        """
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['civil'] == SpecialtyUnit.BUILDINGS
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['finishing'] == SpecialtyUnit.BUILDINGS
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['plumbing'] == SpecialtyUnit.MECHANICAL
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['hvac'] == SpecialtyUnit.MECHANICAL
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['mechanical'] == SpecialtyUnit.MECHANICAL
        assert LEGACY_DISCIPLINE_TO_CANONICAL_UNIT['electrical'] == SpecialtyUnit.ELECTRICAL

        for excluded in ('machinery', 'warehouse', 'security'):
            assert excluded not in LEGACY_DISCIPLINE_TO_CANONICAL_UNIT

        # Create one legacy report per legacy discipline on different dates
        reports = {
            'civil': _create_legacy_sub_report(project, user, discipline='civil', report_date='2026-10-01'),
            'finishing': _create_legacy_sub_report(project, user, discipline='finishing', report_date='2026-10-02'),
            'plumbing': _create_legacy_sub_report(project, user, discipline='plumbing', report_date='2026-10-03'),
            'hvac': _create_legacy_sub_report(project, user, discipline='hvac', report_date='2026-10-04'),
            'electrical': _create_legacy_sub_report(project, user, discipline='electrical', report_date='2026-10-05'),
            'mechanical': _create_legacy_sub_report(project, user, discipline='mechanical', report_date='2026-10-06'),
        }

        migrate_legacy_sub_reports(project_id=project.id)

        reports['civil'].refresh_from_db()
        assert reports['civil'].unit == SpecialtyUnit.BUILDINGS
        assert reports['civil'].legacy_discipline == 'civil'

        reports['finishing'].refresh_from_db()
        assert reports['finishing'].unit == SpecialtyUnit.BUILDINGS
        assert reports['finishing'].legacy_discipline == 'finishing'

        reports['plumbing'].refresh_from_db()
        assert reports['plumbing'].unit == SpecialtyUnit.MECHANICAL

        reports['hvac'].refresh_from_db()
        assert reports['hvac'].unit == SpecialtyUnit.MECHANICAL

        reports['electrical'].refresh_from_db()
        assert reports['electrical'].unit == SpecialtyUnit.ELECTRICAL

        reports['mechanical'].refresh_from_db()
        assert reports['mechanical'].unit == SpecialtyUnit.MECHANICAL

    def test_100_percent_accounting_traces_every_report_and_activity_row(self, project, user):
        """Every source report and activity row must exist in trace exactly once."""
        rep = _create_legacy_sub_report(project, user, discipline='civil', report_date='2026-10-10')
        act = DisciplineSubReportActivity.objects.create(
            sub_report=rep,
            row_number=1,
            shift='day',
            crew_name='Crew A',
            activity_description='Foundation pour',
        )
        dar = DepartmentActivityRecord.objects.create(
            project=project,
            department='buildings',
            date='2026-10-10',
            activity_description='Masonry wall inspection',
        )

        migrate_legacy_sub_reports(project_id=project.id)

        # Check trace entries
        rep_trace = UnitReportMigrationTrace.objects.filter(
            source_system='legacy_sub_report',
            source_model='DisciplineSubReport',
            source_id=str(rep.id),
        ).first()
        assert rep_trace is not None
        assert rep_trace.disposition == MigrationDisposition.MIGRATED
        assert rep_trace.canonical_unit == SpecialtyUnit.BUILDINGS
        assert rep_trace.original_category == 'civil'
        assert rep_trace.source_checksum != ''
        assert rep_trace.target_report_id == rep.id

        dar_trace = UnitReportMigrationTrace.objects.filter(
            source_system='inventory',
            source_model='DepartmentActivityRecord',
            source_id=str(dar.id),
        ).first()
        assert dar_trace is not None
        assert dar_trace.disposition == MigrationDisposition.MIGRATED
        assert dar_trace.canonical_unit == SpecialtyUnit.BUILDINGS

        dar.refresh_from_db()
        assert dar.unit_report_id == rep.id

    def test_migration_executor_rehearsal(self):
        """MigrationExecutor forward -> pre-feature target -> forward again, restoring leaf in finally."""
        executor = MigrationExecutor(connection)
        current_leaves = dict(executor.loader.graph.leaf_nodes())
        leaf_targets = list(executor.loader.graph.leaf_nodes())

        # Roll back feature 032 apps to pre-feature targets
        feature_rollbacks = {
            'sub_reports': '0004_standardize_weather',
            'field_reports': '0018_daily_header_weather',
            'inventory': '0005_department_activity_contractor_ref',
            'project_templates': '0002_seed_system_templates',
        }
        pre_feature_targets = [
            (app, feature_rollbacks.get(app, leaf))
            for app, leaf in current_leaves.items()
        ]

        try:
            # Unapply down to pre-feature boundary
            executor.migrate(pre_feature_targets)
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(leaf_targets)
            sub_reports_steps = [m for m, _ in plan if m.app_label == 'sub_reports']
            assert len(sub_reports_steps) >= 2

            # Migrate forward again
            executor.migrate(leaf_targets)
        finally:
            # Ensure leaf migration is restored on test database
            executor = MigrationExecutor(connection)
            executor.migrate(leaf_targets)


@pytest.mark.django_db(transaction=True)
class TestCollisionAndQuarantine:
    """T062: Collision resolution, duplicate aliases, and quarantine."""

    def test_collision_resolution_selects_latest_business_change_time(self, project, user):
        """Multiple legacy reports for same project/date/unit are preserved as versions;

        current selected by latest business change time, with displaced current markers traced.
        """
        now = timezone.now()
        t1 = now - timedelta(hours=3)
        t2 = now - timedelta(hours=1)

        # rep1 (civil -> buildings) submitted earlier
        rep1 = _create_legacy_sub_report(
            project, user,
            discipline='civil',
            report_date='2026-10-15',
            status=SubReportStatus.SUBMITTED,
            submitted_by=user,
            submitted_at=t1,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=rep1, row_number=1, shift='day', crew_name='Civil Crew',
            activity_description='Concrete pour',
        )

        # rep2 (finishing -> buildings) approved later (winner)
        rep2 = _create_legacy_sub_report(
            project, user,
            discipline='finishing',
            report_date='2026-10-15',
            status=SubReportStatus.APPROVED,
            submitted_by=user,
            submitted_at=t1,
            approved_by=user,
            approved_at=t2,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=rep2, row_number=1, shift='day', crew_name='Finishing Crew',
            activity_description='Drywall installation',
        )

        migrate_legacy_sub_reports(project_id=project.id)

        rep1.refresh_from_db()
        rep2.refresh_from_db()

        # Both preserved as versions in same lineage
        assert rep1.lineage_id == rep2.lineage_id
        assert rep1.unit == SpecialtyUnit.BUILDINGS
        assert rep2.unit == SpecialtyUnit.BUILDINGS

        # rep2 is winner (latest business change time)
        assert rep2.is_current is True
        assert rep2.version_number == 2
        assert rep2.supersedes_id == rep1.id

        # rep1 is historical version
        assert rep1.is_current is False
        assert rep1.version_number == 1

        # Check traces
        trace1 = UnitReportMigrationTrace.objects.get(
            source_system='legacy_sub_report', source_id=str(rep1.id),
        )
        assert trace1.disposition == MigrationDisposition.HISTORICAL
        assert trace1.selected_current is False
        assert 'Displaced by current version' in trace1.resolution_reason

        trace2 = UnitReportMigrationTrace.objects.get(
            source_system='legacy_sub_report', source_id=str(rep2.id),
        )
        assert trace2.disposition == MigrationDisposition.MIGRATED
        assert trace2.selected_current is True

        # Check baseline events: rep2 has approved event, rep1 has submitted event
        ev2 = rep2.status_events.first()
        assert ev2 is not None
        assert ev2.event_type == UnitReportEventType.APPROVED

        ev1 = rep1.status_events.first()
        assert ev1 is not None
        assert ev1.event_type == UnitReportEventType.SUBMITTED

    def test_collision_resolution_tie_breaker_uses_stable_uuid(self, project, user):
        """When business change times are identical, higher UUID is deterministic tie-breaker."""
        same_time = timezone.now() - timedelta(hours=2)
        rep_a = _create_legacy_sub_report(
            project, user,
            discipline='civil',
            report_date='2026-10-16',
            status=SubReportStatus.DRAFT,
        )
        rep_b = _create_legacy_sub_report(
            project, user,
            discipline='finishing',
            report_date='2026-10-16',
            status=SubReportStatus.DRAFT,
        )
        DisciplineSubReport.objects.filter(id__in=[rep_a.id, rep_b.id]).update(
            created_at=same_time, updated_at=same_time,
        )
        # Give distinct content so they are not exact duplicates
        DisciplineSubReportActivity.objects.create(
            sub_report=rep_a, row_number=1, shift='day', crew_name='A', activity_description='Act A',
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=rep_b, row_number=1, shift='day', crew_name='B', activity_description='Act B',
        )

        expected_winner_id = max(rep_a.id, rep_b.id, key=lambda i: str(i))
        expected_loser_id = min(rep_a.id, rep_b.id, key=lambda i: str(i))

        migrate_legacy_sub_reports(project_id=project.id)

        winner = DisciplineSubReport.objects.get(id=expected_winner_id)
        loser = DisciplineSubReport.objects.get(id=expected_loser_id)

        assert winner.is_current is True
        assert winner.version_number == 2
        assert loser.is_current is False
        assert loser.version_number == 1

    def test_exact_duplicates_become_duplicate_alias(self, project, user):
        """Exact duplicates (e.g. civil and finishing with identical payload) become trace aliases and contribute only once."""
        rep1 = _create_legacy_sub_report(
            project, user,
            discipline='civil',
            report_date='2026-10-17',
            status=SubReportStatus.DRAFT,
            site_status='active',
        )
        # rep2 maps to same canonical unit ('finishing' -> 'buildings') with identical content
        rep2 = _create_legacy_sub_report(
            project, user,
            discipline='finishing',
            report_date='2026-10-17',
            status=SubReportStatus.DRAFT,
            site_status='active',
        )

        migrate_legacy_sub_reports(project_id=project.id)

        rep1.refresh_from_db()
        rep2.refresh_from_db()

        # Exactly one is current
        current_reports = [r for r in [rep1, rep2] if r.is_current]
        assert len(current_reports) == 1
        active_rep = current_reports[0]
        alias_rep = rep1 if active_rep.id == rep2.id else rep2

        alias_trace = UnitReportMigrationTrace.objects.get(
            source_system='legacy_sub_report', source_id=str(alias_rep.id),
        )
        assert alias_trace.disposition == MigrationDisposition.DUPLICATE_ALIAS
        assert alias_trace.target_report_id == active_rep.id
        assert alias_trace.selected_current is False

    def test_unknown_or_malformed_discipline_quarantined(self, project, user):
        """Unknown legacy discipline quarantined with stable reason code and never silently mapped."""
        rep = _create_legacy_sub_report(
            project, user,
            discipline='geotechnical',  # Not in canonical mapping
            report_date='2026-10-18',
        )

        migrate_legacy_sub_reports(project_id=project.id)

        rep.refresh_from_db()
        assert rep.unit is None
        assert rep.is_current is False

        trace = UnitReportMigrationTrace.objects.get(
            source_system='legacy_sub_report', source_id=str(rep.id),
        )
        assert trace.disposition == MigrationDisposition.QUARANTINED
        assert trace.canonical_unit is None

        quarantine = UnitReportMigrationQuarantine.objects.get(trace=trace)
        assert quarantine.reason_code == 'unknown_legacy_discipline'
        assert quarantine.raw_category == 'geotechnical'

    def test_unsafe_department_activity_quarantined(self, project, user):
        """DepartmentActivityRecord with unknown department is quarantined, row ID preserved."""
        dar = DepartmentActivityRecord.objects.create(
            project=project,
            department='unknown_department_xyz',
            date='2026-10-18',
            activity_description='Mystery task',
        )

        migrate_legacy_sub_reports(project_id=project.id)

        dar.refresh_from_db()
        assert dar.unit_report is None  # Not attached

        trace = UnitReportMigrationTrace.objects.get(
            source_system='inventory', source_id=str(dar.id),
        )
        assert trace.disposition == MigrationDisposition.QUARANTINED
        assert trace.canonical_unit is None

        quarantine = UnitReportMigrationQuarantine.objects.get(trace=trace)
        assert quarantine.reason_code == 'unsafe_department_attachment'


@pytest.mark.django_db(transaction=True)
class TestLinkAndRollback:
    """T063: Preservation of summary links and reversible rollback."""

    def test_linked_daily_report_preserved_after_migration(self, project, user):
        """Existing linked_daily_report relationships resolve after migration."""
        daily = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 19),
            status='draft',
            created_by=user,
        )
        rep = _create_legacy_sub_report(
            project, user,
            discipline='civil',
            report_date='2026-10-19',
            linked_daily_report=daily,
        )

        migrate_legacy_sub_reports(project_id=project.id)

        rep.refresh_from_db()
        assert rep.linked_daily_report_id == daily.id

        trace = UnitReportMigrationTrace.objects.get(
            source_system='legacy_sub_report', source_id=str(rep.id),
        )
        assert trace.original_link_id == str(daily.id)

    def test_rollback_reconstructs_original_categories_and_relationships(self, project, user):
        """Rollback from the trace reconstructs original values, current-version relationships, and summary links."""
        daily = DailyReport.objects.create(
            project=project,
            report_date=date(2026, 10, 20),
            status='draft',
            created_by=user,
        )
        rep1 = _create_legacy_sub_report(
            project, user,
            discipline='civil',
            report_date='2026-10-20',
            linked_daily_report=daily,
        )
        rep2 = _create_legacy_sub_report(
            project, user,
            discipline='finishing',
            report_date='2026-10-20',
        )
        dar = DepartmentActivityRecord.objects.create(
            project=project,
            department='buildings',
            date='2026-10-20',
            activity_description='Pre-rollback activity',
        )

        # Migrate
        migrate_legacy_sub_reports(project_id=project.id)

        rep1.refresh_from_db()
        rep2.refresh_from_db()
        dar.refresh_from_db()

        assert rep1.unit == SpecialtyUnit.BUILDINGS
        assert rep2.unit == SpecialtyUnit.BUILDINGS
        assert dar.unit_report is not None

        # Rollback
        rollback_unit_report_migration(project_id=project.id)

        rep1.refresh_from_db()
        rep2.refresh_from_db()
        dar.refresh_from_db()

        # Reconstructed pre-migration state
        assert rep1.discipline == 'civil'
        assert rep1.unit is None
        assert rep1.legacy_discipline == ''
        assert rep1.linked_daily_report_id == daily.id

        assert rep2.discipline == 'finishing'
        assert rep2.unit is None
        assert rep2.legacy_discipline == ''

        assert dar.unit_report is None

    def test_rehearsal_drill_management_command(self):
        """T070: Sanitized-dataset rehearsal and rollback drill via management command."""
        out = StringIO()
        call_command('rehearse_unit_report_migration', '--json', stdout=out)
        result = json.loads(out.getvalue())
        assert result['success'] is True
        assert result['forward_1']['success'] is True
        assert result['forward_2']['success'] is True
        assert result['forward_1']['accounting']['unaccounted_sub_reports'] == 0
        assert result['forward_1']['accounting']['unaccounted_activity_records'] == 0


@pytest.mark.django_db(transaction=True)
class TestConstraintMigrationT069:
    """T069: Database constraints enforcing canonical taxonomy and version invariants."""

    def test_product_visible_row_requires_valid_canonical_unit(self, project, user):
        """Current, non-deleted reports cannot have NULL unit."""
        from django.db import IntegrityError, transaction
        with pytest.raises(IntegrityError), transaction.atomic():
            DisciplineSubReport.objects.create(
                project=project,
                report_date='2026-11-10',
                discipline='civil',
                unit=None,
                is_current=True,
                is_deleted=False,
                created_by=user,
            )

    def test_supersedes_requires_version_gt_1(self, project, user):
        """Setting supersedes requires version_number > 1."""
        from django.db import IntegrityError, transaction
        parent = DisciplineSubReport.objects.create(
            project=project,
            report_date='2026-11-11',
            discipline='civil',
            unit=SpecialtyUnit.BUILDINGS,
            version_number=1,
            is_current=False,
            created_by=user,
        )
        with pytest.raises(IntegrityError), transaction.atomic():
            DisciplineSubReport.objects.create(
                project=project,
                report_date='2026-11-11',
                discipline='civil',
                unit=SpecialtyUnit.BUILDINGS,
                version_number=1,  # Must be > 1 to supersede
                supersedes=parent,
                is_current=True,
                created_by=user,
            )


@pytest.mark.django_db
class TestQuarantineAPI:
    """T067: Quarantine resolution surface for migration operators."""

    def test_non_operator_cannot_access_quarantine(self, project, user):
        client = APIClient()
        client.force_authenticate(user=user)
        res = client.get('/api/v1/unit-reports/quarantine/')
        # Regular member/user is not staff/admin
        assert res.status_code in (403, 404)

    def test_admin_can_list_and_resolve_quarantine(self, project):
        admin_user = User.objects.create_superuser(
            username='admin_operator',
            mobile='+989129999999',
            full_name='Admin Operator',
            password='adminpass123',
        )
        client = APIClient()
        client.force_authenticate(user=admin_user)

        rep = _create_legacy_sub_report(
            project, admin_user,
            discipline='unknown_category',
            report_date='2026-10-22',
        )
        migrate_legacy_sub_reports(project_id=project.id)

        quarantine = UnitReportMigrationQuarantine.objects.filter(
            raw_category='unknown_category',
        ).first()
        assert quarantine is not None

        # List
        res = client.get('/api/v1/unit-reports/quarantine/')
        assert res.status_code == 200
        assert len(res.data) >= 1

        # Resolve
        resolve_url = f'/api/v1/unit-reports/quarantine/{quarantine.id}/resolve/'
        resolve_res = client.post(resolve_url, {'resolution_notes': 'Reviewed and confirmed invalid'})
        assert resolve_res.status_code == 200

        quarantine.refresh_from_db()
        assert quarantine.resolved_by == admin_user
        assert quarantine.resolved_at is not None
        assert quarantine.resolution_notes == 'Reviewed and confirmed invalid'
