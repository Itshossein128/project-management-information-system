"""Migration services for Phase 8 / US6: Migrate legacy reports without losing history.

Implements:
- FR-004: Mapping rules (civil/finishing -> buildings, plumbing/hvac/mechanical -> mechanical,
          electrical -> electrical; no inference for machinery/warehouse/security).
- FR-033/034: 100% accounting, link preservation, and normalization before constraints.
- FR-035: Collision resolution via latest business change time then stable UUID tie-breaker.
- FR-036: Exact duplicate alias consolidation.
- FR-037: Quarantine for unknown/malformed legacy disciplines and unsafe attachments.
- FR-038: Rollback reconstruction from trace ledger.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from collections import defaultdict
from datetime import date, datetime
from typing import Any

from django.db import transaction
from django.utils import timezone

from common.reporting_units import SpecialtyUnit
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

LEGACY_DISCIPLINE_TO_CANONICAL_UNIT = {
    'civil': SpecialtyUnit.BUILDINGS,
    'finishing': SpecialtyUnit.BUILDINGS,
    'plumbing': SpecialtyUnit.MECHANICAL,
    'hvac': SpecialtyUnit.MECHANICAL,
    'electrical': SpecialtyUnit.ELECTRICAL,
    'mechanical': SpecialtyUnit.MECHANICAL,
}

CANONICAL_UNIT_TO_FALLBACK_DISCIPLINE = {
    SpecialtyUnit.BUILDINGS: Discipline.CIVIL,
    SpecialtyUnit.ELECTRICAL: Discipline.ELECTRICAL,
    SpecialtyUnit.MECHANICAL: Discipline.MECHANICAL,
    SpecialtyUnit.MACHINERY: Discipline.MECHANICAL,
    SpecialtyUnit.WAREHOUSE: Discipline.MECHANICAL,
    SpecialtyUnit.SECURITY: Discipline.CIVIL,
}


def _json_serial(obj: Any) -> Any:
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f'Type {type(obj)} not serializable')


def compute_legacy_report_snapshot_and_checksum(
    report: DisciplineSubReport,
    canonical_unit: str | None = None,
) -> tuple[dict, str]:
    """Capture complete state snapshot and stable SHA256 checksum of a legacy report.

    Checksum uses canonical_unit to identify identical payload across legacy disciplines
    (e.g. civil vs finishing with identical data mapping to buildings).
    """
    mapped_unit = canonical_unit or LEGACY_DISCIPLINE_TO_CANONICAL_UNIT.get(report.discipline) or report.unit or report.discipline
    activities = [
        {
            'id': str(a.id),
            'row_number': a.row_number,
            'shift': a.shift,
            'crew_name': a.crew_name,
            'activity_description': a.activity_description,
            'unit': a.unit or '',
            'quantity': str(a.quantity) if a.quantity is not None else None,
            'execution_percentage': str(a.execution_percentage) if a.execution_percentage is not None else None,
            'zone': a.zone or '',
            'block': a.block or '',
            'floor': a.floor or '',
        }
        for a in report.activities.filter(is_deleted=False).order_by('row_number', 'id')
    ]

    labor = [
        {
            'id': str(l.id),
            'labor_category': l.labor_category,
            'job_title': l.job_title,
            'present_count': l.present_count,
            'leave_count': l.leave_count,
        }
        for l in report.labor_entries.filter(is_deleted=False).order_by('id')
    ]

    materials = [
        {
            'id': str(m.id),
            'material_description': m.material_description,
            'quantity': str(m.quantity),
            'unit': m.unit,
            'notes': m.notes,
        }
        for m in report.material_entries.filter(is_deleted=False).order_by('id')
    ]

    concrete = [
        {
            'id': str(c.id),
            'concrete_description': c.concrete_description,
            'volume_m3': str(c.volume_m3),
            'zone': c.zone or '',
            'block': c.block or '',
            'floor': c.floor or '',
            'notes': c.notes,
        }
        for c in report.concrete_entries.filter(is_deleted=False).order_by('id')
    ]

    general_activities = [
        {
            'id': str(g.id),
            'activity_description': g.activity_description,
            'location': g.location,
            'quantity': str(g.quantity) if g.quantity is not None else None,
            'unit': g.unit or '',
            'notes': g.notes,
        }
        for g in report.general_activities.filter(is_deleted=False).order_by('id')
    ]

    notes = [
        {
            'id': str(n.id),
            'note_type': n.note_type,
            'text': n.text,
            'row_number': n.row_number,
        }
        for n in report.notes.filter(is_deleted=False).order_by('row_number', 'id')
    ]

    # Deterministic content dictionary for deduplication & hashing
    content_payload = {
        'project_id': str(report.project_id),
        'report_date': report.report_date.isoformat(),
        'canonical_unit': mapped_unit,
        'status': report.status,
        'weather_condition': report.weather_condition,
        'site_status': report.site_status,
        'form_code': report.form_code,
        'revision_number': report.revision_number,
        'rejection_reason': report.rejection_reason,
        'activities': activities,
        'labor': labor,
        'materials': materials,
        'concrete': concrete,
        'general_activities': general_activities,
        'notes': notes,
    }

    serialized = json.dumps(content_payload, sort_keys=True, default=_json_serial)
    checksum = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    snapshot = {
        'id': str(report.id),
        'lineage_id': str(report.lineage_id) if report.lineage_id else None,
        'version_number': report.version_number,
        'is_current': report.is_current,
        'supersedes_id': str(report.supersedes_id) if report.supersedes_id else None,
        'linked_daily_report_id': str(report.linked_daily_report_id) if report.linked_daily_report_id else None,
        'created_at': report.created_at.isoformat() if hasattr(report, 'created_at') and report.created_at else None,
        'updated_at': report.updated_at.isoformat() if hasattr(report, 'updated_at') and report.updated_at else None,
        'content': content_payload,
    }

    return snapshot, checksum


def get_business_change_time(report: DisciplineSubReport) -> datetime:
    """Determine latest business change time across all review and audit timestamps."""
    timestamps = [
        report.approved_at,
        report.submitted_at,
        report.rejected_at,
        getattr(report, 'updated_at', None),
        getattr(report, 'created_at', None),
    ]
    valid = [t for t in timestamps if t is not None]
    return max(valid) if valid else timezone.now()


def create_baseline_status_event(report: DisciplineSubReport) -> UnitReportStatusEvent | None:
    """Create a baseline status event describing only evidence present at migration time.

    No fabricated pre-feature transitions (data-model §5).
    """
    if report.status_events.exists():
        return None

    status_to_event = {
        SubReportStatus.DRAFT: UnitReportEventType.CREATED,
        SubReportStatus.SUBMITTED: UnitReportEventType.SUBMITTED,
        SubReportStatus.APPROVED: UnitReportEventType.APPROVED,
        SubReportStatus.REJECTED: UnitReportEventType.REJECTED,
    }
    event_type = status_to_event.get(report.status, UnitReportEventType.CREATED)

    actor = None
    occurred_at = None
    reason = ''

    if report.status == SubReportStatus.APPROVED:
        actor = report.approved_by or report.submitted_by
        occurred_at = report.approved_at or report.submitted_at
    elif report.status == SubReportStatus.SUBMITTED:
        actor = report.submitted_by
        occurred_at = report.submitted_at
    elif report.status == SubReportStatus.REJECTED:
        actor = report.rejected_by
        occurred_at = report.rejected_at
        reason = report.rejection_reason or ''
    elif report.status == SubReportStatus.DRAFT:
        actor = getattr(report, 'created_by', None)
        occurred_at = getattr(report, 'created_at', None)

    if not occurred_at:
        occurred_at = getattr(report, 'updated_at', None) or getattr(report, 'created_at', None) or timezone.now()

    return UnitReportStatusEvent.objects.create(
        report_version=report,
        from_status='',
        to_status=report.status,
        actor=actor,
        occurred_at=occurred_at,
        reason=reason,
        event_type=event_type,
    )


@transaction.atomic
def migrate_legacy_sub_reports(project_id: uuid.UUID | str | None = None) -> dict[str, int]:
    """Execute backfill of legacy reports into canonical unit taxonomy.

    Resolves collisions, snapshots traces, and attaches activity records.
    Idempotent and resumable.
    """
    qs = DisciplineSubReport.all_objects.all()
    if project_id:
        qs = qs.filter(project_id=project_id)

    # 1. Separate mappable legacy reports from unknown disciplines
    groups: dict[tuple, list[DisciplineSubReport]] = defaultdict(list)
    quarantined_reports: list[DisciplineSubReport] = []

    for report in qs:
        # Determine canonical unit
        canonical_unit = LEGACY_DISCIPLINE_TO_CANONICAL_UNIT.get(report.discipline)
        if not canonical_unit and report.unit:
            canonical_unit = report.unit

        if not canonical_unit:
            quarantined_reports.append(report)
        else:
            groups[(report.project_id, report.report_date, canonical_unit)].append(report)

    # 2. Process quarantined reports
    for rep in quarantined_reports:
        snapshot, checksum = compute_legacy_report_snapshot_and_checksum(rep)
        rep.is_current = False
        rep.unit = None
        rep.save(update_fields=['is_current', 'unit'])

        trace, _ = UnitReportMigrationTrace.objects.update_or_create(
            source_system='legacy_sub_report',
            source_model='DisciplineSubReport',
            source_id=str(rep.id),
            defaults={
                'original_category': str(rep.discipline),
                'original_deleted': rep.is_deleted,
                'original_link_id': str(rep.linked_daily_report_id or ''),
                'canonical_unit': None,
                'target_report': rep,
                'selected_current': False,
                'disposition': MigrationDisposition.QUARANTINED,
                'resolution_reason': f'Unknown legacy discipline: {rep.discipline}',
                'source_checksum': checksum,
                'snapshot': snapshot,
            },
        )

        UnitReportMigrationQuarantine.objects.update_or_create(
            trace=trace,
            defaults={
                'reason_code': 'unknown_legacy_discipline',
                'raw_category': str(rep.discipline),
                'raw_payload': snapshot,
            },
        )

    # 3. Process collision groups
    for (proj_id, r_date, canon_unit), reports in groups.items():
        # First check for exact duplicates (identical content checksum)
        checksum_map: dict[str, list[DisciplineSubReport]] = defaultdict(list)
        checksum_snapshots = {}

        for rep in reports:
            snap, csum = compute_legacy_report_snapshot_and_checksum(rep, canonical_unit=canon_unit)
            checksum_map[csum].append(rep)
            checksum_snapshots[rep.id] = (snap, csum)

        candidates: list[DisciplineSubReport] = []
        duplicate_aliases: list[tuple[DisciplineSubReport, DisciplineSubReport]] = []

        for csum, matching_reports in checksum_map.items():
            if len(matching_reports) == 1:
                candidates.append(matching_reports[0])
            else:
                # Pick the representative by highest business change time then UUID
                matching_reports.sort(key=lambda r: (get_business_change_time(r), str(r.id)))
                representative = matching_reports[-1]
                candidates.append(representative)
                for dup in matching_reports[:-1]:
                    duplicate_aliases.append((dup, representative))

        # Handle duplicate aliases
        for dup, rep_target in duplicate_aliases:
            snap, csum = checksum_snapshots[dup.id]
            dup.is_current = False
            dup.unit = canon_unit
            dup.legacy_discipline = dup.discipline
            dup.save(update_fields=['is_current', 'unit', 'legacy_discipline'])

            UnitReportMigrationTrace.objects.update_or_create(
                source_system='legacy_sub_report',
                source_model='DisciplineSubReport',
                source_id=str(dup.id),
                defaults={
                    'original_category': dup.discipline,
                    'original_deleted': dup.is_deleted,
                    'original_link_id': str(dup.linked_daily_report_id or ''),
                    'canonical_unit': canon_unit,
                    'target_report': rep_target,
                    'selected_current': False,
                    'disposition': MigrationDisposition.DUPLICATE_ALIAS,
                    'resolution_reason': f'Exact duplicate alias of report {rep_target.id}',
                    'source_checksum': csum,
                    'snapshot': snap,
                },
            )

        # Sort remaining candidates by business change time then stable UUID
        candidates.sort(key=lambda r: (get_business_change_time(r), str(r.id)))
        shared_lineage_id = candidates[0].lineage_id or uuid.uuid4()
        winner = candidates[-1]

        for idx, rep in enumerate(candidates, start=1):
            snap, csum = checksum_snapshots[rep.id]
            is_winner = (idx == len(candidates))
            version_number = idx
            prev_rep = candidates[idx - 2] if idx > 1 else None

            rep.lineage_id = shared_lineage_id
            rep.version_number = version_number
            rep.unit = canon_unit
            rep.legacy_discipline = rep.discipline
            if prev_rep:
                rep.supersedes = prev_rep

            if is_winner:
                rep.is_current = not rep.is_deleted
                selected_current = True
                disposition = MigrationDisposition.MIGRATED
                reason = f'Selected as current version via latest business change time ({get_business_change_time(rep)})'
            else:
                rep.is_current = False
                selected_current = False
                disposition = MigrationDisposition.HISTORICAL
                reason = f'Displaced by current version {winner.id} via latest business change time'

            rep.save(update_fields=['lineage_id', 'version_number', 'unit', 'legacy_discipline', 'supersedes', 'is_current'])
            create_baseline_status_event(rep)

            trace, _ = UnitReportMigrationTrace.objects.update_or_create(
                source_system='legacy_sub_report',
                source_model='DisciplineSubReport',
                source_id=str(rep.id),
                defaults={
                    'original_category': rep.discipline,
                    'original_deleted': rep.is_deleted,
                    'original_link_id': str(rep.linked_daily_report_id or ''),
                    'canonical_unit': canon_unit,
                    'target_report': rep,
                    'lineage_id': shared_lineage_id,
                    'version_number': version_number,
                    'selected_current': selected_current,
                    'disposition': disposition,
                    'resolution_reason': reason,
                    'source_checksum': csum,
                    'snapshot': snap,
                },
            )

            # Trace child activity rows for 100% accounting
            for act in rep.activities.all():
                UnitReportMigrationTrace.objects.update_or_create(
                    source_system='legacy_sub_report',
                    source_model='DisciplineSubReportActivity',
                    source_id=str(act.id),
                    defaults={
                        'original_category': rep.discipline,
                        'original_deleted': act.is_deleted,
                        'canonical_unit': canon_unit,
                        'target_report': rep,
                        'disposition': disposition,
                        'resolution_reason': f'Child activity row of report {rep.id}',
                    },
                )

    # 4. Process DepartmentActivityRecord rows (T065)
    dar_qs = DepartmentActivityRecord.objects.all()
    if project_id:
        dar_qs = dar_qs.filter(project_id=project_id)

    for dar in dar_qs:
        if dar.department in SpecialtyUnit.values:
            # Look for existing current unit report
            current_rep = DisciplineSubReport.objects.filter(
                project_id=dar.project_id,
                report_date=dar.date,
                unit=dar.department,
                is_current=True,
                is_deleted=False,
            ).first()

            if current_rep:
                dar.unit_report = current_rep
                dar.save(update_fields=['unit_report'])
                UnitReportMigrationTrace.objects.update_or_create(
                    source_system='inventory',
                    source_model='DepartmentActivityRecord',
                    source_id=str(dar.id),
                    defaults={
                        'original_category': dar.department,
                        'canonical_unit': dar.department,
                        'target_report': current_rep,
                        'disposition': MigrationDisposition.MIGRATED,
                        'resolution_reason': f'Attached to existing unit report {current_rep.id}',
                    },
                )
            else:
                # Create traced draft lineage when no report exists
                draft_rep = DisciplineSubReport.objects.create(
                    project=dar.project,
                    report_date=dar.date,
                    unit=dar.department,
                    discipline=CANONICAL_UNIT_TO_FALLBACK_DISCIPLINE.get(dar.department, Discipline.CIVIL),
                    legacy_discipline='',
                    lineage_id=uuid.uuid4(),
                    version_number=1,
                    is_current=True,
                    status=SubReportStatus.DRAFT,
                )
                create_baseline_status_event(draft_rep)
                snap, csum = compute_legacy_report_snapshot_and_checksum(draft_rep)
                UnitReportMigrationTrace.objects.update_or_create(
                    source_system='legacy_sub_report',
                    source_model='DisciplineSubReport',
                    source_id=str(draft_rep.id),
                    defaults={
                        'original_category': dar.department,
                        'canonical_unit': dar.department,
                        'target_report': draft_rep,
                        'lineage_id': draft_rep.lineage_id,
                        'version_number': 1,
                        'selected_current': True,
                        'disposition': MigrationDisposition.MIGRATED,
                        'resolution_reason': 'Created draft lineage to host legacy activity records',
                        'source_checksum': csum,
                        'snapshot': snap,
                    },
                )
                dar.unit_report = draft_rep
                dar.save(update_fields=['unit_report'])
                UnitReportMigrationTrace.objects.update_or_create(
                    source_system='inventory',
                    source_model='DepartmentActivityRecord',
                    source_id=str(dar.id),
                    defaults={
                        'original_category': dar.department,
                        'canonical_unit': dar.department,
                        'target_report': draft_rep,
                        'disposition': MigrationDisposition.MIGRATED,
                        'resolution_reason': f'Attached to newly created draft report {draft_rep.id}',
                    },
                )
        else:
            # Unsafe department category -> quarantine
            trace, _ = UnitReportMigrationTrace.objects.update_or_create(
                source_system='inventory',
                source_model='DepartmentActivityRecord',
                source_id=str(dar.id),
                defaults={
                    'original_category': str(dar.department),
                    'canonical_unit': None,
                    'target_report': None,
                    'selected_current': False,
                    'disposition': MigrationDisposition.QUARANTINED,
                    'resolution_reason': f'Unsafe department attachment: {dar.department}',
                },
            )
            UnitReportMigrationQuarantine.objects.update_or_create(
                trace=trace,
                defaults={
                    'reason_code': 'unsafe_department_attachment',
                    'raw_category': str(dar.department),
                    'raw_payload': {'id': str(dar.id), 'department': dar.department, 'date': str(dar.date)},
                },
            )

    return {
        'total_traces': UnitReportMigrationTrace.objects.count(),
        'quarantined': UnitReportMigrationQuarantine.objects.count(),
    }


@transaction.atomic
def rollback_unit_report_migration(project_id: uuid.UUID | str | None = None) -> None:
    """Reconstruct original categories, links, and current-version relationships from trace ledger.

    (FR-038 / data-model Migration and Rollback Invariants).
    """
    trace_qs = UnitReportMigrationTrace.objects.all()
    if project_id:
        trace_qs = trace_qs.filter(
            target_report__project_id=project_id,
        )

    # 1. Restore DepartmentActivityRecord attachments
    dar_traces = trace_qs.filter(source_model='DepartmentActivityRecord')
    for trace in dar_traces:
        dar = DepartmentActivityRecord.objects.filter(id=trace.source_id).first()
        if dar:
            dar.unit_report = None
            dar.save(update_fields=['unit_report'])

    # 2. Restore DisciplineSubReport records
    rep_traces = trace_qs.filter(source_model='DisciplineSubReport')
    for trace in rep_traces:
        rep = DisciplineSubReport.all_objects.filter(id=trace.source_id).first()
        if rep:
            rep.discipline = trace.original_category
            rep.unit = None
            rep.legacy_discipline = ''
            if trace.snapshot:
                rep.lineage_id = trace.snapshot.get('lineage_id')
                rep.version_number = trace.snapshot.get('version_number', 1)
                rep.is_current = trace.snapshot.get('is_current', True)
                rep.supersedes_id = trace.snapshot.get('supersedes_id')
            if trace.original_link_id:
                rep.linked_daily_report_id = trace.original_link_id
            else:
                rep.linked_daily_report_id = None
            rep.is_deleted = trace.original_deleted
            rep.save()

    # 3. Clean up migration status events
    UnitReportStatusEvent.objects.filter(
        report_version__migration_traces__in=rep_traces,
    ).delete()

    # 4. Clean up traces and quarantines
    UnitReportMigrationQuarantine.objects.filter(trace__in=trace_qs).delete()
    trace_qs.delete()
