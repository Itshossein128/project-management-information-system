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
from sub_reports.serializers import UnitReportActivitySectionSerializer

CONTRACTOR_SCOPE_ERROR = 'contractor_not_in_project_scope'
CONTRACTOR_REQUIRED_ERROR = 'contractor_required'
ACTIVITY_SCOPE_ERROR = 'activity_not_in_project_scope'
QUANTITY_POSITIVE_ERROR = 'quantity_must_be_positive'

# Stable section error codes and their localized fa messages (T043 will wire
# the web locale files; the API layer relies on the messages below).
ERROR_MESSAGES = {
    CONTRACTOR_SCOPE_ERROR: _('این پیمانکار در محدوده پروژه نیست'),
    CONTRACTOR_REQUIRED_ERROR: _('انتخاب پیمانکار الزامی است'),
    ACTIVITY_SCOPE_ERROR: _('فعالیت از محدوده پروژه خارج است یا غیرفعال است'),
    QUANTITY_POSITIVE_ERROR: _('مقدار مدیراً باید بزرگ‌تر از صفر باشد'),
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
        if validated.get('quantity') is not None and validated['quantity'] <= 0:
            errors.append({
                'row': index,
                'field': 'quantity',
                'code': QUANTITY_POSITIVE_ERROR,
                'message': str(ERROR_MESSAGES[QUANTITY_POSITIVE_ERROR]),
            })
            continue

        ref = validated.get('activity_ref')
        if ref is None or not _activity_active_and_within_project(ref, report.project_id):
            errors.append({
                'row': index,
                'field': 'activity_ref',
                'code': ACTIVITY_SCOPE_ERROR,
                'message': str(ERROR_MESSAGES[ACTIVITY_SCOPE_ERROR]),
            })
            continue

        contractor = validated.get('contractor_ref')
        if contractor is None:
            errors.append({
                'row': index,
                'field': 'contractor_ref',
                'code': CONTRACTOR_REQUIRED_ERROR,
                'message': str(ERROR_MESSAGES[CONTRACTOR_REQUIRED_ERROR]),
            })
            continue
        if not _contractor_within_project(contractor, report.project_id):
            errors.append({
                'row': index,
                'field': 'contractor_ref',
                'code': CONTRACTOR_SCOPE_ERROR,
                'message': str(ERROR_MESSAGES[CONTRACTOR_SCOPE_ERROR]),
            })
            continue

        if errors:
            continue

        row_number = validated.pop('row_number', None)
        if row_number is None:
            row_number = _next_row_number(report, 'activities')
        saved.append(serializer.save(sub_report=report, row_number=row_number))
    if errors:
        raise SectionContractError(field_errors=errors)
    return saved


def _next_row_number(report, related_name):
    current = list(
        getattr(report, related_name).filter(is_deleted=False)
        .values_list('row_number', flat=True)
    )
    return (max(current) if current else 0) + 1
