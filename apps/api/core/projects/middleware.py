import re
import uuid

from django.http import JsonResponse


PROJECT_UUID_RE = re.compile(
    r'^/api/v1/projects/(?P<project_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'
)


class ProjectTenancyMiddleware:
    """Extract project_id from nested /api/v1/projects/{uuid}/ routes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.project_id = None
        match = PROJECT_UUID_RE.match(request.path)
        if match:
            try:
                request.project_id = uuid.UUID(match.group('project_id'))
            except ValueError:
                return JsonResponse({'detail': 'Invalid project id.'}, status=400)
        return self.get_response(request)
