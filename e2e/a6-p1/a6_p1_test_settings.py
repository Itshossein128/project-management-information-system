"""Isolated settings for the A6-P1 real E2E server; never use for a live database."""
import os
from config.settings import *  # noqa: F403

expected = os.environ.get('A6_P1_E2E_DB', '')
if not expected.startswith('velora_a6_p1_e2e_') or DATABASES['default']['NAME'] != expected:  # noqa: F405
    raise RuntimeError('A6-P1 E2E settings require a matching isolated test database')
# Keep authentication rate limiting enabled, but isolate its counters from the user's Redis.
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'velora-a6-p1-e2e'}}
# This isolated test server runs in one process; production still requires shared cache.
SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003', 'django_ratelimit.W001']
