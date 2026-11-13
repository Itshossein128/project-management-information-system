"""
Django settings for Velora API.
"""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

_DEBUG = os.environ.get('DEBUG', 'true').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if _DEBUG:
        SECRET_KEY = 'django-insecure-gw$5z@-^7ca^l^uobo6x(y)i(l@_3!gkplz!6#*p6n6cl_!sgm'
    else:
        raise ImproperlyConfigured(
            'The SECRET_KEY environment variable must be set when DEBUG is False.'
        )

DEBUG = _DEBUG

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'django_ratelimit',
    'django_celery_results',
    'treebeard',
    'common',
    'authentication',
    'master_data',
    'projects',
    'schedule',
    'field_reports',
    'concrete_operations',
    'hr',
    'sub_reports',
    'notifications',
    'resources',
    'cost_control',
    'contracts',
    'cash_flow',
    'subcontractors',
    'documents',
    'workflow',
    'economic',
    'risk',
    'decision_support',
    'alerts',
    'audit',
    'storage',
    'events',
    'business_meta',
    'wbs',
    'project_templates',
    'inventory',
    'procurement',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'projects.middleware.ProjectTenancyMiddleware',
    'audit.middleware.AuditLogMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

if os.environ.get('IMPORT_HELPER') == '1':
    # Model import asks the backend for identifier limits. An empty in-memory
    # database satisfies that without credentials or a project connection.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL', 'postgres://ipcas:ipcas@localhost:5433/ipcas'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
if 'TEST_DATABASE_NAME' in os.environ:
    DATABASES['default']['TEST'] = {'NAME': os.environ['TEST_DATABASE_NAME']}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en'
LANGUAGES = [
    ('en', 'English'),
    ('fa', 'Persian'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'authentication.User'

AUTHENTICATION_BACKENDS = [
    'authentication.backends.UsernameOrMobileBackend',
    'django.contrib.auth.backends.ModelBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'authentication.jwt.AccountJWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'config.pagination.DefaultPageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'authentication.throttles.BurstAnonRateThrottle',
        'authentication.throttles.RoleAwareUserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '60/min',
        'user': '600/min',
        'admin': '1200/min',
        'hr': '900/min',
        'login': '10/min',
    },
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Velora API',
    'DESCRIPTION': 'Velora project control platform API',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,
    'SWAGGER_UI_DIST': 'SIDECAR',
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'TAGS': [
        {'name': 'Authentication', 'description': 'JWT auth, password reset'},
        {'name': 'Projects', 'description': 'Project foundation (blueprint Module 1)'},
        {'name': 'Project meta', 'description': 'Dynamic schema, members, positions'},
        {'name': 'Storage', 'description': 'S3 presigned file upload/download'},
        {'name': 'Items', 'description': 'Legacy global inventory (deprecated)'},
    ],
}

SIMPLE_JWT = {
    'CHECK_REVOKE_TOKEN': True,
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'USER_AUTHENTICATION_RULE': 'authentication.services.account_can_authenticate',
}

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000',
    ).split(',')
    if origin.strip()
]

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@velora.local')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
# Feature 037: versioned unit sync stays off until an isolated test or rollout enables it.
V2_OFFLINE_SYNC_ENABLED = os.environ.get('V2_OFFLINE_SYNC_ENABLED', 'false').lower() in ('1', 'true', 'yes')

# Alert notification channels (K-04): in_app, email, sms
ALERT_NOTIFY_CHANNELS = os.environ.get('ALERT_NOTIFY_CHANNELS', 'in_app,email')
SMS_PROVIDER = os.environ.get('SMS_PROVIDER', 'console')
# Empty until the customer channel owner names one test recipient.
# Console, locmem, and dummy email, and SMS_PROVIDER=console, are not delivery.
TEAM_DELIVERY_TEST_RECIPIENT = os.environ.get('TEAM_DELIVERY_TEST_RECIPIENT', '')

# S3 / MinIO
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', 'http://localhost:9000')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', 'ipcas')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', 'ipcas-secret')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'ipcas-files')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
AWS_S3_USE_SSL = os.environ.get('AWS_S3_USE_SSL', 'false').lower() in ('1', 'true', 'yes')

# Economic engine
ECONOMIC_ANNUAL_FINANCING_RATE = float(os.environ.get('ECONOMIC_ANNUAL_FINANCING_RATE', '0.28'))

# RabbitMQ
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://ipcas:ipcas@localhost:5672/')

# Audit: publish to RabbitMQ when true; sync fallback on publish failure
AUDIT_LOG_ASYNC = os.environ.get('AUDIT_LOG_ASYNC', 'true').lower() in ('1', 'true', 'yes')

# MSP native MPP conversion (MPXJ); wall-clock bound for untrusted uploads
MPP_CONVERT_TIMEOUT_SECONDS = int(os.environ.get('MPP_CONVERT_TIMEOUT_SECONDS', '60'))


def _import_int(name: str, default: str) -> int:
    raw = os.environ.get(name, default)
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise ImproperlyConfigured(f'{name} must be an integer') from exc


def _import_bool(name: str, default: str = 'false') -> bool:
    return os.environ.get(name, default).lower() in ('1', 'true', 'yes')


# Initial isolated acceptance profile. These are safety bounds, not a customer SLA.
IMPORT_PREPARE_TIMEOUT_SECONDS = _import_int('IMPORT_PREPARE_TIMEOUT_SECONDS', '75')
IMPORT_PREPARE_GRACE_SECONDS = _import_int('IMPORT_PREPARE_GRACE_SECONDS', '2')
IMPORT_HELPER_MEMORY_BYTES = _import_int('IMPORT_HELPER_MEMORY_BYTES', str(1024 ** 3))
IMPORT_HELPER_SWAP_BYTES = _import_int('IMPORT_HELPER_SWAP_BYTES', '0')
IMPORT_HELPER_PIDS = _import_int('IMPORT_HELPER_PIDS', '32')
IMPORT_HELPER_HEAP_BYTES = _import_int('IMPORT_HELPER_HEAP_BYTES', str(512 * 1024 * 1024))
IMPORT_SCRATCH_QUOTA_BYTES = _import_int('IMPORT_SCRATCH_QUOTA_BYTES', str(256 * 1024 * 1024))
IMPORT_OUTPUT_LIMIT_BYTES = _import_int('IMPORT_OUTPUT_LIMIT_BYTES', str(128 * 1024 * 1024))
IMPORT_DIAGNOSTIC_LIMIT_BYTES = _import_int('IMPORT_DIAGNOSTIC_LIMIT_BYTES', str(64 * 1024))
IMPORT_PREPARATION_SLOTS = _import_int('IMPORT_PREPARATION_SLOTS', '1')
IMPORT_EXECUTION_SOFT_SECONDS = _import_int('IMPORT_EXECUTION_SOFT_SECONDS', '170')
IMPORT_EXECUTION_HARD_SECONDS = _import_int('IMPORT_EXECUTION_HARD_SECONDS', '180')
IMPORT_APPLY_STATEMENT_SECONDS = _import_int('IMPORT_APPLY_STATEMENT_SECONDS', '90')
IMPORT_LOCK_WAIT_SECONDS = _import_int('IMPORT_LOCK_WAIT_SECONDS', '3')
IMPORT_DISPATCH_DEADLINE_SECONDS = _import_int('IMPORT_DISPATCH_DEADLINE_SECONDS', '300')
IMPORT_PUBLISH_BUDGET_SECONDS = _import_int('IMPORT_PUBLISH_BUDGET_SECONDS', '5')
IMPORT_RECONCILE_INTERVAL_SECONDS = _import_int('IMPORT_RECONCILE_INTERVAL_SECONDS', '60')
IMPORT_MAINTENANCE_BATCH_SIZE = _import_int('IMPORT_MAINTENANCE_BATCH_SIZE', '100')
IMPORT_PURGE_INTERVAL_SECONDS = _import_int('IMPORT_PURGE_INTERVAL_SECONDS', '3600')
IMPORT_RETENTION_HOURS = _import_int('IMPORT_RETENTION_HOURS', '168')
IMPORT_REDIS_VISIBILITY_SECONDS = _import_int('IMPORT_REDIS_VISIBILITY_SECONDS', '600')
IMPORT_MAINTENANCE_ITEM_SECONDS = _import_int('IMPORT_MAINTENANCE_ITEM_SECONDS', '10')
IMPORT_MAINTENANCE_GAP_SECONDS = _import_int('IMPORT_MAINTENANCE_GAP_SECONDS', '0')
IMPORT_UPLOAD_LIMIT_BYTES = _import_int('IMPORT_UPLOAD_LIMIT_BYTES', str(50 * 1024 * 1024))
IMPORT_CONTAINMENT_REQUIRED = _import_bool('IMPORT_CONTAINMENT_REQUIRED', 'false')
IMPORT_PREPARE_INLINE = _import_bool('IMPORT_PREPARE_INLINE', 'false')
IMPORT_ADMISSION_REQUIRES_CATCHUP = _import_bool('IMPORT_ADMISSION_REQUIRES_CATCHUP', 'false')
IMPORT_CGROUP_ROOT = os.environ.get('IMPORT_CGROUP_ROOT', '')
IMPORT_SCRATCH_ROOT = os.environ.get('IMPORT_SCRATCH_ROOT', str(BASE_DIR / 'var' / 'import-scratch'))
IMPORT_EXECUTION_QUEUE = os.environ.get('IMPORT_EXECUTION_QUEUE', 'celery')
IMPORT_MAINTENANCE_QUEUE = os.environ.get('IMPORT_MAINTENANCE_QUEUE', 'celery')
IMPORT_PROFILE_ID = 'a7-p5-v1'

_import_profile_errors = []
if IMPORT_PREPARE_TIMEOUT_SECONDS < MPP_CONVERT_TIMEOUT_SECONDS:
    _import_profile_errors.append('preparation budget must cover conversion')
if IMPORT_PREPARE_GRACE_SECONDS < 0 or IMPORT_PREPARE_GRACE_SECONDS >= IMPORT_PREPARE_TIMEOUT_SECONDS:
    _import_profile_errors.append('kill grace must fit inside preparation')
if IMPORT_EXECUTION_SOFT_SECONDS >= IMPORT_EXECUTION_HARD_SECONDS:
    _import_profile_errors.append('execution soft limit must be below the hard limit')
if IMPORT_EXECUTION_HARD_SECONDS < IMPORT_PREPARE_TIMEOUT_SECONDS:
    _import_profile_errors.append('execution budget must cover preparation')
if IMPORT_APPLY_STATEMENT_SECONDS <= 0 or IMPORT_APPLY_STATEMENT_SECONDS > 90:
    _import_profile_errors.append('application statement budget must be 1..90 seconds')
if IMPORT_LOCK_WAIT_SECONDS <= 0 or IMPORT_LOCK_WAIT_SECONDS > 3:
    _import_profile_errors.append('lock wait must be 1..3 seconds')
if IMPORT_MAINTENANCE_BATCH_SIZE < 1 or IMPORT_MAINTENANCE_BATCH_SIZE > 100:
    _import_profile_errors.append('maintenance batch size must be 1..100')
if IMPORT_MAINTENANCE_ITEM_SECONDS <= 0:
    _import_profile_errors.append('per-item maintenance budget must be positive')
if IMPORT_MAINTENANCE_GAP_SECONDS < 0 or IMPORT_MAINTENANCE_GAP_SECONDS > 1:
    _import_profile_errors.append('inter-batch delay must be 0..1 seconds')
if IMPORT_RETENTION_HOURS != 168:
    _import_profile_errors.append('original retention is fixed at 168 hours')
if IMPORT_REDIS_VISIBILITY_SECONDS < IMPORT_EXECUTION_HARD_SECONDS:
    _import_profile_errors.append('Redis visibility must exceed the execution hard limit')
if IMPORT_HELPER_MEMORY_BYTES < IMPORT_HELPER_HEAP_BYTES:
    _import_profile_errors.append('helper memory must cover the JVM heap')
if IMPORT_PREPARATION_SLOTS < 1:
    _import_profile_errors.append('at least one preparation slot is required')
if _import_profile_errors:
    raise ImproperlyConfigured('Import profile is inconsistent: ' + '; '.join(_import_profile_errors))

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get(
    'CELERY_RESULT_BACKEND',
    'django-db',
)
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_TASK_ALWAYS_EAGER', 'false').lower() in ('1', 'true', 'yes')
CELERY_RESULT_EXTENDED = True
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': IMPORT_REDIS_VISIBILITY_SECONDS}
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {'visibility_timeout': IMPORT_REDIS_VISIBILITY_SECONDS}
CELERY_TASK_ROUTES = {
    'schedule.tasks.run_msp_import_task': {'queue': IMPORT_EXECUTION_QUEUE},
    'schedule.tasks.run_p6_import_task': {'queue': IMPORT_EXECUTION_QUEUE},
    'schedule.tasks.reconcile_import_jobs': {'queue': IMPORT_MAINTENANCE_QUEUE},
    'schedule.tasks.purge_import_originals': {'queue': IMPORT_MAINTENANCE_QUEUE},
    'schedule.tasks.reconcile_import_scratch': {'queue': IMPORT_MAINTENANCE_QUEUE},
}

from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    'monitor-ipc-delays': {
        'task': 'contracts.tasks.monitor_ipc_payment_delays',
        'schedule': crontab(hour=8, minute=0),
    },
    'monitor-guarantee-expiry': {
        'task': 'contracts.tasks.monitor_guarantee_expiry',
        'schedule': crontab(hour=7, minute=30),
    },
    'monitor-correspondence-due': {
        'task': 'documents.tasks.monitor_correspondence_due',
        'schedule': crontab(hour=8, minute=10),
    },
    'monitor-cash-gaps': {
        'task': 'alerts.tasks.monitor_cash_gaps',
        'schedule': crontab(hour=8, minute=15),
    },
    'run-daily-alert-checks': {
        'task': 'alerts.tasks.run_daily_alert_checks',
        'schedule': crontab(hour=23, minute=0),
    },
    'generate-daily-economic-snapshots': {
        'task': 'economic.tasks.generate_daily_snapshots',
        'schedule': crontab(hour=1, minute=0),
    },
    'reconcile-import-jobs': {
        'task': 'schedule.tasks.reconcile_import_jobs',
        'schedule': float(IMPORT_RECONCILE_INTERVAL_SECONDS),
    },
    'reconcile-import-scratch': {
        'task': 'schedule.tasks.reconcile_import_scratch',
        'schedule': float(IMPORT_RECONCILE_INTERVAL_SECONDS),
    },
    'purge-import-originals': {
        'task': 'schedule.tasks.purge_import_originals',
        'schedule': crontab(minute=0),
    },
}

# Redis cache (rate limiting + API response caching)
_redis_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': _redis_url,
    }
}

# django-ratelimit
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_ENABLE = True
RATELIMIT_VIEW = 'authentication.ratelimit_handlers.ratelimit_view'
