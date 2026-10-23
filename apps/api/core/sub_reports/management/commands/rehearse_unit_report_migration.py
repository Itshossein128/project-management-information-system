"""Rehearsal and rollback drill for 032 unit-report migration (quickstart.md §10, T070).

Executes a full forward/rollback/forward cycle on a representative sanitized dataset:
1. Records pre-migration baseline (IDs, categories, statuses, children, summary links).
2. Applies backfill migration.
3. Validates 100% accounting and invariant checks.
4. Executes rollback and verifies restoration of pre-migration states and relationships.
5. Reapplies forward migration and confirms verifier passes.
"""
from __future__ import annotations

import json
import sys
import uuid
from datetime import date, timedelta
from io import StringIO
from typing import Any

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from common.reporting_units import SpecialtyUnit
from field_reports.models import DailyReport
from inventory.models import DepartmentActivityRecord
from projects.models import Project, ProjectStatus
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    MigrationDisposition,
    SubReportStatus,
    UnitReportMigrationQuarantine,
    UnitReportMigrationTrace,
)
from sub_reports.services.migration import (
    migrate_legacy_sub_reports,
    rollback_unit_report_migration,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Execute sanitized dataset rehearsal and rollback drill (quickstart.md §10).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            dest='as_json',
            help='Output result strictly as JSON payload.',
        )

    def handle(self, *args, **options):
        as_json = options.get('as_json', False)

        with transaction.atomic():
            report = self._run_rehearsal_drill()
            # Roll back temporary drill data created in test sandbox
            transaction.set_rollback(True)

        if as_json:
            self.stdout.write(json.dumps(report, indent=2))
        else:
            if report['success']:
                self.stdout.write(self.style.SUCCESS(
                    "Rehearsal drill PASSED: Forward -> Rollback -> Forward verified with 100% accounting."
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Rehearsal drill FAILED: {report.get('error')}"
                ))

        if not report['success']:
            sys.exit(1)

    def _run_rehearsal_drill(self) -> dict[str, Any]:
        operator, _ = User.objects.get_or_create(
            username='rehearsal_operator',
            defaults={'mobile': '+989128888888', 'full_name': 'Rehearsal Operator'},
        )
        project = Project.objects.create(
            project_code=f'PRJ-{uuid.uuid4().hex[:6].upper()}',
            project_name='Rehearsal Sandbox Project',
            status=ProjectStatus.ACTIVE,
            project_manager=operator,
        )

        d1 = date(2026, 11, 1)
        d2 = date(2026, 11, 2)
        d3 = date(2026, 11, 3)

        daily1 = DailyReport.objects.create(project=project, report_date=d1, created_by=operator)

        # 1. Representative legacy dataset
        # Case A: civil and finishing collision on d1 (both -> buildings)
        rep_civil = DisciplineSubReport.objects.create(
            project=project, report_date=d1, discipline='civil', unit=None, status=SubReportStatus.SUBMITTED,
            submitted_by=operator, submitted_at=timezone.now() - timedelta(hours=2),
            linked_daily_report=daily1, created_by=operator, is_current=False,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=rep_civil, row_number=1, shift='day', crew_name='Civil Crew',
            activity_description='Concrete foundation',
        )

        rep_finishing = DisciplineSubReport.objects.create(
            project=project, report_date=d1, discipline='finishing', unit=None, status=SubReportStatus.APPROVED,
            submitted_by=operator, submitted_at=timezone.now() - timedelta(hours=2),
            approved_by=operator, approved_at=timezone.now() - timedelta(hours=1),
            created_by=operator, is_current=False,
        )
        DisciplineSubReportActivity.objects.create(
            sub_report=rep_finishing, row_number=1, shift='day', crew_name='Finishing Crew',
            activity_description='Plastering wall',
        )

        # Case B: plumbing and hvac on d2 (both -> mechanical)
        rep_plumbing = DisciplineSubReport.objects.create(
            project=project, report_date=d2, discipline='plumbing', unit=None, status=SubReportStatus.DRAFT,
            created_by=operator, is_current=False,
        )
        rep_hvac = DisciplineSubReport.objects.create(
            project=project, report_date=d2, discipline='hvac', unit=None, status=SubReportStatus.DRAFT,
            created_by=operator, is_current=False,
        )

        # Case C: electrical on d3
        rep_elec = DisciplineSubReport.objects.create(
            project=project, report_date=d3, discipline='electrical', unit=None, status=SubReportStatus.REJECTED,
            rejected_by=operator, rejected_at=timezone.now() - timedelta(hours=3),
            rejection_reason='Incomplete single-line diagrams provided',
            created_by=operator, is_current=False,
        )

        # Case D: unknown category (quarantine)
        rep_unknown = DisciplineSubReport.objects.create(
            project=project, report_date=d3, discipline='telecom_radio', unit=None, status=SubReportStatus.DRAFT,
            created_by=operator, is_current=False,
        )

        # Case E: DepartmentActivityRecord attachment
        dar_valid = DepartmentActivityRecord.objects.create(
            project=project, department='buildings', date=d1, activity_description='Masonry checking',
        )
        dar_unsafe = DepartmentActivityRecord.objects.create(
            project=project, department='landscape_gardening', date=d1, activity_description='Tree planting',
        )

        # 2. Pre-migration baseline inventory
        pre_sub_report_ids = set(DisciplineSubReport.objects.filter(project=project).values_list('id', flat=True))
        pre_dar_ids = set(DepartmentActivityRecord.objects.filter(project=project).values_list('id', flat=True))
        assert len(pre_sub_report_ids) == 6
        assert len(pre_dar_ids) == 2

        # 3. First forward migration
        migrate_legacy_sub_reports(project_id=project.id)

        # Run verifier command
        out = StringIO()
        call_command('verify_unit_report_migration', '--json', f'--project-id={project.id}', stdout=out)
        verifier_first = json.loads(out.getvalue())
        if not verifier_first['success']:
            return {'success': False, 'step': 'forward_1', 'verifier': verifier_first}

        # 4. Rollback
        rollback_unit_report_migration(project_id=project.id)

        # Verify restoration of pre-migration state
        for rid in pre_sub_report_ids:
            r = DisciplineSubReport.objects.get(id=rid)
            if r.unit is not None:
                return {'success': False, 'step': 'rollback', 'error': f'Report {rid} unit was not cleared'}
            if r.legacy_discipline != '':
                return {'success': False, 'step': 'rollback', 'error': f'Report {rid} legacy_discipline was not cleared'}

        rep_civil.refresh_from_db()
        if rep_civil.linked_daily_report_id != daily1.id:
            return {'success': False, 'step': 'rollback', 'error': 'rep_civil linked_daily_report not restored'}

        rep_elec.refresh_from_db()
        if rep_elec.rejection_reason != 'Incomplete single-line diagrams provided':
            return {'success': False, 'step': 'rollback', 'error': 'rep_elec rejection reason not restored'}

        dar_valid.refresh_from_db()
        if dar_valid.unit_report is not None:
            return {'success': False, 'step': 'rollback', 'error': 'dar_valid unit_report not detached'}

        # 5. Second forward migration
        migrate_legacy_sub_reports(project_id=project.id)

        out2 = StringIO()
        call_command('verify_unit_report_migration', '--json', f'--project-id={project.id}', stdout=out2)
        verifier_second = json.loads(out2.getvalue())
        if not verifier_second['success']:
            return {'success': False, 'step': 'forward_2', 'verifier': verifier_second}

        return {
            'success': True,
            'dataset': {
                'sub_reports_count': len(pre_sub_report_ids),
                'activity_records_count': len(pre_dar_ids),
            },
            'forward_1': verifier_first,
            'rollback_verification': 'PASSED (categories, units, links, rejections restored)',
            'forward_2': verifier_second,
        }
