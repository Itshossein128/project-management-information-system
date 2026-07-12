"""Redis-backed response caching helpers."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

from django.core.cache import cache


def cache_key(prefix: str, project_id, *parts) -> str:
    raw = ':'.join(str(p) for p in (project_id, *parts) if p is not None)
    return f'{prefix}:{raw}'


def get_cached_or_compute(key: str, ttl: int, compute: Callable[[], Any]) -> Any:
    cached = cache.get(key)
    if cached is not None:
        return cached
    value = compute()
    cache.set(key, value, ttl)
    return value


def params_fingerprint(params: dict) -> str:
    return hashlib.md5(json.dumps(params, sort_keys=True, default=str).encode()).hexdigest()[:12]
