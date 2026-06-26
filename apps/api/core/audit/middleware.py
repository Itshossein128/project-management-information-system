import json
import logging

from django.utils.deprecation import MiddlewareMixin

from audit.resolve_resource import resolve_resource
from audit.service import build_audit_payload, record_audit_log

logger = logging.getLogger(__name__)

AUDIT_METHODS = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})
SKIP_PATH_PREFIXES = ('/api/schema/', '/api/docs/', '/api/redoc/', '/admin/')


class AuditLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.method not in AUDIT_METHODS:
            return response
        if any(request.path.startswith(p) for p in SKIP_PATH_PREFIXES):
            return response
        if response.status_code >= 400:
            return response
        try:
            actor = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            changes = {}
            if hasattr(request, 'data') and request.data is not None:
                try:
                    changes = dict(request.data)
                except (TypeError, ValueError):
                    changes = {'data': str(request.data)}
            elif hasattr(request, '_body'):
                raw = request._body
                if raw:
                    try:
                        changes = json.loads(raw.decode('utf-8'))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        changes = {'raw': 'binary or invalid json'}

            project_id = getattr(request, 'project_id', None)
            resolved = resolve_resource(request.path, project_id=project_id)
            resource_type = ''
            resource_id = None
            project_fk_id = project_id
            if resolved:
                resource_type = resolved.resource_type
                resource_id = resolved.resource_id
                if resolved.project_id is not None:
                    project_fk_id = resolved.project_id

            payload = build_audit_payload(
                actor_id=actor.id if actor else None,
                project_id=project_fk_id,
                http_method=request.method,
                path=request.path,
                resource_type=resource_type,
                resource_id=resource_id,
                changes=changes if isinstance(changes, dict) else {'data': changes},
                ip_address=self._client_ip(request),
            )
            record_audit_log(payload)
        except Exception:
            logger.exception('Failed to write audit log')
        return response

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
