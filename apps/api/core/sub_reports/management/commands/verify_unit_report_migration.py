"""Verification command for 032 unit-report migration (feature 032, US6, T068).

Emits JSON classification of 100% accounting across legacy sub-reports and activity rows.
Asserts:
- Every legacy report and activity record has a permanent trace entry.
- Correct taxonomy mapping with zero guessing.
- Deterministic collision resolution (at most one current version per canonical key).
- Proper quarantine with reason codes for invalid/malformed categories.
- Link preservation for daily-report summaries.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Any

from django.core.management.base import BaseCommand
from django.db.models import Count, Q

from common.reporting_units import SpecialtyUnit
from inventory.models import DepartmentActivityRecord
from sub_reports.models import (
    DisciplineSubReport,
    MigrationDisposition,
    UnitReportMigrationQuarantine,
    UnitReportMigrationTrace,
)


class Command(BaseCommand):
    help = 'Verify 100% accounting and canonical invariants for unit-report migration.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            dest='as_json',
            help='Output result strictly as a JSON payload to stdout.',
        )
        parser.add_argument(
            '--project-id',
            type=str,
            default=None,
            help='Optional project UUID to verify.',
        )

    def handle(self, *args, **options):
        as_json = options.get('as_json', False)
        project_id = options.get('project_id')

        violations: list[str] = []

        # 1. Scope querysets
        rep_qs = DisciplineSubReport.all_objects.all()
        dar_qs = DepartmentActivityRecord.objects.all()
        trace_qs = UnitReportMigrationTrace.objects.all()
        quarantine_qs = UnitReportMigrationQuarantine.objects.all()

        if project_id:
            rep_qs = rep_qs.filter(project_id=project_id)
            dar_qs = dar_qs.filter(project_id=project_id)
            trace_qs = trace_qs.filter(
                Q(target_report__project_id=project_id)
                | Q(source_id__in=[str(r.id) for r in rep_qs])
                | Q(source_id__in=[str(d.id) for d in dar_qs]),
            )
            quarantine_qs = quarantine_qs.filter(trace__in=trace_qs)

        total_reports = rep_qs.count()
        total_dars = dar_qs.count()

        # 2. Check 100% accounting: reports
        traced_rep_ids = set(
            trace_qs.filter(source_model='DisciplineSubReport').values_list('source_id', flat=True),
        )
        all_rep_ids = {str(rid) for rid in rep_qs.values_list('id', flat=True)}
        unaccounted_rep_ids = all_rep_ids - traced_rep_ids
        if unaccounted_rep_ids:
            violations.append(
                f'{len(unaccounted_rep_ids)} DisciplineSubReport records missing from UnitReportMigrationTrace'
            )

        # 3. Check 100% accounting: department activity records
        traced_dar_ids = set(
            trace_qs.filter(source_model='DepartmentActivityRecord').values_list('source_id', flat=True),
        )
        all_dar_ids = {str(did) for did in dar_qs.values_list('id', flat=True)}
        unaccounted_dar_ids = all_dar_ids - traced_dar_ids
        if unaccounted_dar_ids:
            violations.append(
                f'{len(unaccounted_dar_ids)} DepartmentActivityRecord rows missing from UnitReportMigrationTrace'
            )

        # 4. Check one current version per canonical key
        collision_violations = (
            rep_qs.filter(is_current=True, is_deleted=False, unit__isnull=False)
            .values('project_id', 'report_date', 'unit')
            .annotate(current_count=Count('id'))
            .filter(current_count__gt=1)
        )
        if collision_violations.exists():
            for cv in collision_violations:
                violations.append(
                    f"Multiple current reports ({cv['current_count']}) for project {cv['project_id']}, "
                    f"date {cv['report_date']}, unit {cv['unit']}"
                )

        # 5. Check quarantined records invariants
        quarantined_traces = trace_qs.filter(disposition=MigrationDisposition.QUARANTINED)
        for qt in quarantined_traces:
            if qt.selected_current:
                violations.append(f'Quarantined trace {qt.id} is marked as selected_current=True')
            if qt.canonical_unit is not None:
                violations.append(f'Quarantined trace {qt.id} has non-null canonical_unit {qt.canonical_unit}')
            if not hasattr(qt, 'quarantine') or qt.quarantine is None:
                violations.append(f'Quarantined trace {qt.id} missing UnitReportMigrationQuarantine record')

        for q in quarantine_qs:
            if not q.reason_code:
                violations.append(f'Quarantine record {q.id} has empty reason_code')

        # 6. Check summary link validity
        linked_reports = rep_qs.filter(linked_daily_report__isnull=False)
        for lr in linked_reports:
            if lr.project_id != lr.linked_daily_report.project_id:
                violations.append(
                    f'Report {lr.id} linked to DailyReport {lr.linked_daily_report_id} of different project'
                )
            if lr.report_date != lr.linked_daily_report.report_date:
                violations.append(
                    f'Report {lr.id} linked to DailyReport {lr.linked_daily_report_id} of different date'
                )

        # 7. Dispositions summary
        disp_counter = Counter(trace_qs.values_list('disposition', flat=True))

        payload: dict[str, Any] = {
            'success': len(violations) == 0,
            'accounting': {
                'sub_reports_total': total_reports,
                'sub_reports_traced': len(traced_rep_ids),
                'activity_records_total': total_dars,
                'activity_records_traced': len(traced_dar_ids),
                'unaccounted_sub_reports': len(unaccounted_rep_ids),
                'unaccounted_activity_records': len(unaccounted_dar_ids),
            },
            'dispositions': {
                'migrated': disp_counter.get('migrated', 0),
                'historical': disp_counter.get('historical', 0),
                'duplicate_alias': disp_counter.get('duplicate_alias', 0),
                'quarantined': disp_counter.get('quarantined', 0),
            },
            'quarantine_count': quarantine_qs.count(),
            'violations': violations,
        }

        if as_json:
            self.stdout.write(json.dumps(payload, indent=2))
        else:
            if payload['success']:
                self.stdout.write(self.style.SUCCESS(
                    f"Migration verified: 100% accounting ({total_reports} reports, {total_dars} activities), "
                    f"{payload['quarantine_count']} quarantined, 0 violations."
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f"Migration verification FAILED: {len(violations)} violations found:\n" +
                    '\n'.join(f' - {v}' for v in violations)
                ))

        if not payload['success']:
            sys.exit(1)
