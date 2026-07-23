"""django-ratelimit helpers for auth endpoints."""
from __future__ import annotations

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django_ratelimit.decorators import ratelimit


def ratelimit_view(request, exception=None):
    """RATELIMIT_VIEW handler — return 429 with localized message."""
    return JsonResponse(
        {'detail': _('Too many requests. Please try again later.')},
        status=429,
    )


def handle_ratelimit_403(request, exception=None):
    """Django handler403 — return 429 JSON for django-ratelimit blocks."""
    from django_ratelimit.exceptions import Ratelimited

    if isinstance(exception, Ratelimited):
        return ratelimit_view(request, exception)
    from django.views.defaults import permission_denied

    return permission_denied(request, exception)


def auth_ratelimit(rate: str):
    """Apply IP-based POST rate limit to a DRF class-based view."""

    def decorator(cls):
        return method_decorator(
            ratelimit(key='ip', rate=rate, method='POST', block=True),
            name='dispatch',
        )(cls)

    return decorator
