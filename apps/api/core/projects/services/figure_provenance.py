"""Canonical dashboard figure provenance shape (FR-RPT / progress-report aligned)."""

from __future__ import annotations

from typing import Any


FIGURE_STATUS_OK = 'ok'
FIGURE_STATUS_INACTIVE = 'inactive'
FIGURE_STATUS_UNAVAILABLE = 'unavailable'


def make_figure(
    *,
    figure_key: str,
    value: Any = None,
    status: str = FIGURE_STATUS_OK,
    source_type: str = '',
    source_id=None,
    source_path: str = '',
    source_approved: bool = False,
    last_updated_at=None,
    label_unapproved: bool = False,
    drill_href: str | None = None,
) -> dict:
    """Build a figure dict. Inactive figures must use value=None (never fabricated 0 success)."""
    if status == FIGURE_STATUS_INACTIVE:
        value = None
    fig = {
        'figure_key': figure_key,
        'value': value,
        'status': status,
        'source_type': source_type,
        'source_id': str(source_id) if source_id else None,
        'source_path': source_path or '',
        'source_approved': bool(source_approved),
        'last_updated_at': last_updated_at.isoformat() if last_updated_at else None,
        'label_unapproved': bool(label_unapproved),
        'drill': {'href': drill_href} if drill_href else None,
    }
    return fig


def make_drill_row(
    *,
    id,
    display: str,
    approval_status: str = '',
    approved: bool = False,
    last_updated_at=None,
    amount=None,
    source_path: str = '',
) -> dict:
    return {
        'id': str(id),
        'display': display,
        'amount': amount,
        'approval_status': approval_status,
        'approved': bool(approved),
        'last_updated_at': last_updated_at.isoformat() if last_updated_at else None,
        'source_path': source_path or '',
    }
