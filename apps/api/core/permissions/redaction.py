"""Nested payload redaction for wage/rate and contact fields (A6-P4)."""

from __future__ import annotations

from typing import Any

WAGE_KEYS = frozenset(
    {
        'wage',
        'wages',
        'rate',
        'rates',
        'hourly_rate',
        'daily_rate',
        'labor_rate',
        'unit_rate',
        'pay_rate',
    }
)

CONTACT_KEYS = frozenset(
    {
        'email',
        'mobile',
        'phone',
        'telephone',
        'contact_email',
        'contact_mobile',
        'contact_phone',
    }
)

PERSON_CONTACT_KEYS = frozenset({'email', 'mobile', 'phone', 'telephone'})


def _should_strip_wage(key: str, permissions: set[str]) -> bool:
    return key in WAGE_KEYS and 'view_wage' not in permissions


def _should_strip_contact(key: str, permissions: set[str], *, person: bool) -> bool:
    if person:
        if key not in PERSON_CONTACT_KEYS and key not in CONTACT_KEYS:
            return False
        return 'view_person_contacts' not in permissions
    if key not in CONTACT_KEYS:
        return False
    return 'view_sensitive_contacts' not in permissions


def redact_sensitive_payload(
    payload: Any,
    permissions: set[str] | None = None,
    *,
    redact_wages: bool = True,
    redact_stakeholder_contacts: bool = False,
    redact_person_contacts: bool = False,
) -> Any:
    """Return a deep copy-like structure with unauthorized sensitive keys cleared.

    Clearing sets scalar contact/wage values to ``None`` and adds
    ``{key}_redacted: True`` beside dict parents when a top-level key is removed.
    Nested dicts and lists are walked recursively.
    """
    perms = set(permissions or ())
    return _walk(
        payload,
        perms,
        redact_wages=redact_wages,
        redact_stakeholder_contacts=redact_stakeholder_contacts,
        redact_person_contacts=redact_person_contacts,
    )


def _walk(
    value: Any,
    permissions: set[str],
    *,
    redact_wages: bool,
    redact_stakeholder_contacts: bool,
    redact_person_contacts: bool,
) -> Any:
    if isinstance(value, list):
        return [
            _walk(
                item,
                permissions,
                redact_wages=redact_wages,
                redact_stakeholder_contacts=redact_stakeholder_contacts,
                redact_person_contacts=redact_person_contacts,
            )
            for item in value
        ]
    if not isinstance(value, dict):
        return value

    out: dict[str, Any] = {}
    redacted_markers: list[str] = []
    for key, child in value.items():
        strip = False
        if redact_wages and _should_strip_wage(str(key), permissions):
            strip = True
        elif redact_person_contacts and _should_strip_contact(str(key), permissions, person=True):
            strip = True
        elif redact_stakeholder_contacts and _should_strip_contact(
            str(key), permissions, person=False
        ):
            strip = True
        if strip:
            out[key] = None
            redacted_markers.append(str(key))
            continue
        out[key] = _walk(
            child,
            permissions,
            redact_wages=redact_wages,
            redact_stakeholder_contacts=redact_stakeholder_contacts,
            redact_person_contacts=redact_person_contacts,
        )
    for key in redacted_markers:
        marker = f'{key}_redacted'
        if marker not in out:
            out[marker] = True
    return out
