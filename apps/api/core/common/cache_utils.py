"""Redis cache invalidation for project-scoped endpoints."""

from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def _redis_client():
    try:
        import redis

        return redis.from_url(settings.CELERY_BROKER_URL)
    except Exception:
        return None


def invalidate_project_caches(project_id) -> None:
    """Invalidate cached KPI, variance, activity log, and personnel summary data."""
    client = _redis_client()
    if client is None:
        return
    patterns = [
        f's_curve:{project_id}:*',
        f'kpis:{project_id}:*',
        f'variance:{project_id}:*',
        f'activity_log:{project_id}:*',
        f'personnel_summary:{project_id}:*',
    ]
    for pattern in patterns:
        try:
            for key in client.scan_iter(match=pattern):
                client.delete(key)
        except Exception as exc:
            logger.warning('Cache invalidation failed for %s: %s', pattern, exc)
