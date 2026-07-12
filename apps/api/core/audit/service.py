"""Persist audit log entries from middleware or async consumer."""
import logging
import uuid
from typing import Any

from django.conf import settings

from audit.models import AuditLog

logger = logging.getLogger(__name__)


def build_audit_payload(
    *,
    actor_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    http_method: str,
    path: str,
    resource_type: str,
    resource_id: uuid.UUID | None,
    changes: dict[str, Any],
    ip_address: str | None,
) -> dict[str, Any]:
    return {
        'actor_id': str(actor_id) if actor_id else None,
        'project_id': str(project_id) if project_id else None,
        'http_method': http_method,
        'path': path,
        'resource_type': resource_type,
        'resource_id': str(resource_id) if resource_id else None,
        'changes': changes,
        'ip_address': ip_address,
    }


def persist_audit_log(payload: dict[str, Any]) -> AuditLog:
    actor_id = payload.get('actor_id')
    project_id = payload.get('project_id')
    resource_id = payload.get('resource_id')
    return AuditLog.objects.create(
        actor_id=uuid.UUID(actor_id) if actor_id else None,
        project_id=uuid.UUID(project_id) if project_id else None,
        http_method=payload.get('http_method', ''),
        path=payload.get('path', '')[:512],
        resource_type=payload.get('resource_type', ''),
        resource_id=uuid.UUID(resource_id) if resource_id else None,
        changes=payload.get('changes') or {},
        ip_address=payload.get('ip_address'),
    )


def record_audit_log(payload: dict[str, Any]) -> None:
    """Publish audit event asynchronously; fall back to synchronous DB write."""
    if not getattr(settings, 'AUDIT_LOG_ASYNC', True):
        persist_audit_log(payload)
        return
    try:
        from events.publisher import EventPublisher

        EventPublisher().publish(
            'audit.log',
            payload,
            project_id=payload.get('project_id'),
        )
    except Exception:
        logger.exception('Async audit publish failed; writing synchronously')
        persist_audit_log(payload)
