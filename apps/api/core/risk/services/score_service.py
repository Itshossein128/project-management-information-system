"""Composite risk score helpers (FR-RSK)."""

from __future__ import annotations

from risk.models import RiskStatus


def compute_composite_score(
    probability_level: int | None,
    impact_severity_level: int | None,
) -> int | None:
    """Return probability × impact (1–25), or None if either level is missing."""
    if probability_level is None or impact_severity_level is None:
        return None
    if not (1 <= probability_level <= 5 and 1 <= impact_severity_level <= 5):
        return None
    return probability_level * impact_severity_level


def default_status_for_incomplete_score(
    probability_level: int | None,
    impact_severity_level: int | None,
    *,
    explicit_status: str | None = None,
) -> str | None:
    """
    When score inputs are incomplete and the client omits status, default to under_review.
    Returns None when caller already supplied an explicit status (use that instead).
    """
    if explicit_status is not None and explicit_status != '':
        return None
    if probability_level is None or impact_severity_level is None:
        return RiskStatus.UNDER_REVIEW
    return None


def normalize_status(raw: str | None) -> str | None:
    """Map legacy barrier statuses to FR RiskStatus codes."""
    if raw is None:
        return None
    mapping = {
        'in_progress': RiskStatus.UNDER_REVIEW,
        'resolved': RiskStatus.CLOSED,
    }
    return mapping.get(raw, raw)
