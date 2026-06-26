"""Resolve resource_type and resource_id from API request paths."""
import re
import uuid
from dataclasses import dataclass

PROJECT_UUID = (
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)

RESOURCE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ('project', re.compile(rf'^/api/v1/projects/(?P<id>{PROJECT_UUID})/?$')),
    ('project_member', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/members/(?P<id>{PROJECT_UUID})/?$'
    )),
    ('project_position', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/positions/(?P<id>{PROJECT_UUID})/?$'
    )),
    ('table', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/tables/(?P<id>\d+)/?$'
    )),
    ('table_by_slug', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/tables/by_slug/(?P<slug>[^/]+)/?$'
    )),
    ('field', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/tables/\d+/fields/(?P<id>\d+)/?$'
    )),
    ('dynamic_row', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/tables/[^/]+/rows/(?P<id>[^/]+)/?$'
    )),
    ('stored_file', re.compile(rf'^/api/v1/files/(?P<id>{PROJECT_UUID})/')),
    ('stored_file_upload', re.compile(
        rf'^/api/v1/projects/(?P<project_id>{PROJECT_UUID})/files/upload-url/?$'
    )),
]


@dataclass(frozen=True)
class ResolvedResource:
    resource_type: str
    resource_id: uuid.UUID | None
    project_id: uuid.UUID | None = None


def _parse_uuid(value: str | None) -> uuid.UUID | None:
    if not value:
        return None
    try:
        return uuid.UUID(value)
    except (TypeError, ValueError):
        return None


def resolve_resource(path: str, project_id: uuid.UUID | None = None) -> ResolvedResource | None:
    """Match path against known API patterns and return resource metadata."""
    for resource_type, pattern in RESOURCE_PATTERNS:
        match = pattern.match(path)
        if not match:
            continue
        groups = match.groupdict()
        resource_id = _parse_uuid(groups.get('id'))
        resolved_project = _parse_uuid(groups.get('project_id')) or project_id
        if resource_type == 'table_by_slug':
            return ResolvedResource(
                resource_type='table',
                resource_id=None,
                project_id=resolved_project,
            )
        if resource_type == 'dynamic_row' and groups.get('id'):
            try:
                resource_id = uuid.UUID(groups['id'])
            except ValueError:
                pass
        return ResolvedResource(
            resource_type=resource_type,
            resource_id=resource_id,
            project_id=resolved_project,
        )
    if project_id is not None:
        return ResolvedResource(resource_type='project', resource_id=project_id, project_id=project_id)
    return None
