"""Activity measurement methods, versioning, quantity changes and progress validation (FR-PRG)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import transaction
from django.utils import timezone

from master_data.models import Unit
from schedule.models import (
    ActivityMeasurementDefinition,
    ActivityMeasurementVersion,
    ActivityProgress,
    ActivityQuantityChange,
    ActivityQuantityChangeStatus,
    MeasurementMethod,
    MeasurementStatus,
)

MILESTONE_WEIGHT_TOLERANCE = Decimal('0.01')
PROGRESS_EPSILON = 1e-9

_STATUS_BY_CODE = {
    'measurement_already_approved': 409,
}


class ProgressValidationError(Exception):
    """Domain validation failure carrying a stable machine-readable code."""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code

    @property
    def http_status(self) -> int:
        return _STATUS_BY_CODE.get(self.code, 400)

    def as_response(self) -> dict:
        return {'error': {'code': self.code, 'message': self.message}}


# ---------------------------------------------------------------- helpers

def _to_decimal(value: Any, field: str) -> Decimal | None:
    if value is None or value == '':
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ProgressValidationError(
            f'مقدار {field} نامعتبر است.', 'incomplete_measurement_basis',
        ) from exc


def _normalize_milestones(raw: Any) -> list[dict]:
    if raw in (None, ''):
        return []
    if not isinstance(raw, list):
        raise ProgressValidationError('milestones باید لیست باشد.', 'incomplete_measurement_basis')
    result = []
    for item in raw:
        if not isinstance(item, dict):
            raise ProgressValidationError(
                'هر milestone باید شامل name و weight باشد.', 'incomplete_measurement_basis',
            )
        weight = item.get('weight')
        result.append({
            'name': str(item.get('name') or '').strip(),
            'weight': None if weight is None or weight == '' else float(weight),
        })
    return result


def _definition_basis_errors(definition: ActivityMeasurementDefinition) -> str | None:
    """Return a human message when the draft basis is incomplete; None when valid."""
    method = definition.method
    if method == MeasurementMethod.QUANTITY:
        if definition.total_quantity is None or definition.total_quantity <= 0:
            return 'برای روش مقداری، مقدار کل (total_quantity) الزامی است.'
        if definition.unit_id is None:
            return 'برای روش مقداری، واحد (unit) الزامی است.'
        return None
    if method == MeasurementMethod.WEIGHTED_MILESTONES:
        milestones = definition.milestones or []
        if not milestones:
            return 'برای روش نقاط عطف وزنی، حداقل یک milestone لازم است.'
        total = Decimal('0')
        for item in milestones:
            if not item.get('name') or item.get('weight') is None or float(item['weight']) <= 0:
                return 'نام و وزن مثبت برای همه milestoneها الزامی است.'
            total += Decimal(str(item['weight']))
        if abs(total - Decimal('1')) > MILESTONE_WEIGHT_TOLERANCE:
            return 'مجموع وزن milestoneها باید برابر ۱ باشد.'
        return None
    if method == MeasurementMethod.EVIDENCE_PERCENT:
        if not (definition.evidence_rules or '').strip():
            return 'برای روش درصد مستند، قوانین مستندات (evidence_rules) الزامی است.'
        return None
    return 'روش اندازه‌گیری نامعتبر است.'


def build_basis_snapshot(definition: ActivityMeasurementDefinition) -> dict:
    unit = definition.unit
    return {
        'method': definition.method,
        'total_quantity': str(definition.total_quantity) if definition.total_quantity is not None else None,
        'unit_id': str(definition.unit_id) if definition.unit_id else None,
        'unit_symbol': (unit.unit_symbol or unit.unit_name) if unit else '',
        'milestones': list(definition.milestones or []),
        'evidence_rules': definition.evidence_rules or '',
    }


def _snapshot_basis_error(snapshot: dict) -> str | None:
    """Validate a stored snapshot (used on every progress write)."""
    method = snapshot.get('method')
    if method == MeasurementMethod.QUANTITY:
        try:
            total = Decimal(str(snapshot.get('total_quantity')))
        except (InvalidOperation, ValueError):
            return 'مقدار کل پایه اندازه‌گیری ناقص است.'
        if total <= 0 or not snapshot.get('unit_id'):
            return 'مقدار کل یا واحد پایه اندازه‌گیری ناقص است.'
        return None
    if method == MeasurementMethod.WEIGHTED_MILESTONES:
        milestones = snapshot.get('milestones') or []
        weights = [m.get('weight') for m in milestones]
        if not milestones or any(w is None for w in weights):
            return 'وزن milestoneها ناقص است.'
        if abs(Decimal(str(sum(weights))) - Decimal('1')) > MILESTONE_WEIGHT_TOLERANCE:
            return 'مجموع وزن milestoneها برابر ۱ نیست.'
        return None
    if method == MeasurementMethod.EVIDENCE_PERCENT:
        if not (snapshot.get('evidence_rules') or '').strip():
            return 'قوانین مستندات تعریف نشده است.'
        return None
    return 'روش اندازه‌گیری نامعتبر است.'


def _apply_basis(definition: ActivityMeasurementDefinition, data: dict) -> None:
    if 'method' in data and data['method'] is not None:
        if data['method'] not in MeasurementMethod.values:
            raise ProgressValidationError('روش اندازه‌گیری نامعتبر است.', 'incomplete_measurement_basis')
        definition.method = data['method']
    if 'total_quantity' in data:
        definition.total_quantity = _to_decimal(data['total_quantity'], 'total_quantity')
    if 'unit_id' in data or 'unit' in data:
        unit_id = data.get('unit_id', data.get('unit'))
        if unit_id in (None, ''):
            definition.unit = None
        else:
            unit = Unit.objects.filter(pk=unit_id).first()
            if unit is None:
                raise ProgressValidationError('واحد انتخاب‌شده یافت نشد.', 'incomplete_measurement_basis')
            definition.unit = unit
    if 'milestones' in data:
        definition.milestones = _normalize_milestones(data['milestones'])
    if 'evidence_rules' in data:
        definition.evidence_rules = data['evidence_rules'] or ''


# ---------------------------------------------------------------- definition lifecycle

def get_or_create_definition(activity, user) -> ActivityMeasurementDefinition:
    definition = ActivityMeasurementDefinition.objects.filter(activity=activity).select_related(
        'unit', 'current_version',
    ).first()
    if definition:
        return definition
    return ActivityMeasurementDefinition.objects.create(
        project_id=activity.project_id,
        activity=activity,
        method=MeasurementMethod.QUANTITY,
        status=MeasurementStatus.DRAFT,
        total_quantity=activity.total_quantity,
        unit_id=activity.unit_id,
        created_by=user,
        updated_by=user,
    )


def update_draft(definition: ActivityMeasurementDefinition, data: dict, user) -> ActivityMeasurementDefinition:
    if definition.status == MeasurementStatus.APPROVED:
        raise ProgressValidationError(
            'تعریف تأییدشده است؛ برای تغییر از endpoint تغییر روش (change) استفاده کنید.',
            'measurement_locked',
        )
    _apply_basis(definition, data)
    definition.updated_by = user
    definition.save()
    return definition


@transaction.atomic
def approve_definition(definition: ActivityMeasurementDefinition, user, reason: str = '') -> ActivityMeasurementVersion:
    if definition.status == MeasurementStatus.APPROVED:
        raise ProgressValidationError('هیچ تغییر در انتظار تأییدی وجود ندارد.', 'measurement_already_approved')

    error = _definition_basis_errors(definition)
    if error:
        raise ProgressValidationError(error, 'incomplete_measurement_basis')

    last = definition.versions.order_by('-version_number').first()
    version_number = (last.version_number if last else 0) + 1
    reason = (reason or definition.pending_change_reason or '').strip()
    if version_number > 1 and not reason:
        raise ProgressValidationError('برای تغییر روش، ذکر دلیل الزامی است.', 'method_change_reason_required')

    now = timezone.now()
    version = ActivityMeasurementVersion.objects.create(
        definition=definition,
        version_number=version_number,
        method=definition.method,
        basis_snapshot=build_basis_snapshot(definition),
        change_reason=reason,
        approved_at=now,
        approved_by=user,
    )
    definition.status = MeasurementStatus.APPROVED
    definition.current_version = version
    definition.approved_at = now
    definition.approved_by = user
    definition.pending_change_reason = ''
    definition.updated_by = user
    definition.save()
    return version


@transaction.atomic
def start_method_change(
    definition: ActivityMeasurementDefinition, data: dict, user, reason: str,
) -> ActivityMeasurementDefinition:
    """Move an approved definition back to draft with a new pending basis.

    ``current_version`` is retained so progress writes keep using the last approved
    basis until the new draft is approved.
    """
    reason = (reason or '').strip()
    if not reason:
        raise ProgressValidationError('برای تغییر روش، ذکر دلیل الزامی است.', 'method_change_reason_required')
    if definition.current_version_id is None:
        raise ProgressValidationError(
            'هنوز نسخه تأییدشده‌ای وجود ندارد؛ از ویرایش پیش‌نویس استفاده کنید.',
            'measurement_not_approved',
        )
    _apply_basis(definition, data)
    definition.status = MeasurementStatus.DRAFT
    definition.pending_change_reason = reason
    definition.updated_by = user
    definition.save()
    return definition


def get_current_approved_version(activity) -> ActivityMeasurementVersion | None:
    definition = ActivityMeasurementDefinition.objects.filter(activity=activity).select_related(
        'current_version',
    ).first()
    if definition is None:
        return None
    return definition.current_version


# ---------------------------------------------------------------- quantity changes

def create_quantity_change(activity, data: dict, user) -> ActivityQuantityChange:
    new_total = _to_decimal(data.get('new_total'), 'new_total')
    if new_total is None or new_total <= 0:
        raise ProgressValidationError('new_total باید مقداری مثبت باشد.', 'invalid_quantity_change')
    previous = _to_decimal(data.get('previous_total'), 'previous_total')
    if previous is None:
        previous = effective_total_quantity(activity)
    if previous is None:
        raise ProgressValidationError('previous_total مشخص نیست.', 'invalid_quantity_change')
    if new_total <= previous:
        raise ProgressValidationError(
            'new_total باید بزرگ‌تر از previous_total باشد.', 'invalid_quantity_change',
        )
    reason = (data.get('reason') or '').strip()
    if not reason:
        raise ProgressValidationError('دلیل تغییر مقدار الزامی است.', 'quantity_change_reason_required')
    return ActivityQuantityChange.objects.create(
        project_id=activity.project_id,
        activity=activity,
        previous_total=previous,
        new_total=new_total,
        reason=reason,
        status=ActivityQuantityChangeStatus.DRAFT,
        created_by=user,
        updated_by=user,
    )


@transaction.atomic
def approve_quantity_change(change: ActivityQuantityChange, user) -> ActivityQuantityChange:
    if change.status != ActivityQuantityChangeStatus.DRAFT:
        raise ProgressValidationError('فقط تغییر پیش‌نویس قابل تأیید است.', 'quantity_change_not_draft')
    change.status = ActivityQuantityChangeStatus.APPROVED
    change.approved_at = timezone.now()
    change.approved_by = user
    change.updated_by = user
    change.save()
    activity = change.activity
    activity.total_quantity = change.new_total
    activity.updated_by = user
    activity.save(update_fields=['total_quantity', 'updated_by', 'updated_at'])
    return change


def _latest_approved_change(activity) -> ActivityQuantityChange | None:
    return (
        ActivityQuantityChange.objects.filter(
            activity=activity, status=ActivityQuantityChangeStatus.APPROVED,
        )
        .order_by('-approved_at')
        .first()
    )


def effective_total_quantity(activity, version: ActivityMeasurementVersion | None = None) -> Decimal | None:
    """Approved basis total, raised by the latest approved quantity change."""
    version = version or get_current_approved_version(activity)
    base: Decimal | None = None
    if version is not None and version.method == MeasurementMethod.QUANTITY:
        raw = version.basis_snapshot.get('total_quantity')
        base = Decimal(str(raw)) if raw is not None else None
    elif version is None and activity.total_quantity is not None:
        base = Decimal(str(activity.total_quantity))
    change = _latest_approved_change(activity)
    if change is not None and (base is None or change.new_total > base):
        return change.new_total
    return base


# ---------------------------------------------------------------- validation

def require_approved_version(activity) -> ActivityMeasurementVersion:
    version = get_current_approved_version(activity)
    if version is None:
        raise ProgressValidationError(
            'روش اندازه‌گیری این فعالیت هنوز تأیید نشده است.', 'measurement_not_approved',
        )
    error = _snapshot_basis_error(version.basis_snapshot)
    if error:
        raise ProgressValidationError(error, 'incomplete_measurement_basis')
    return version


def validate_progress_pct(activity, pct: float, *, version: ActivityMeasurementVersion | None = None) -> float:
    """Validate a cumulative progress fraction (0..1) and return the value to store.

    * No approved measurement → ``measurement_not_approved``
    * Incomplete basis → ``incomplete_measurement_basis``
    * ``pct`` > 1 → ``progress_exceeds_100`` unless the quantity method has an approved
      quantity change that covers it; the returned value is then re-based onto the new total.
    """
    version = version or require_approved_version(activity)
    if pct < 0:
        raise ProgressValidationError('پیشرفت نمی‌تواند منفی باشد.', 'invalid_progress')
    if pct <= 1 + PROGRESS_EPSILON:
        return min(pct, 1.0)

    if version.method == MeasurementMethod.QUANTITY:
        base = Decimal(str(version.basis_snapshot.get('total_quantity')))
        effective = effective_total_quantity(activity, version)
        if effective is not None and effective > base:
            implied_quantity = base * Decimal(str(pct))
            if implied_quantity <= effective:
                return float(implied_quantity / effective)
    raise ProgressValidationError(
        'پیشرفت تجمعی بیش از ۱۰۰٪ است و تغییر مقدار تأییدشده‌ای آن را پوشش نمی‌دهد.',
        'progress_exceeds_100',
    )


def compute_quantity_progress(activity, cumulative_quantity, version: ActivityMeasurementVersion) -> float:
    """Cumulative fraction for quantity-method activities against the effective total."""
    total = effective_total_quantity(activity, version)
    if total is None or total <= 0:
        raise ProgressValidationError('مقدار کل پایه اندازه‌گیری ناقص است.', 'incomplete_measurement_basis')
    pct = float(Decimal(str(cumulative_quantity or 0)) / total)
    if pct > 1 + PROGRESS_EPSILON:
        raise ProgressValidationError(
            'پیشرفت تجمعی بیش از ۱۰۰٪ است و تغییر مقدار تأییدشده‌ای آن را پوشش نمی‌دهد.',
            'progress_exceeds_100',
        )
    return min(pct, 1.0)


# ---------------------------------------------------------------- progress recording

def previous_cumulative_progress(activity, report_date: date) -> float:
    prior = (
        ActivityProgress.objects.filter(
            activity=activity,
            report_date__lt=report_date,
            actual_progress__isnull=False,
        )
        .order_by('-report_date')
        .first()
    )
    return float(prior.actual_progress) if prior else 0.0


def record_progress(
    activity,
    report_date: date,
    actual_progress: float,
    user,
    *,
    source: str,
    cumulative_quantity=None,
    notes: str = '',
    evidence_refs: dict | None = None,
    version: ActivityMeasurementVersion | None = None,
    approve: bool = False,
) -> ActivityProgress:
    """Create/update a progress row with period delta and measurement version.

    ``approved_progress`` is only written when ``approve`` is true (daily-report path or
    explicit technical approval). Manual entries leave any existing approved value untouched.
    """
    version = version or require_approved_version(activity)
    period = round(actual_progress - previous_cumulative_progress(activity, report_date), 3)
    defaults: dict[str, Any] = {
        'actual_progress': actual_progress,
        'period_progress': period,
        'cumulative_quantity': cumulative_quantity,
        'source': source,
        'notes': notes,
        'updated_by': user,
        'measurement_version': version,
    }
    if evidence_refs is not None:
        defaults['evidence_refs'] = evidence_refs
    if approve:
        defaults['approved_progress'] = actual_progress
        defaults['technical_approved_at'] = timezone.now()
        defaults['technical_approved_by'] = user
    progress, _ = ActivityProgress.objects.update_or_create(
        activity=activity,
        report_date=report_date,
        defaults=defaults,
    )
    return progress


def record_manual_progress(
    activity,
    report_date: date,
    actual_progress: float,
    user,
    *,
    cumulative_quantity=None,
    notes: str = '',
    evidence_refs: dict | None = None,
) -> ActivityProgress:
    version = require_approved_version(activity)
    pct = validate_progress_pct(activity, actual_progress, version=version)
    return record_progress(
        activity,
        report_date,
        pct,
        user,
        source=ActivityProgress.ProgressSource.MANUAL,
        cumulative_quantity=cumulative_quantity,
        notes=notes,
        evidence_refs=evidence_refs,
        version=version,
    )


@transaction.atomic
def technical_approve_progress(activity, user, *, report_date: date | None = None, data: dict | None = None):
    """Mark the latest (or given-date) recorded progress as technically approved."""
    data = data or {}
    if data.get('basis') == 'photo' or data.get('approved_by_photo'):
        raise ProgressValidationError(
            'عکس به‌تنهایی تأیید فنی محسوب نمی‌شود.', 'photo_not_technical_approval',
        )
    version = require_approved_version(activity)
    qs = ActivityProgress.objects.filter(activity=activity, actual_progress__isnull=False)
    if report_date:
        qs = qs.filter(report_date=report_date)
    progress = qs.order_by('-report_date').first()
    if progress is None:
        raise ProgressValidationError('پیشرفت ثبت‌شده‌ای برای تأیید وجود ندارد.', 'progress_not_found')
    validate_progress_pct(activity, float(progress.actual_progress), version=version)

    progress.approved_progress = progress.actual_progress
    progress.technical_approved_at = timezone.now()
    progress.technical_approved_by = user
    progress.updated_by = user
    update_fields = [
        'approved_progress', 'technical_approved_at', 'technical_approved_by', 'updated_by',
    ]
    if progress.measurement_version_id is None:
        progress.measurement_version = version
        update_fields.append('measurement_version')
    evidence = data.get('evidence_refs')
    if isinstance(evidence, dict):
        progress.evidence_refs = evidence
        update_fields.append('evidence_refs')
    progress.save(update_fields=update_fields)
    return progress
