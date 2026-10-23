"""Shared section-level rules for unit-report child rows (feature 033).

Shift recognition uses the full synonym list and an exact-resolve contract:
anything outside the list is refused with ``invalid_shift`` — never silently
remapped (FR-003, contract unit-report-sections-api.md §1).
"""
from __future__ import annotations

from field_reports.models import ActivityRowShift

# Full synonym list (English compact/underscored + Persian with spaces,
# Persian and English digits). Every canonical value also maps to itself.
SHIFT_SYNONYMS: dict[str, str] = {
    'shift_1': ActivityRowShift.SHIFT_1,
    'shift1': ActivityRowShift.SHIFT_1,
    'شیفت1': ActivityRowShift.SHIFT_1,
    'شیفت_1': ActivityRowShift.SHIFT_1,
    'شیفت ۱': ActivityRowShift.SHIFT_1,
    'شیفت 1': ActivityRowShift.SHIFT_1,
    'shift_2': ActivityRowShift.SHIFT_2,
    'shift2': ActivityRowShift.SHIFT_2,
    'شیفت2': ActivityRowShift.SHIFT_2,
    'شیفت_2': ActivityRowShift.SHIFT_2,
    'شیفت ۲': ActivityRowShift.SHIFT_2,
    'شیفت 2': ActivityRowShift.SHIFT_2,
    'shift_3': ActivityRowShift.SHIFT_3,
    'shift3': ActivityRowShift.SHIFT_3,
    'شیفت3': ActivityRowShift.SHIFT_3,
    'شیفت_3': ActivityRowShift.SHIFT_3,
    'شیفت ۳': ActivityRowShift.SHIFT_3,
    'شیفت 3': ActivityRowShift.SHIFT_3,
}

SHIFT_CODES = {ActivityRowShift.SHIFT_1, ActivityRowShift.SHIFT_2, ActivityRowShift.SHIFT_3}


def resolve_shift(raw) -> str | None:
    """Resolve a raw shift value, else None – caller refuses with a code."""
    if raw is None:
        return None
    normalized = str(raw).strip()
    if not normalized:
        return None
    canonical = SHIFT_SYNONYMS.get(normalized)
    if canonical is not None:
        return canonical
    lowered = normalized.lower()
    return SHIFT_SYNONYMS.get(lowered)
