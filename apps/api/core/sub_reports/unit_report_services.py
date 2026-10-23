"""Unit daily report workflow services (feature 032, US1/US2/US4).

Canonical unit-report open/create/edit/submit/approve/reject/correct/delete with
deterministic current-version resolution, append-only status events, and SoD.
All transition checks reload and lock the current version before validating
state (data-model State Transitions).
"""
from __future__ import annotations

import uuid
from datetime import date

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from common.reporting_units import SpecialtyUnit, is_canonical_unit
from field_reports.services.daily_report_aggregation import rebuild_daily_report_summary
from inventory.models import DepartmentActivityRecord
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
    SubReportStatus,
    UnitReportEventType,
    UnitReportStatusEvent,
)

# Canonical unit -> legacy discipline value kept only as internal compatibility
# evidence during the migration window. Never exposed as a product unit.
UNIT_TO_LEGACY_DISCIPLINE = {
    SpecialtyUnit.BUILDINGS: 'civil',
    SpecialtyUnit.ELECTRICAL: 'electrical',
    SpecialtyUnit.MECHANICAL: 'mechanical',
    SpecialtyUnit.MACHINERY: 'mechanical',
    SpecialtyUnit.WAREHOUSE: 'mechanical',
    SpecialtyUnit.SECURITY: 'civil',
}

EDITABLE_STATUSES = {SubReportStatus.DRAFT, SubReportStatus.REJECTED}
ELIGIBLE_STATUSES = {SubReportStatus.SUBMITTED, SubReportStatus.APPROVED}


class UnitReportError(ValidationError):
    """ValidationError carrying a stable machine-readable code."""

    def __init__(self, detail: str, code: str):
        self.default_code = code
        super().__init__({'detail': detail, 'code': code}, code=code)


class UnitReportNotFound(NotFound):
    """Non-disclosing not-found for scoped unit-report lookups."""

    default_code = 'unit_report_not_found'

    def __init__(self, detail: str = 'گزارش واحد یافت نشد', code: str = 'unit_report_not_found'):
        self.default_code = code
        super().__init__({'detail': detail, 'code': code}, code=code)


def _record_event(report, event_type, actor, from_status='', to_status=None, reason=''):
    return UnitReportStatusEvent.objects.create(
        report_version=report,
        from_status=from_status,
        to_status=to_status if to_status is not None else report.status,
        actor=actor,
        occurred_at=timezone.now(),
        reason=reason or '',
        event_type=event_type,
    )


def current_report_queryset(project_id, unit: str, report_date: date):
    return DisciplineSubReport.objects.filter(
        project_id=project_id,
        unit=unit,
        report_date=report_date,
        is_current=True,
        is_deleted=False,
    )


@transaction.atomic
def open_unit_report(*, project, unit: str, report_date: date, user):
    """Idempotently return the current report or create its first draft.

    Concurrent opens resolve to one current draft: the uniqueness constraint on
    (project, report_date, unit) where is_current=true guarantees a single row,
    and the loser of the race receives the existing report.
    """
    if not is_canonical_unit(unit):
        raise UnitReportError('واحد تخصصی نامعتبر است', 'invalid_specialty_unit')

    existing = (
        current_report_queryset(project.id, unit, report_date)
        .select_for_update()
        .first()
    )
    if existing is not None:
        return existing, False

    try:
        with transaction.atomic():
            report = DisciplineSubReport.objects.create(
                project=project,
                report_date=report_date,
                unit=unit,
                discipline=UNIT_TO_LEGACY_DISCIPLINE[unit],
                legacy_discipline='',
                lineage_id=uuid.uuid4(),
                version_number=1,
                is_current=True,
                status=SubReportStatus.DRAFT,
                created_by=user,
                updated_by=user,
            )
            _record_event(
                report, UnitReportEventType.CREATED, user,
                from_status='', to_status=SubReportStatus.DRAFT,
            )
            return report, True
    except IntegrityError:
        existing = (
            current_report_queryset(project.id, unit, report_date)
            .first()
        )
        if existing is not None:
            return existing, False
        raise


def get_scoped_report(*, project_id, unit: str, report_id):
    """Resolve a report version scoped to the URL project/unit (non-disclosing)."""
    try:
        return (
            DisciplineSubReport.all_objects
            .filter(project_id=project_id, unit=unit, id=report_id)
            .select_related('project')
            .get()
        )
    except DisciplineSubReport.DoesNotExist:
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')


def lock_current_version(report):
    """Reload and lock the current version of the report's lineage."""
    try:
        return (
            DisciplineSubReport.objects
            .select_for_update()
            .filter(
                project_id=report.project_id,
                unit=report.unit,
                report_date=report.report_date,
                is_current=True,
                is_deleted=False,
            )
            .get()
        )
    except DisciplineSubReport.DoesNotExist:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')


def assert_editable(report, user, *, unit=None):
    """Submitted/approved content is immutable; only current versions mutate."""
    if not report.is_current:
        raise UnitReportError('این نسخه قابل ویرایش نیست', 'unit_report_not_current')
    if report.is_deleted:
        raise UnitReportError('این نسخه حذف شده است', 'unit_report_not_editable')
    if report.status not in EDITABLE_STATUSES:
        raise UnitReportError(
            'فقط گزارش‌های پیش‌نویس یا ردشده قابل ویرایش هستند', 'unit_report_not_editable',
        )
    if unit is not None and report.unit != unit:
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')


@transaction.atomic
def update_unit_report(
    report,
    *,
    user,
    unit=None,
    validated_fields: dict,
    nested_data: dict | None = None,
):
    locked = lock_current_version(report)
    if report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    assert_editable(locked, user, unit=unit)
    for field, value in validated_fields.items():
        setattr(locked, field, value)
    locked.updated_by = user
    locked.save()
    if nested_data:
        managers = {
            'activities': (locked.activities, DisciplineSubReportActivity),
            'labor_entries': (locked.labor_entries, DisciplineSubReportLabor),
            'material_entries': (locked.material_entries, DisciplineSubReportMaterial),
            'concrete_entries': (locked.concrete_entries, DisciplineSubReportConcrete),
            'general_activities': (locked.general_activities, DisciplineSubReportGeneralActivity),
            'notes': (locked.notes, DisciplineSubReportNote),
        }
        for key, rows in nested_data.items():
            if rows is None or key not in managers:
                continue
            manager, model = managers[key]
            manager.filter(is_deleted=False).update(is_deleted=True)
            for row in rows:
                model.objects.create(sub_report=locked, **row)
    return locked


@transaction.atomic
def submit_unit_report(report, *, user, unit=None):
    locked = lock_current_version(report)
    if not locked.is_current or report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    if unit is not None and (locked.unit != unit or report.unit != unit):
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')
    if locked.status not in EDITABLE_STATUSES:
        raise UnitReportError(
            'فقط گزارش‌های پیش‌نویس یا ردشده قابل ارسال هستند', 'invalid_unit_report_transition',
        )
    from_status = locked.status
    locked.status = SubReportStatus.SUBMITTED
    locked.submitted_by = user
    locked.submitted_at = timezone.now()
    locked.updated_by = user
    locked.save()
    _record_event(
        locked, UnitReportEventType.SUBMITTED, user,
        from_status=from_status, to_status=SubReportStatus.SUBMITTED,
    )
    _trigger_rebuild(locked, user)
    return locked


@transaction.atomic
def approve_unit_report(report, *, user, unit=None, sod_checker=None):
    locked = lock_current_version(report)
    if not locked.is_current or report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    if unit is not None and (locked.unit != unit or report.unit != unit):
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')
    if locked.status != SubReportStatus.SUBMITTED:
        raise UnitReportError(
            'فقط گزارش‌های ارائه‌شده قابل تأیید هستند', 'invalid_unit_report_transition',
        )
    # T028: Enforce Segregation of Duties (SoD) in the service path.
    # Preparer or submitter cannot approve the same report; superuser break-glass allows.
    if not getattr(user, 'is_superuser', False) and (
        locked.created_by_id == getattr(user, 'id', None)
        or locked.submitted_by_id == getattr(user, 'id', None)
    ):
        raise UnitReportError('تفکیک وظایف: تهیه‌کننده یا ارسال‌کننده نمی‌تواند گزارش را تأیید کند', 'sod_self_approve')
    if sod_checker is not None:
        violation = sod_checker(locked, user)
        if violation:
            raise UnitReportError(violation, 'sod_self_approve')
    from_status = locked.status
    locked.status = SubReportStatus.APPROVED
    locked.approved_by = user
    locked.approved_at = timezone.now()
    locked.updated_by = user
    locked.save()
    _record_event(
        locked, UnitReportEventType.APPROVED, user,
        from_status=from_status, to_status=SubReportStatus.APPROVED,
    )
    _trigger_rebuild(locked, user)
    return locked


@transaction.atomic
def reject_unit_report(report, *, user, rejection_reason, unit=None):
    locked = lock_current_version(report)
    if not locked.is_current or report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    if unit is not None and (locked.unit != unit or report.unit != unit):
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')
    if locked.status != SubReportStatus.SUBMITTED:
        raise UnitReportError(
            'فقط گزارش‌های ارائه‌شده قابل رد هستند', 'invalid_unit_report_transition',
        )
    reason = (rejection_reason or '').strip()
    if not reason:
        raise UnitReportError('دلیل رد الزامی است', 'rejection_reason_required')
    from_status = locked.status
    locked.status = SubReportStatus.REJECTED
    locked.rejection_reason = reason
    locked.rejected_by = user
    locked.rejected_at = timezone.now()
    locked.updated_by = user
    locked.save()
    _record_event(
        locked, UnitReportEventType.REJECTED, user,
        from_status=from_status, to_status=SubReportStatus.REJECTED, reason=reason,
    )
    _trigger_rebuild(locked, user)
    return locked


@transaction.atomic
def correct_unit_report(report, *, user, unit=None):
    """Explicit correction action (feature 032, US4, T048).

    Requires approved status and is_current=True.
    Clones report-owned content into a new version:
      - monotonic version_number incremented within lineage
      - same lineage_id
      - supersedes=report
      - is_current=True
      - status='draft'
    Sets old version is_current=False.
    Creates UnitReportStatusEvent with event_type='corrected'.
    Triggers summary rebuild so obsolete contributions are removed.
    """
    locked = lock_current_version(report)
    if not locked.is_current or report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    if unit is not None and (locked.unit != unit or report.unit != unit):
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')
    if locked.status != SubReportStatus.APPROVED:
        raise UnitReportError(
            'فقط گزارش‌های تأییدشده قابل اصلاح هستند', 'invalid_unit_report_transition',
        )

    # 1. Old version is no longer current (remains read-only approved history)
    locked.is_current = False
    locked.updated_by = user
    locked.save(update_fields=['is_current', 'updated_by', 'updated_at'])

    # 2. Create new current draft version
    new_report = DisciplineSubReport.objects.create(
        project=locked.project,
        report_date=locked.report_date,
        unit=locked.unit,
        discipline=locked.discipline,
        legacy_discipline=locked.legacy_discipline,
        lineage_id=locked.lineage_id,
        version_number=locked.version_number + 1,
        supersedes=locked,
        is_current=True,
        status=SubReportStatus.DRAFT,
        weather_condition=locked.weather_condition,
        site_status=locked.site_status,
        form_code=locked.form_code,
        revision_number=locked.revision_number,
        created_by=user,
        updated_by=user,
    )

    # 3. Clone child rows
    for act in locked.activities.filter(is_deleted=False).order_by('row_number', 'id'):
        DisciplineSubReportActivity.objects.create(
            sub_report=new_report,
            row_number=act.row_number,
            shift=act.shift,
            crew_name=act.crew_name,
            foreman_count=act.foreman_count,
            worker_count=act.worker_count,
            headcount=act.headcount,
            parcel=act.parcel,
            zone=act.zone,
            block=act.block,
            floor=act.floor,
            activity_description=act.activity_description,
            notes=act.notes,
            unit=act.unit,
            quantity=act.quantity,
            execution_percentage=act.execution_percentage,
            activity_ref=act.activity_ref,
            contractor_ref=act.contractor_ref,
        )

    for dar in locked.activity_records.all().order_by('id'):
        DepartmentActivityRecord.objects.create(
            project=dar.project,
            department=dar.department,
            date=dar.date,
            location=dar.location,
            activity_description=dar.activity_description,
            contractor=dar.contractor,
            contractor_ref=dar.contractor_ref,
            unit=dar.unit,
            description=dar.description,
            material_type=dar.material_type,
            quantity_in=dar.quantity_in,
            quantity_out=dar.quantity_out,
            consumption_location=dar.consumption_location,
            supplier=dar.supplier,
            unit_report=new_report,
        )

    for l in locked.labor_entries.filter(is_deleted=False).order_by('id'):
        DisciplineSubReportLabor.objects.create(
            sub_report=new_report,
            labor_category=l.labor_category,
            job_title=l.job_title,
            present_count=l.present_count,
            leave_count=l.leave_count,
            overtime_hours=l.overtime_hours,
            contractor_ref=l.contractor_ref,
        )

    from sub_reports.models import DisciplineSubReportMachinery

    for mr in locked.machinery_rows.filter(is_deleted=False).order_by('row_number', 'id'):
        DisciplineSubReportMachinery.objects.create(
            sub_report=new_report,
            row_number=mr.row_number,
            equipment_type=mr.equipment_type,
            equipment_ref=mr.equipment_ref,
            status_total=mr.status_total,
            status_active=mr.status_active,
            status_ready=mr.status_ready,
            status_inactive=mr.status_inactive,
            status_under_repair=mr.status_under_repair,
            operating_hours=mr.operating_hours,
            stoppage_hours=mr.stoppage_hours,
            repair_hours=mr.repair_hours,
            stoppage_reason_code=mr.stoppage_reason_code,
        )

    for m in locked.material_entries.filter(is_deleted=False).order_by('id'):
        DisciplineSubReportMaterial.objects.create(
            sub_report=new_report,
            transaction_type=m.transaction_type,
            material_ref=m.material_ref,
            material_description=m.material_description,
            quantity=m.quantity,
            unit=m.unit,
            consumption_location=m.consumption_location,
            supplier=m.supplier,
            warehouse_document_reference=m.warehouse_document_reference,
            notes=m.notes,
        )

    for c in locked.concrete_entries.filter(is_deleted=False).order_by('id'):
        DisciplineSubReportConcrete.objects.create(
            sub_report=new_report,
            concrete_description=c.concrete_description,
            volume_m3=c.volume_m3,
            zone=c.zone,
            block=c.block,
            floor=c.floor,
            notes=c.notes,
        )

    for g in locked.general_activities.filter(is_deleted=False).order_by('id'):
        DisciplineSubReportGeneralActivity.objects.create(
            sub_report=new_report,
            activity_description=g.activity_description,
            location=g.location,
            quantity=g.quantity,
            unit=g.unit,
            notes=g.notes,
        )

    for n in locked.notes.filter(is_deleted=False).order_by('row_number', 'id'):
        DisciplineSubReportNote.objects.create(
            sub_report=new_report,
            note_type=n.note_type,
            text=n.text,
            row_number=n.row_number,
        )

    # 4. Status event
    _record_event(
        new_report, UnitReportEventType.CORRECTED, user,
        from_status=SubReportStatus.APPROVED, to_status=SubReportStatus.DRAFT,
    )

    # 5. Trigger summary rebuild (v1 no longer contributes; v2 is draft)
    _trigger_rebuild(locked, user)

    return new_report


@transaction.atomic
def soft_delete_unit_report(report, *, user, unit=None):
    locked = lock_current_version(report)
    if not locked.is_current or report.id != locked.id:
        raise UnitReportError('این نسخه جاری نیست', 'unit_report_not_current')
    if unit is not None and (locked.unit != unit or report.unit != unit):
        raise UnitReportNotFound('گزارش واحد یافت نشد', 'unit_report_not_found')
    if locked.status not in EDITABLE_STATUSES:
        raise UnitReportError(
            'فقط گزارش‌های پیش‌نویس یا ردشده قابل حذف هستند', 'unit_report_not_editable',
        )
    from_status = locked.status
    locked.is_deleted = True
    locked.deleted_at = timezone.now()
    # A deleted current row must be made non-current so a new current row may
    # be created for the same project/date/unit key.
    locked.is_current = False
    locked.updated_by = user
    locked.save()
    _record_event(
        locked, UnitReportEventType.DELETED, user,
        from_status=from_status, to_status=from_status,
    )
    _trigger_rebuild(locked, user)
    return locked


def _trigger_rebuild(report, user=None):
    rebuild_daily_report_summary(report.project_id, report.report_date, user=user)
