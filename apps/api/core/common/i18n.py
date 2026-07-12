"""Helpers for localized API error payloads."""
from __future__ import annotations

from typing import Any

from django.utils.encoding import force_str
from django.utils.functional import Promise


def localize_api_payload(value: Any) -> Any:
    """Recursively coerce lazy translation objects to localized strings."""
    if isinstance(value, Promise):
        return force_str(value)
    if isinstance(value, dict):
        return {key: localize_api_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [localize_api_payload(item) for item in value]
    return value
