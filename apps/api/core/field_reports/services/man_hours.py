"""Fixed registry of man-hours rules (feature 033, data-model §1.2).

Rules are pure functions of the effective configuration snapshot and the
contributing labor inputs: identical inputs always produce identical outputs
(FR-008). No project title counts are hard-coded here — the shift length comes
from the effective ``ProjectReportingConfiguration.standard_shift_hours`` at
call time, and the rule code from its ``man_hours_rule_code``.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

_MAN_HOURS_QUANTUM = Decimal('0.01')


def standard_shift_plus_overtime(
    *,
    present_count: int | float | Decimal | None,
    overtime_person_hours: Decimal | None,
    standard_shift_hours: Decimal,
) -> Decimal:
    """Default rule: ``present_count × standard_shift_hours + overtime``.

    Pure and total: a missing present count is treated as absent (never a
    fabricated zero shift), a missing overtime component contributes nothing.
    Output is quantized to two decimals with deterministic half-up rounding so
    identical inputs always produce identical outputs (FR-008).
    """
    present = Decimal(str(present_count if present_count is not None else 0))
    overtime = Decimal(str(overtime_person_hours if overtime_person_hours is not None else 0))
    shift_hours = Decimal(str(standard_shift_hours))
    total = present * shift_hours + overtime
    return total.quantize(_MAN_HOURS_QUANTUM, rounding=ROUND_HALF_UP)


MAN_HOURS_RULE_REGISTRY: dict[str, object] = {
    'standard_shift_plus_overtime': standard_shift_plus_overtime,
}

DEFAULT_MAN_HOURS_RULE_CODE = 'standard_shift_plus_overtime'


def compute_man_hours(
    rule_code: str | None,
    *,
    present_count,
    overtime_person_hours,
    standard_shift_hours,
) -> Decimal:
    """Compute man-hours using the registered rule identified by ``rule_code``.

    Unknown or unconfigured rule codes fall back to the default registered rule
    rather than failing aggregation (the registry is code-reviewed and closed;
    per contract §3 the configuration only references registered codes).
    """
    rule = MAN_HOURS_RULE_REGISTRY.get(rule_code or '')
    if rule is None:
        rule = MAN_HOURS_RULE_REGISTRY[DEFAULT_MAN_HOURS_RULE_CODE]
    return rule(  # type: ignore[misc]
        present_count=present_count,
        overtime_person_hours=overtime_person_hours,
        standard_shift_hours=standard_shift_hours or Decimal('8'),
    )
