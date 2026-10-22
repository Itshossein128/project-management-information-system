"""Ensure and rebuild project daily-report summaries from specialty sub-reports."""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from django.db import transaction
from django.utils import timezone

from field_reports.models import (
    ActivityRowShift,
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportLabor,
    DailyReportMaterial,
    InactivityReason,
    MaterialTransactionType,
    ReportShift,
    SiteStatus,
    WeatherCondition,
)
from sub_reports.models import (
    DEFAULT_EXPECTED_DISCIPLINES,
    DisciplineSubReport,
    SubReportNoteType,
    SubReportStatus,
)

INCLUDE_STATUSES = {SubReportStatus.SUBMITTED, SubReportStatus.APPROVED}

WEATHER_SEVERITY = {
    WeatherCondition.STORMY: 50,
    WeatherCondition.SNOWY: 40,
    WeatherCondition.RAINY: 30,
    WeatherCondition.CLOUDY: 20,
    WeatherCondition.CLEAR: 10,
}


def contributing_sub_reports(project_id, report_date: date):
    return (
        DisciplineSubReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            is_deleted=False,
            status__in=INCLUDE_STATUSES,
        )
        .prefetch_related(
            'activities',
            'labor_entries',
            'material_entries',
            'concrete_entries',
            'general_activities',
            'notes',
        )
        .order_by('discipline')
    )


def build_aggregation_meta(project_id, report_date: date, report: DailyReport | None = None) -> dict:
    expected = [d.value for d in DEFAULT_EXPECTED_DISCIPLINES]
    contributing = list(
        contributing_sub_reports(project_id, report_date).values_list('discipline', flat=True),
    )
    contributing = sorted(set(contributing))
    missing = [d for d in expected if d not in contributing]
    return {
        'is_auto_summary': bool(report.is_auto_summary) if report else True,
        'aggregated_at': report.aggregated_at.isoformat().replace('+00:00', 'Z') if report and report.aggregated_at else None,
        'is_partial': len(contributing) == 0 or len(missing) > 0,
        'expected_disciplines': expected,
        'contributing_disciplines': contributing,
        'missing_disciplines': missing,
        'weather_source': 'override' if report and report.weather_override else 'derived',
        'site_status_source': 'override' if report and report.site_status_override else 'derived',
    }


def _normalize_shift(raw: str) -> str:
    value = (raw or '').strip().lower().replace(' ', '_')
    mapping = {
        'shift_1': ActivityRowShift.SHIFT_1,
        'shift1': ActivityRowShift.SHIFT_1,
        'شیفت1': ActivityRowShift.SHIFT_1,
        'شیفت_1': ActivityRowShift.SHIFT_1,
        'shift_2': ActivityRowShift.SHIFT_2,
        'shift2': ActivityRowShift.SHIFT_2,
        'shift_3': ActivityRowShift.SHIFT_3,
        'shift3': ActivityRowShift.SHIFT_3,
    }
    if value in mapping:
        return mapping[value]
    if value in {c.value for c in ActivityRowShift}:
        return value
    return ActivityRowShift.SHIFT_1


def _pick_weather(sub_reports) -> str | None:
    best = None
    best_score = -1
    for sr in sub_reports:
        cond = (sr.weather_condition or '').strip()
        if not cond:
            continue
        score = WEATHER_SEVERITY.get(cond, 0)
        if score > best_score:
            best_score = score
            best = cond
    return best


def _clear_derived(report: DailyReport) -> None:
    for manager in (
        report.activities,
        report.labor_entries,
        report.material_entries,
        report.concrete_logs,
    ):
        manager.filter(is_derived=True).delete()


@transaction.atomic
def ensure_daily_report_summary(project_id, report_date: date, user=None) -> DailyReport:
    from projects.models import Project
    Project.objects.select_for_update().filter(id=project_id).first()
    report = (
        DailyReport.objects.filter(
            project_id=project_id,
            report_date=report_date,
            shift=ReportShift.FULL,
            is_deleted=False,
            is_current=True,
        )
        .order_by('-created_at')
        .first()
    )
    if report is None:
        kwargs = {
            'project_id': project_id,
            'report_date': report_date,
            'shift': ReportShift.FULL,
            'is_auto_summary': True,
            'is_current': True,
        }
        if user is not None:
            kwargs['prepared_by'] = user
            kwargs['created_by'] = user
            kwargs['updated_by'] = user
        report = DailyReport.objects.create(**kwargs)
    elif not report.is_auto_summary:
        report.is_auto_summary = True
        report.save(update_fields=['is_auto_summary', 'updated_at'])
    return rebuild_daily_report_summary(project_id, report_date, user=user, report=report)


@transaction.atomic
def rebuild_daily_report_summary(
    project_id,
    report_date: date,
    user=None,
    report: DailyReport | None = None,
) -> DailyReport:
    if report is None:
        report = (
            DailyReport.objects.filter(
                project_id=project_id,
                report_date=report_date,
                shift=ReportShift.FULL,
                is_deleted=False,
                is_current=True,
            )
            .first()
        )
        if report is None:
            return ensure_daily_report_summary(project_id, report_date, user=user)

    sub_reports = list(contributing_sub_reports(project_id, report_date))
    _clear_derived(report)

    if not report.weather_override:
        weather = _pick_weather(sub_reports)
        if weather:
            report.weather_condition = weather
    if not report.site_status_override:
        # Decision 7: inactive if any contributing specialty marks inactive; else active.
        if any(
            (getattr(sr, 'site_status', None) or SiteStatus.ACTIVE) == SiteStatus.INACTIVE
            for sr in sub_reports
        ):
            report.site_status = SiteStatus.INACTIVE
            # Preserve existing valid inactivity_reason, or leave blank if none set
            if report.inactivity_reason and report.inactivity_reason not in InactivityReason.values:
                report.inactivity_reason = ''
        elif sub_reports:
            report.site_status = SiteStatus.ACTIVE
            report.inactivity_reason = ''
    else:
        if report.site_status == SiteStatus.ACTIVE:
            report.inactivity_reason = ''

    labor_sums: dict[tuple[str, str], dict] = defaultdict(
        lambda: {'present': 0, 'leave': 0, 'source_sub_report': None, 'source_discipline': ''},
    )

    issue_parts: list[str] = []
    visit_parts: list[str] = []
    general_parts: list[str] = []

    for sr in sub_reports:
        sr.linked_daily_report = report
        sr.save(update_fields=['linked_daily_report', 'updated_at'])

        for row in sr.activities.all():
            if row.is_deleted:
                continue
            DailyReportActivity.objects.create(
                report=report,
                activity_description=row.activity_description,
                shift=_normalize_shift(row.shift),
                headcount=row.worker_count,
                zone=row.zone,
                block=row.block,
                floor=row.floor,
                quantity=row.quantity,
                quantity_measured=row.quantity is not None,
                unit=row.unit,
                execution_percentage=row.execution_percentage,
                activity_ref=row.activity_ref,
                subcontractor_name=row.crew_name or '',
                notes='',
                source_sub_report=sr,
                source_discipline=sr.discipline,
                is_derived=True,
            )

        for row in sr.labor_entries.all():
            if row.is_deleted:
                continue
            key = (row.labor_category, (row.job_title or '').strip())
            bucket = labor_sums[key]
            bucket['present'] += row.present_count or 0
            bucket['leave'] += row.leave_count or 0
            bucket['source_sub_report'] = sr
            bucket['source_discipline'] = sr.discipline

        for row in sr.material_entries.all():
            if row.is_deleted:
                continue
            DailyReportMaterial.objects.create(
                report=report,
                material_description=row.material_description,
                quantity=row.quantity,
                unit=row.unit,
                transaction_type=MaterialTransactionType.RECEIPT,
                notes=row.notes or '',
                source_sub_report=sr,
                source_discipline=sr.discipline,
                is_derived=True,
            )

        for row in sr.concrete_entries.all():
            if row.is_deleted:
                continue
            DailyReportConcreteLog.objects.create(
                report=report,
                concrete_description=row.concrete_description,
                volume_m3=row.volume_m3,
                zone=row.zone,
                block=row.block,
                floor=row.floor,
                notes=row.notes or '',
                source_sub_report=sr,
                source_discipline=sr.discipline,
                is_derived=True,
            )

        for row in sr.general_activities.all():
            if row.is_deleted:
                continue
            loc = row.location or ''
            general_parts.append(
                f'[{sr.discipline}] {row.activity_description}'
                + (f' @ {loc}' if loc else '')
                + (f' ({row.quantity} {row.unit})' if row.quantity is not None else ''),
            )

        for row in sr.notes.all():
            if row.is_deleted:
                continue
            tagged = f'[{sr.discipline}] {row.text}'
            if row.note_type == SubReportNoteType.VISIT:
                visit_parts.append(tagged)
            elif row.note_type == SubReportNoteType.ISSUE:
                issue_parts.append(tagged)
            else:
                issue_parts.append(tagged)

    for (category, title), bucket in labor_sums.items():
        if not title:
            continue
        DailyReportLabor.objects.create(
            report=report,
            project_id=project_id,
            report_date=report_date,
            labor_category=category,
            job_title=title,
            shift_1_count=bucket['present'],
            shift_2_count=0,
            shift_3_count=0,
            absence_count=bucket['leave'],
            source_sub_report=bucket['source_sub_report'],
            source_discipline=bucket['source_discipline'],
            is_derived=True,
        )

    # Preserve summary-owned general_notes / management_opinion; append derived narratives
    # only into a dedicated suffix markers if notes were empty of prior auto block.
    auto_block_parts = []
    if general_parts:
        auto_block_parts.append('فعالیت‌های عمومی:\n' + '\n'.join(general_parts))
    if issue_parts:
        auto_block_parts.append('ملاحظات:\n' + '\n'.join(issue_parts))
    if visit_parts:
        auto_block_parts.append('بازدیدها:\n' + '\n'.join(visit_parts))
    if auto_block_parts:
        marker_start = '<!--auto-summary-notes-->'
        marker_end = '<!--/auto-summary-notes-->'
        existing = report.general_notes or ''
        if marker_start in existing and marker_end in existing:
            before = existing.split(marker_start)[0].rstrip()
            after = existing.split(marker_end, 1)[1].lstrip()
            existing = (before + ('\n' if before and after else '') + after).strip()
        block = marker_start + '\n' + '\n\n'.join(auto_block_parts) + '\n' + marker_end
        report.general_notes = (existing + '\n\n' + block).strip() if existing else block

    report.is_auto_summary = True
    report.aggregated_at = timezone.now()
    if user is not None:
        report.updated_by = user
    report.save()
    return report
