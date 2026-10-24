"""Section-level contract validation for unit-report child rows (feature 033).

Task T014 (§1 executed activities) and later section stages share this module.
Validation is fielded and raises a single :class:`SectionContractError` carrying
stable machine codes (`quantity_must_be_positive`, `invalid_shift`,
`activity_not_in_project_scope`, `contractor_not_in_project_scope`,
`contractor_required`, …) plus localized messages, so the API layer can render
a 422 JSON body with per-field codes (contract unit-report-sections-api.md).
"""
from __future__ import annotations

from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError as DRFValidationError

from projects.models import Activity, ActivityStatus, Stakeholder
from sub_reports.serializers import (
    UnitReportActivitySectionSerializer,
    UnitReportLaborSectionSerializer,
    UnitReportMachinerySectionSerializer,
    UnitReportMaterialSectionSerializer,
)

CONTRACTOR_SCOPE_ERROR = 'contractor_not_in_project_scope'
CONTRACTOR_REQUIRED_ERROR = 'contractor_required'
ACTIVITY_SCOPE_ERROR = 'activity_not_in_project_scope'
QUANTITY_POSITIVE_ERROR = 'quantity_must_be_positive'
HEADCOUNT_NON_NEGATIVE_ERROR = 'headcount_must_be_non_negative'
UNKNOWN_JOB_TITLE_ERROR = 'unknown_job_title'
INVALID_LABOR_CATEGORY_ERROR = 'invalid_labor_category'
STOPPAGE_REASON_REQUIRED_ERROR = 'stoppage_reason_required_when_stoppage_gt_zero'
HOURS_EXCEED_DAY_LIMIT_ERROR = 'hours_exceed_day_limit'
STOPPAGE_REASON_NOT_IN_VOCABULARY_ERROR = 'stoppage_reason_not_in_vocabulary'
STATUS_COUNT_NON_NEGATIVE_ERROR = 'status_count_must_be_non_negative'
MACHINERY_STATUS_SUMS_INCONSISTENT_ERROR = 'machinery_status_sums_inconsistent'
REFERENCE_SCOPE_ERROR = 'reference_not_in_project_scope'
TRANSACTION_TYPE_REQUIRED_ERROR = 'transaction_type_required'
RECEIPT_REQUIRES_DOCUMENT_REFERENCE_ERROR = 'receipt_requires_document_reference'
CONSUMPTION_LOCATION_REQUIRED_ERROR = 'consumption_location_required_for_consumption'
VOLUME_POSITIVE_ERROR = 'volume_must_be_positive'
SAMPLING_REQUIRES_TEST_INFORMATION = 'sampling_requires_test_information'
BARRIER_OWNER_DUE_ERROR = 'barrier_owner_and_due_date_required'
HSE_IMMEDIATE_ACTION_ERROR = 'hse_immediate_action_required'
UNSUPPORTED_FILE_FORMAT = 'unsupported_file_format'
FILE_TOO_LARGE = 'file_too_large'
ATTACHMENT_ROW_NOT_IN_VERSION = 'attachment_row_not_in_version'

# Stable section error codes and their localized fa messages (T043 will wire
# the web locale files; the API layer relies on the messages below).
ERROR_MESSAGES = {
    CONTRACTOR_SCOPE_ERROR: _('این پیمانکار در محدوده پروژه نیست'),
    CONTRACTOR_REQUIRED_ERROR: _('انتخاب پیمانکار الزامی است'),
    ACTIVITY_SCOPE_ERROR: _('فعالیت از محدوده پروژه خارج است یا غیرفعال است'),
    QUANTITY_POSITIVE_ERROR: _('مقدار مدیراً باید بزرگ‌تر از صفر باشد'),
    HEADCOUNT_NON_NEGATIVE_ERROR: _('تعداد نفرات نمی‌تواند منفی باشد'),
    UNKNOWN_JOB_TITLE_ERROR: _('عنوان شغلی در کاتالوگ فعال پروژه وجود ندارد'),
    INVALID_LABOR_CATEGORY_ERROR: _('دسته‌بندی نیروی انسانی با عنوان شغلی مطابقت ندارد'),
    STOPPAGE_REASON_REQUIRED_ERROR: _('هنگامی که ساعت توقف بزرگ‌تر از صفر است، انتخاب علت توقف الزامی است'),
    HOURS_EXCEED_DAY_LIMIT_ERROR: _('مجموع ساعات کارکرد، توقف و تعمیر نمی‌تواند بیش از ۲۴ ساعت در شبانه‌روز باشد'),
    STOPPAGE_REASON_NOT_IN_VOCABULARY_ERROR: _('علت توقف انتخاب‌شده در فهرست مجاز پروژه وجود ندارد'),
    STATUS_COUNT_NON_NEGATIVE_ERROR: _('تعداد وضعیت ماشین‌آلات نمی‌تواند منفی باشد'),
    MACHINERY_STATUS_SUMS_INCONSISTENT_ERROR: _('مجموع وضعیت‌های ردیف کلی نوع ماشین‌آلات با جمع ردیف‌های تفکیکی مطابقت ندارد'),
    REFERENCE_SCOPE_ERROR: _('شناسه ارجاع‌شده متعلق به این پروژه نیست'),
    TRANSACTION_TYPE_REQUIRED_ERROR: _('انتخاب نوع تراکنش مصالح الزامی است'),
    RECEIPT_REQUIRES_DOCUMENT_REFERENCE_ERROR: _('برای رسید انبار، شماره برگه/سند انبار الزامی است'),
    CONSUMPTION_LOCATION_REQUIRED_ERROR: _('برای مصرف مصالح، محل مصرف الزامی است'),
    VOLUME_POSITIVE_ERROR: _('حجم بتن باید بزرگ‌تر از صفر باشد'),
    SAMPLING_REQUIRES_TEST_INFORMATION: _('نمونه‌برداری اعلام‌شده بدون کد آزمایشگاه یا تعداد برگه آزمایش قابل ارسال نیست'),
    BARRIER_OWNER_DUE_ERROR: _('برای مانع، مسئول و تاریخ سررسید الزامی است'),
    HSE_IMMEDIATE_ACTION_ERROR: _('اقدام فوری برای حادثه ایمنی الزامی است'),
    UNSUPPORTED_FILE_FORMAT: _('فقط تصاویر JPEG و PNG پذیرفته می‌شوند'),
    FILE_TOO_LARGE: _('حجم فایل نمی‌تواند بیش از ۱۰ مگابایت باشد'),
    ATTACHMENT_ROW_NOT_IN_VERSION: _('ردیف پیوست متعلق به این نسخه گزارش نیست'),
}


class SectionContractError(Exception):
    """Contracts violation carrying fielded stable codes + localized messages."""

    def __init__(self, field_errors=None, code=None, message=None):
        self.errors = []
        if code:
            self.errors.append({
                'code': code,
                'field': None,
                'message': message or str(ERROR_MESSAGES.get(code, code)),
            })
        for item in field_errors or []:
            self.errors.append(item)
        super().__init__('; '.join(f"{e['field']}:{e['code']}" if e.get('field') else e['code']
                                   for e in self.errors))

    @property
    def codes(self):
        return [e['code'] for e in self.errors]

    @property
    def messages(self):
        return [e.get('message') or e['code'] for e in self.errors]

    def field_errors(self, field):
        return [e['code'] for e in self.errors if e.get('field') == field]


# Stable-code mapping for DRF serializer errors (field, drf_code) -> contract code
_DRF_CODE_MAP = {
    ('shift', 'required'): 'invalid_shift',
    ('shift', 'blank'): 'invalid_shift',
    ('shift', 'null'): 'invalid_shift',
    ('shift', 'invalid'): 'invalid_shift',
    ('activity_ref', 'required'): ACTIVITY_SCOPE_ERROR,
    ('activity_ref', 'null'): ACTIVITY_SCOPE_ERROR,
    ('activity_ref', 'does_not_exist'): ACTIVITY_SCOPE_ERROR,
    ('activity_ref', 'incorrect_type'): ACTIVITY_SCOPE_ERROR,
    ('contractor_ref', 'required'): CONTRACTOR_REQUIRED_ERROR,
    ('contractor_ref', 'null'): CONTRACTOR_REQUIRED_ERROR,
    ('contractor_ref', 'does_not_exist'): CONTRACTOR_SCOPE_ERROR,
    ('contractor_ref', 'incorrect_type'): CONTRACTOR_SCOPE_ERROR,
    ('quantity', 'min_string_length'): QUANTITY_POSITIVE_ERROR,
    ('quantity', 'max_string_length'): QUANTITY_POSITIVE_ERROR,
    ('quantity', 'invalid'): QUANTITY_POSITIVE_ERROR,
    ('present_count', 'min_value'): HEADCOUNT_NON_NEGATIVE_ERROR,
    ('present_count', 'invalid'): HEADCOUNT_NON_NEGATIVE_ERROR,
    ('leave_count', 'min_value'): HEADCOUNT_NON_NEGATIVE_ERROR,
    ('leave_count', 'invalid'): HEADCOUNT_NON_NEGATIVE_ERROR,
    ('overtime_hours', 'min_value'): HEADCOUNT_NON_NEGATIVE_ERROR,
    ('labor_category', 'required'): INVALID_LABOR_CATEGORY_ERROR,
    ('labor_category', 'blank'): INVALID_LABOR_CATEGORY_ERROR,
    ('labor_category', 'null'): INVALID_LABOR_CATEGORY_ERROR,
    ('status_total', 'min_value'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_total', 'invalid'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_active', 'min_value'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_active', 'invalid'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_ready', 'min_value'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_ready', 'invalid'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_inactive', 'min_value'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_inactive', 'invalid'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_under_repair', 'min_value'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('status_under_repair', 'invalid'): STATUS_COUNT_NON_NEGATIVE_ERROR,
    ('equipment_ref', 'does_not_exist'): REFERENCE_SCOPE_ERROR,
    ('equipment_ref', 'incorrect_type'): REFERENCE_SCOPE_ERROR,
    ('material_ref', 'does_not_exist'): REFERENCE_SCOPE_ERROR,
    ('material_ref', 'incorrect_type'): REFERENCE_SCOPE_ERROR,
    ('material_ref', 'reference_not_in_project_scope'): REFERENCE_SCOPE_ERROR,
    ('transaction_type', 'required'): TRANSACTION_TYPE_REQUIRED_ERROR,
    ('transaction_type', 'blank'): TRANSACTION_TYPE_REQUIRED_ERROR,
    ('transaction_type', 'null'): TRANSACTION_TYPE_REQUIRED_ERROR,
    ('transaction_type', 'invalid_choice'): TRANSACTION_TYPE_REQUIRED_ERROR,
    ('transaction_type', 'transaction_type_required'): TRANSACTION_TYPE_REQUIRED_ERROR,
    ('warehouse_document_reference', 'receipt_requires_document_reference'): RECEIPT_REQUIRES_DOCUMENT_REFERENCE_ERROR,
    ('consumption_location', 'consumption_location_required_for_consumption'): CONSUMPTION_LOCATION_REQUIRED_ERROR,
    ('quantity', 'quantity_must_be_positive'): QUANTITY_POSITIVE_ERROR,
    ('quantity', 'required'): QUANTITY_POSITIVE_ERROR,
    ('quantity', 'null'): QUANTITY_POSITIVE_ERROR,
}


def _error_from_drf(index, field, detail):
    entries = detail if isinstance(detail, list) else [detail]
    result = []
    for e in entries:
        raw_code = getattr(e, 'code', None) or (e.get('code') if isinstance(e, dict) else None)
        code = _DRF_CODE_MAP.get((field, str(raw_code)))
        if code is None:
            code = str(raw_code) if raw_code else 'invalid'
        result.append({
            'row': index,
            'field': field,
            'code': code,
            'message': ERROR_MESSAGES.get(code, str(e)),
        })
    return result


def _activity_active_and_within_project(activity: Activity, project_id) -> bool:
    """Recognized vocabulary of schedulable activity states (§1).

    Refuses other-project activities, deleted ones, and inactive/unapproved
    statuses — each with the same stable scope code (never silent coercion).
    """
    if activity is None:
        return False
    if activity.is_deleted or str(activity.project_id) != str(project_id):
        return False
    return activity.status in {ActivityStatus.NOT_STARTED, ActivityStatus.IN_PROGRESS}


def _contractor_within_project(stakeholder: Stakeholder, project_id) -> bool:
    """Contractor stakeholder must be project-scoped (and not deleted)."""
    if stakeholder is None:
        return False
    if stakeholder.is_deleted or str(stakeholder.project_id) != str(project_id):
        return False
    return True


@transaction.atomic
def validate_activity_rows(report, rows, context=None):
    """Validate + persist §1 activity child rows bound to this version.

    Returns the saved rows when the entire version-level suite passes; raises
    :class:`SectionContractError` with every fielded error otherwise.
    """
    if context is None:
        context = {}
    errors = []
    saved = []
    rows = rows if rows is not None else []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')

    for index, row in enumerate(rows):
        serializer = UnitReportActivitySectionSerializer(data=row, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            for field, detail in exc.detail.items():
                errors.extend(_error_from_drf(index, field, detail))
            continue

        validated = dict(serializer.validated_data)
        errors.extend(_contract_errors(report, validated, index))
        if errors:
            continue

        row_number = validated.pop('row_number', None)
        if row_number is None:
            row_number = _next_row_number(report, 'activities')
        saved.append(serializer.save(sub_report=report, row_number=row_number))
    if errors:
        raise SectionContractError(field_errors=errors)
    return saved


def _contract_errors(report, validated, index=0):
    """§1 per-row contract checks shared by the create and update paths.

    Only fields present in ``validated`` are checked: on PATCH an absent
    field stays as persisted (the serializer already refuses missing
    required fields on full writes), while every provided value runs the
    full scope/positivity suite. Short-circuits on the first violation per
    row so one row never emits duplicate codes (T012 expectations).
    """
    errors = []

    def err(field, code):
        return {
            'row': index,
            'field': field,
            'code': code,
            'message': str(ERROR_MESSAGES[code]),
        }

    if 'quantity' in validated:
        quantity = validated['quantity']
        if quantity is not None and quantity <= 0:
            return [err('quantity', QUANTITY_POSITIVE_ERROR)]

    if 'activity_ref' in validated:
        ref = validated['activity_ref']
        if ref is None or not _activity_active_and_within_project(ref, report.project_id):
            return [err('activity_ref', ACTIVITY_SCOPE_ERROR)]

    if 'contractor_ref' in validated:
        contractor = validated['contractor_ref']
        if contractor is None:
            return [err('contractor_ref', CONTRACTOR_REQUIRED_ERROR)]
        if not _contractor_within_project(contractor, report.project_id):
            return [err('contractor_ref', CONTRACTOR_SCOPE_ERROR)]

    return errors


@transaction.atomic
def update_activity_row(report, row, payload, context=None):
    """Validate + apply a partial §1 update bound to this version (T017).

    Instance-bound PATCH semantics: only provided fields change, but every
    provided value re-runs the full section-contract suite. Raises
    :class:`SectionContractError` with the fielded codes otherwise.
    """
    serializer = UnitReportActivitySectionSerializer(
        instance=row, data=payload, context=context or {}, partial=True,
    )
    try:
        serializer.is_valid(raise_exception=True)
    except DRFValidationError as exc:
        errors = []
        for field, detail in exc.detail.items():
            errors.extend(_error_from_drf(0, field, detail))
        raise SectionContractError(field_errors=errors)

    validated = dict(serializer.validated_data)
    errors = _contract_errors(report, validated, 0)
    if errors:
        raise SectionContractError(field_errors=errors)

    updated = serializer.save()
    if 'row_number' in validated:
        # row_number addresses ordering only; keep the persisted sequence.
        updated.refresh_from_db(fields=['row_number'])
    return updated


def _next_row_number(report, related_name):
    current = list(
        getattr(report, related_name).filter(is_deleted=False)
        .values_list('row_number', flat=True)
    )
    return (max(current) if current else 0) + 1


# ---------------------------------------------------------------------------
# §2 Labor section validation (feature 033, task T021)
# ---------------------------------------------------------------------------


def _labor_contract_errors(report, validated, index=0, instance=None):
    errors = []

    def err(field, code):
        return {
            'row': index,
            'field': field,
            'code': code,
            'message': str(ERROR_MESSAGES[code]),
        }

    for count_field in ('present_count', 'leave_count'):
        if count_field in validated and validated[count_field] is not None:
            if validated[count_field] < 0:
                return [err(count_field, HEADCOUNT_NON_NEGATIVE_ERROR)]

    if 'overtime_hours' in validated and validated['overtime_hours'] is not None:
        if validated['overtime_hours'] < 0:
            return [err('overtime_hours', HEADCOUNT_NON_NEGATIVE_ERROR)]

    if 'contractor_ref' in validated and validated['contractor_ref'] is not None:
        if not _contractor_within_project(validated['contractor_ref'], report.project_id):
            return [err('contractor_ref', CONTRACTOR_SCOPE_ERROR)]

    category = validated.get(
        'labor_category',
        getattr(instance, 'labor_category', None) if instance else None,
    )
    if category not in ('indirect', 'direct'):
        return [err('labor_category', INVALID_LABOR_CATEGORY_ERROR)]

    raw_title = (validated.get('job_title') or '').strip()
    custom_title = (validated.get('custom_title') or '').strip()
    if not raw_title and custom_title:
        raw_title = custom_title
    elif not raw_title and instance is not None:
        raw_title = (getattr(instance, 'job_title', '') or '').strip()

    if not raw_title:
        return [err('job_title', UNKNOWN_JOB_TITLE_ERROR)]

    from field_reports.services.daily_report_aggregation import (
        resolve_project_reporting_configuration,
    )
    from project_templates.services import resolve_labor_title

    config = resolve_project_reporting_configuration(report.project_id, report.report_date)
    if config is not None and config.labor_titles.exists():
        resolved = resolve_labor_title(config, raw_title)
        if resolved is None:
            return [err('job_title', UNKNOWN_JOB_TITLE_ERROR)]
        if resolved.category != category:
            return [err('labor_category', INVALID_LABOR_CATEGORY_ERROR)]
        # Store the resolved title label (preserving legacy alias if it was an exact match or canonical label)
        validated['job_title'] = raw_title
    else:
        validated['job_title'] = raw_title

    validated.pop('custom_title', None)
    return errors


@transaction.atomic
def validate_labor_rows(report, rows, context=None):
    """Validate + persist §2 labor child rows bound to this unit-report version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    errors = []
    saved = []
    rows = rows if rows is not None else []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')

    for index, row in enumerate(rows):
        serializer = UnitReportLaborSectionSerializer(data=row, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            for field, detail in exc.detail.items():
                errors.extend(_error_from_drf(index, field, detail))
            continue

        validated = dict(serializer.validated_data)
        row_errors = _labor_contract_errors(report, validated, index)
        if row_errors:
            errors.extend(row_errors)
            continue

        from sub_reports.models import DisciplineSubReportLabor

        saved.append(
            DisciplineSubReportLabor.objects.create(sub_report=report, **validated)
        )
    if errors:
        raise SectionContractError(field_errors=errors)
    return saved


@transaction.atomic
def update_labor_row(report, row, payload, context=None):
    """Validate + apply a partial §2 labor row update bound to this version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    serializer = UnitReportLaborSectionSerializer(
        instance=row, data=payload, context=context, partial=True,
    )
    try:
        serializer.is_valid(raise_exception=True)
    except DRFValidationError as exc:
        errors = []
        for field, detail in exc.detail.items():
            errors.extend(_error_from_drf(0, field, detail))
        raise SectionContractError(field_errors=errors)

    validated = dict(serializer.validated_data)
    row_errors = _labor_contract_errors(report, validated, 0, instance=row)
    if row_errors:
        raise SectionContractError(field_errors=row_errors)

    for attr, val in validated.items():
        setattr(row, attr, val)
    row.save()
    return row


# ---------------------------------------------------------------------------
# §3 Machinery section validation (feature 033, task T028)
# ---------------------------------------------------------------------------

MACHINERY_STATUS_FIELDS = (
    'status_total',
    'status_active',
    'status_ready',
    'status_inactive',
    'status_under_repair',
)


class MachineryValidationResult(list):
    """List of saved ``DisciplineSubReportMachinery`` rows carrying ``.vocabulary``."""

    def __init__(self, iterable=(), *, vocabulary=None):
        super().__init__(iterable)
        self.vocabulary = list(vocabulary or [])


def resolve_stoppage_vocabulary(report, context=None) -> list[dict]:
    """Return effective stoppage reason vocabulary [{reason_code, reason_label, reason_label_fa}]."""
    config = (context or {}).get('configuration')
    if config is None and report is not None:
        from field_reports.services.daily_report_aggregation import (
            resolve_project_reporting_configuration,
        )

        config = resolve_project_reporting_configuration(report.project_id, report.report_date)

    if config is not None and config.stoppage_reasons.exists():
        return [
            {
                'reason_code': r.reason_code,
                'reason_label': r.reason_label,
                'reason_label_fa': r.reason_label_fa,
            }
            for r in config.stoppage_reasons.all().order_by('display_order', 'reason_code')
        ]

    from project_templates.models import DEFAULT_STOPPAGE_REASONS

    return [
        {
            'reason_code': code,
            'reason_label': label_en,
            'reason_label_fa': label_fa,
        }
        for code, label_en, label_fa in DEFAULT_STOPPAGE_REASONS
    ]


def _machinery_row_contract_errors(report, validated: dict, index: int, vocab_codes: set[str], instance=None) -> list[dict]:
    from decimal import Decimal

    errors = []

    def err(field, code):
        return {
            'row': index,
            'field': field,
            'code': code,
            'message': ERROR_MESSAGES.get(code, code),
        }

    equipment_ref = validated.get('equipment_ref', getattr(instance, 'equipment_ref', None))
    if equipment_ref is not None:
        if getattr(equipment_ref, 'is_deleted', False) or str(equipment_ref.project_id) != str(report.project_id):
            errors.append(err('equipment_ref', REFERENCE_SCOPE_ERROR))

    for status_field in MACHINERY_STATUS_FIELDS:
        val = validated.get(status_field, getattr(instance, status_field, 0) if instance else 0)
        if val is None:
            val = 0
            validated[status_field] = 0
        if int(val) < 0:
            errors.append(err(status_field, STATUS_COUNT_NON_NEGATIVE_ERROR))

    op_hours = validated.get('operating_hours', getattr(instance, 'operating_hours', None) if instance else None)
    st_hours = validated.get('stoppage_hours', getattr(instance, 'stoppage_hours', None) if instance else None)
    rp_hours = validated.get('repair_hours', getattr(instance, 'repair_hours', None) if instance else None)

    for hr_field, hr_val in (
        ('operating_hours', op_hours),
        ('stoppage_hours', st_hours),
        ('repair_hours', rp_hours),
    ):
        if hr_val is not None and Decimal(str(hr_val)) < Decimal('0'):
            errors.append(err(hr_field, STATUS_COUNT_NON_NEGATIVE_ERROR))

    total_hours = (
        Decimal(str(op_hours or 0))
        + Decimal(str(st_hours or 0))
        + Decimal(str(rp_hours or 0))
    )
    if total_hours > Decimal('24'):
        errors.append(err('operating_hours', HOURS_EXCEED_DAY_LIMIT_ERROR))

    reason_code = (
        validated.get(
            'stoppage_reason_code',
            getattr(instance, 'stoppage_reason_code', '') if instance else '',
        )
        or ''
    ).strip()
    validated['stoppage_reason_code'] = reason_code

    if Decimal(str(st_hours or 0)) > Decimal('0') and not reason_code:
        errors.append(err('stoppage_reason_code', STOPPAGE_REASON_REQUIRED_ERROR))
    elif reason_code and reason_code not in vocab_codes:
        errors.append(err('stoppage_reason_code', STOPPAGE_REASON_NOT_IN_VOCABULARY_ERROR))

    return errors


def _machinery_cross_row_errors(all_rows_data: list[dict]) -> list[dict]:
    """Check per-identity 24h limit and mixed type/item sum consistency."""
    from collections import defaultdict
    from decimal import Decimal

    errors = []

    def err(index, field, code):
        return {
            'row': index,
            'field': field,
            'code': code,
            'message': ERROR_MESSAGES.get(code, code),
        }

    # 1. Per-equipment_ref cumulative hours <= 24
    hours_by_identity: dict[str, Decimal] = defaultdict(lambda: Decimal('0'))
    last_index_by_identity: dict[str, int] = {}
    for item in all_rows_data:
        eq_id = item.get('equipment_ref_id')
        if not eq_id:
            continue
        row_hours = (
            Decimal(str(item.get('operating_hours') or 0))
            + Decimal(str(item.get('stoppage_hours') or 0))
            + Decimal(str(item.get('repair_hours') or 0))
        )
        hours_by_identity[eq_id] += row_hours
        last_index_by_identity[eq_id] = item.get('index', 0)

    for eq_id, total_hr in hours_by_identity.items():
        if total_hr > Decimal('24'):
            errors.append(err(last_index_by_identity[eq_id], 'operating_hours', HOURS_EXCEED_DAY_LIMIT_ERROR))

    # 2. Mixed type-only and item-level rows for the same equipment_type must agree on status sums
    by_type: dict[str, dict[str, list[dict]]] = defaultdict(lambda: {'type_rows': [], 'item_rows': []})
    for item in all_rows_data:
        eq_type = (item.get('equipment_type') or '').strip()
        if not eq_type:
            continue
        if item.get('equipment_ref_id'):
            by_type[eq_type]['item_rows'].append(item)
        else:
            by_type[eq_type]['type_rows'].append(item)

    for eq_type, groups in by_type.items():
        type_rows = groups['type_rows']
        item_rows = groups['item_rows']
        if not type_rows or not item_rows:
            continue
        # Dedupe item_rows by equipment_ref_id when summing status counts
        deduped_items = {}
        for ir in item_rows:
            deduped_items[ir['equipment_ref_id']] = ir
        for status_field in MACHINERY_STATUS_FIELDS:
            type_sum = sum(int(r.get(status_field) or 0) for r in type_rows)
            item_sum = sum(int(r.get(status_field) or 0) for r in deduped_items.values())
            if type_sum != item_sum:
                target_idx = item_rows[-1].get('index', 0)
                errors.append(err(target_idx, 'status_total', MACHINERY_STATUS_SUMS_INCONSISTENT_ERROR))
                break

    return errors


@transaction.atomic
def validate_machinery_rows(report, rows, context=None) -> MachineryValidationResult:
    """Validate + persist §3 machinery child rows bound to this unit-report version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    vocabulary = resolve_stoppage_vocabulary(report, context=context)
    vocab_codes = {v['reason_code'] for v in vocabulary}

    if rows is None:
        rows = []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')
    if not rows:
        return MachineryValidationResult([], vocabulary=vocabulary)

    errors = []
    validated_Batch = []

    for index, row in enumerate(rows):
        serializer = UnitReportMachinerySectionSerializer(data=row, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            for field, detail in exc.detail.items():
                errors.extend(_error_from_drf(index, field, detail))
            continue

        validated = dict(serializer.validated_data)
        row_errors = _machinery_row_contract_errors(report, validated, index, vocab_codes)
        if row_errors:
            errors.extend(row_errors)
            continue
        validated_Batch.append((index, validated))

    if errors:
        raise SectionContractError(field_errors=errors)

    existing_rows = list(
        report.machinery_rows.filter(is_deleted=False).order_by('row_number', 'id')
    )
    combined_for_check = [
        {
            'index': 0,
            'equipment_type': ex.equipment_type,
            'equipment_ref_id': str(ex.equipment_ref_id) if ex.equipment_ref_id else None,
            'status_total': ex.status_total,
            'status_active': ex.status_active,
            'status_ready': ex.status_ready,
            'status_inactive': ex.status_inactive,
            'status_under_repair': ex.status_under_repair,
            'operating_hours': ex.operating_hours,
            'stoppage_hours': ex.stoppage_hours,
            'repair_hours': ex.repair_hours,
        }
        for ex in existing_rows
    ]
    for index, validated in validated_Batch:
        eq_ref = validated.get('equipment_ref')
        combined_for_check.append({
            'index': index,
            'equipment_type': validated.get('equipment_type'),
            'equipment_ref_id': str(eq_ref.id) if eq_ref is not None else None,
            'status_total': validated.get('status_total', 0),
            'status_active': validated.get('status_active', 0),
            'status_ready': validated.get('status_ready', 0),
            'status_inactive': validated.get('status_inactive', 0),
            'status_under_repair': validated.get('status_under_repair', 0),
            'operating_hours': validated.get('operating_hours'),
            'stoppage_hours': validated.get('stoppage_hours'),
            'repair_hours': validated.get('repair_hours'),
        })

    cross_errors = _machinery_cross_row_errors(combined_for_check)
    if cross_errors:
        raise SectionContractError(field_errors=cross_errors)

    from sub_reports.models import DisciplineSubReportMachinery

    next_row_num = (existing_rows[-1].row_number if existing_rows else 0) + 1
    saved = []
    for _index, validated in validated_Batch:
        if not validated.get('row_number'):
            validated['row_number'] = next_row_num
            next_row_num += 1
        saved.append(
            DisciplineSubReportMachinery.objects.create(sub_report=report, **validated)
        )

    return MachineryValidationResult(saved, vocabulary=vocabulary)


@transaction.atomic
def update_machinery_row(report, row, payload, context=None):
    """Validate + apply a partial §3 machinery row update bound to this version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    vocabulary = resolve_stoppage_vocabulary(report, context=context)
    vocab_codes = {v['reason_code'] for v in vocabulary}

    serializer = UnitReportMachinerySectionSerializer(
        instance=row, data=payload, context=context, partial=True,
    )
    try:
        serializer.is_valid(raise_exception=True)
    except DRFValidationError as exc:
        errors = []
        for field, detail in exc.detail.items():
            errors.extend(_error_from_drf(0, field, detail))
        raise SectionContractError(field_errors=errors)

    validated = dict(serializer.validated_data)
    row_errors = _machinery_row_contract_errors(
        report, validated, 0, vocab_codes, instance=row,
    )
    if row_errors:
        raise SectionContractError(field_errors=row_errors)

    other_rows = list(
        report.machinery_rows.filter(is_deleted=False).exclude(pk=row.pk).order_by('row_number', 'id')
    )
    eq_ref = validated.get('equipment_ref', row.equipment_ref)
    combined_for_check = [
        {
            'index': 0,
            'equipment_type': ex.equipment_type,
            'equipment_ref_id': str(ex.equipment_ref_id) if ex.equipment_ref_id else None,
            'status_total': ex.status_total,
            'status_active': ex.status_active,
            'status_ready': ex.status_ready,
            'status_inactive': ex.status_inactive,
            'status_under_repair': ex.status_under_repair,
            'operating_hours': ex.operating_hours,
            'stoppage_hours': ex.stoppage_hours,
            'repair_hours': ex.repair_hours,
        }
        for ex in other_rows
    ]
    combined_for_check.append({
        'index': 0,
        'equipment_type': validated.get('equipment_type', row.equipment_type),
        'equipment_ref_id': str(eq_ref.id) if eq_ref is not None else None,
        'status_total': validated.get('status_total', row.status_total),
        'status_active': validated.get('status_active', row.status_active),
        'status_ready': validated.get('status_ready', row.status_ready),
        'status_inactive': validated.get('status_inactive', row.status_inactive),
        'status_under_repair': validated.get('status_under_repair', row.status_under_repair),
        'operating_hours': validated.get('operating_hours', row.operating_hours),
        'stoppage_hours': validated.get('stoppage_hours', row.stoppage_hours),
        'repair_hours': validated.get('repair_hours', row.repair_hours),
    })

    cross_errors = _machinery_cross_row_errors(combined_for_check)
    if cross_errors:
        raise SectionContractError(field_errors=cross_errors)

    for attr, val in validated.items():
        setattr(row, attr, val)
    row.save()
    return row


# ---------------------------------------------------------------------------
# §4 Materials section validation + warehouse document resolution (T035/T036)
# ---------------------------------------------------------------------------


def resolve_warehouse_document(project_id, document_ref: str | None, material_ref_id=None):
    """Resolve a project-scoped warehouse document record (InventoryTransaction) by document_ref (R5)."""
    doc_ref = (document_ref or '').strip()
    if not doc_ref or not project_id:
        return None
    from resources.models import InventoryTransaction

    base_qs = InventoryTransaction.objects.filter(
        project_id=project_id,
        document_ref=doc_ref,
        is_deleted=False,
    )
    if material_ref_id:
        matched = base_qs.filter(material_id=material_ref_id).order_by('-tx_date', '-created_at').first()
        if matched is not None:
            return matched
    return base_qs.order_by('-tx_date', '-created_at').first()


@transaction.atomic
def validate_material_rows(report, rows, context=None):
    """Validate + persist §4 material child rows bound to this unit-report version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    errors = []
    saved = []
    rows = rows if rows is not None else []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')

    from sub_reports.models import DisciplineSubReportMaterial

    for index, row in enumerate(rows):
        serializer = UnitReportMaterialSectionSerializer(data=row, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            for field, detail in exc.detail.items():
                errors.extend(_error_from_drf(index, field, detail))
            continue

        validated = dict(serializer.validated_data)
        saved.append(
            DisciplineSubReportMaterial.objects.create(sub_report=report, **validated)
        )

    if errors:
        raise SectionContractError(field_errors=errors)
    return saved


@transaction.atomic
def update_material_row(report, row, payload, context=None):
    """Validate + apply a partial §4 material row update bound to this version."""
    if context is None:
        context = {}
    context.setdefault('report', report)
    serializer = UnitReportMaterialSectionSerializer(
        instance=row, data=payload, context=context, partial=True,
    )
    try:
        serializer.is_valid(raise_exception=True)
    except DRFValidationError as exc:
        errors = []
        for field, detail in exc.detail.items():
            errors.extend(_error_from_drf(0, field, detail))
        raise SectionContractError(field_errors=errors)

    validated = dict(serializer.validated_data)
    for attr, val in validated.items():
        setattr(row, attr, val)
    row.save()
    return row


def _plain_text(value) -> str:
    """Strip markup so free text cannot drive structure (FR-041)."""
    import re
    text = '' if value is None else str(value)
    return re.sub(r'<[^>]*>', '', text).strip()


def _stakeholder_in_other_project(project_id, raw):
    import uuid
    from projects.models import Stakeholder

    try:
        parsed = uuid.UUID(str(raw))
    except (TypeError, ValueError):
        return False
    stakeholder = Stakeholder.objects.filter(id=parsed).first()
    if stakeholder is None:
        return False
    return str(stakeholder.project_id) != str(project_id)


@transaction.atomic
def validate_concrete_rows(report, rows, context=None):
    """Validate + persist §2.5 concrete pour rows."""
    from decimal import Decimal

    from sub_reports.models import DisciplineSubReportConcrete, SamplingState
    from sub_reports.serializers import UnitReportConcreteSectionSerializer

    if context is None:
        context = {}
    context.setdefault('report', report)
    errors = []
    saved = []
    rows = rows if rows is not None else []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')

    for index, row in enumerate(rows):
        payload = dict(row)
        volume = payload.get('volume_m3')
        try:
            volume_value = Decimal(str(volume))
        except Exception:
            volume_value = None
        if volume_value is None or volume_value <= 0:
            errors.append({
                'row': index,
                'field': 'volume_m3',
                'code': VOLUME_POSITIVE_ERROR,
                'message': str(ERROR_MESSAGES[VOLUME_POSITIVE_ERROR]),
            })
            continue
        plant = payload.get('batching_plant') or ''
        if plant and _stakeholder_in_other_project(report.project_id, plant):
            errors.append({
                'row': index,
                'field': 'batching_plant',
                'code': REFERENCE_SCOPE_ERROR,
                'message': str(ERROR_MESSAGES[REFERENCE_SCOPE_ERROR]),
            })
            continue
        state = payload.get('sampling_state') or SamplingState.NOT_SAMPLED
        if state == SamplingState.SAMPLING_DECLARED:
            code = (payload.get('lab_sample_code') or '').strip()
            sheets = payload.get('test_sheet_count')
            if not code or sheets in (None, ''):
                errors.append({
                    'row': index,
                    'field': 'lab_sample_code',
                    'code': SAMPLING_REQUIRES_TEST_INFORMATION,
                    'message': str(ERROR_MESSAGES[SAMPLING_REQUIRES_TEST_INFORMATION]),
                })
                continue
        serializer = UnitReportConcreteSectionSerializer(data=payload, context=context)
        try:
            serializer.is_valid(raise_exception=True)
        except DRFValidationError as exc:
            for field, detail in exc.detail.items():
                errors.extend(_error_from_drf(index, field, detail))
            continue
        saved.append(
            DisciplineSubReportConcrete.objects.create(
                sub_report=report, **serializer.validated_data,
            )
        )
    if errors:
        raise SectionContractError(field_errors=errors)
    return saved


def _user_or_none(raw):
    from django.contrib.auth import get_user_model

    if not raw:
        return None
    return get_user_model().objects.filter(pk=raw).first()


@transaction.atomic
def validate_narrative_rows(report, rows, context=None):
    """Persist structured narrative rows. General notes stay type ``other``."""
    from datetime import date as date_cls

    from sub_reports.models import (
        DisciplineSubReportGeneralActivity,
        DisciplineSubReportHseIncident,
        DisciplineSubReportIssue,
        DisciplineSubReportNote,
        DisciplineSubReportVisit,
        HseIncidentSeverity,
        IssueKind,
        SubReportNoteType,
    )

    rows = rows if rows is not None else []
    if not isinstance(rows, list):
        raise SectionContractError(code='invalid_row_payload')
    errors = []
    saved = []
    severities = {choice for choice, _label in HseIncidentSeverity.choices}

    for index, row in enumerate(rows):
        payload = dict(row or {})
        kind = (payload.get('kind') or '').strip()
        if not kind:
            if payload.get('severity') is not None or 'immediate_action' in payload:
                kind = 'hse'
            elif payload.get('activity_description'):
                kind = 'general_activity'
            else:
                kind = 'visit'

        if kind == 'barrier':
            owner = _user_or_none(payload.get('owner_user'))
            due = payload.get('due_date')
            if owner is None or not due:
                errors.append({
                    'row': index,
                    'field': 'owner_user',
                    'code': BARRIER_OWNER_DUE_ERROR,
                    'message': 'owner and due_date are required for a barrier',
                })
                continue
            if isinstance(due, str):
                due = date_cls.fromisoformat(due)
            saved.append(DisciplineSubReportIssue.objects.create(
                sub_report=report,
                row_number=payload.get('row_number') or 1,
                kind=IssueKind.BARRIER,
                text=_plain_text(payload.get('text')),
                owner_user=owner,
                due_date=due,
            ))
            continue

        if kind == 'issue':
            owner = _user_or_none(payload.get('owner_user'))
            due = payload.get('due_date') or None
            if isinstance(due, str) and due:
                due = date_cls.fromisoformat(due)
            saved.append(DisciplineSubReportIssue.objects.create(
                sub_report=report,
                row_number=payload.get('row_number') or 1,
                kind=IssueKind.ISSUE,
                text=_plain_text(payload.get('text')),
                owner_user=owner,
                due_date=due,
            ))
            continue

        if kind == 'visit':
            visit = DisciplineSubReportVisit.objects.create(
                sub_report=report,
                row_number=payload.get('row_number') or 1,
                text=_plain_text(payload.get('text')),
            )
            visit.kind = 'visit'
            saved.append(visit)
            continue

        if kind == 'hse':
            severity = (payload.get('severity') or '').strip()
            action = (payload.get('immediate_action') or '').strip()
            if severity not in severities:
                errors.append({
                    'row': index,
                    'field': 'severity',
                    'code': 'invalid_severity',
                    'message': 'severity must be minor, moderate, or major',
                })
                continue
            if not action:
                errors.append({
                    'row': index,
                    'field': 'immediate_action',
                    'code': HSE_IMMEDIATE_ACTION_ERROR,
                    'message': 'immediate_action is required',
                })
                continue
            saved.append(DisciplineSubReportHseIncident.objects.create(
                sub_report=report,
                row_number=payload.get('row_number') or 1,
                text=_plain_text(payload.get('text')),
                severity=severity,
                immediate_action=_plain_text(action),
            ))
            continue

        if kind == 'general_activity':
            activity = DisciplineSubReportGeneralActivity.objects.create(
                sub_report=report,
                row_number=payload.get('row_number') or 1,
                activity_description=_plain_text(payload.get('activity_description')),
                location=_plain_text(payload.get('location') or ''),
                quantity=payload.get('quantity') or None,
                unit=payload.get('unit') or None,
                notes=_plain_text(payload.get('notes') or ''),
            )
            activity.kind = 'general_activity'
            saved.append(activity)
            continue

        note = DisciplineSubReportNote.objects.create(
            sub_report=report,
            note_type=SubReportNoteType.OTHER,
            text=_plain_text(payload.get('text') or payload.get('activity_description') or ''),
            row_number=payload.get('row_number') or 1,
        )
        note.kind = 'other'
        saved.append(note)

    if errors:
        raise SectionContractError(field_errors=errors)
    return saved

