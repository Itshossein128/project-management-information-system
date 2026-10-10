from django.core.cache import cache
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from redis.exceptions import RedisError


@require_GET
def health(request):
    """Check required dependencies without generating the OpenAPI schema."""
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        cache.get('velora:health')
    except (DatabaseError, RedisError, OSError):
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
