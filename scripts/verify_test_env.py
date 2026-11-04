#!/usr/bin/env python3
"""Health-check the isolated R.0.03 test environment and role account logins.

Usage (from repo root, with .env.test-env loaded or --env-file):

  apps/api/.venv/bin/python scripts/verify_test_env.py
  apps/api/.venv/bin/python scripts/verify_test_env.py --skip-login
  apps/api/.venv/bin/python scripts/verify_test_env.py --api-base http://localhost:8001
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_CORE = ROOT / 'apps' / 'api' / 'core'


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _ok(msg: str) -> None:
    print(f'OK  {msg}')


def _fail(msg: str) -> None:
    print(f'FAIL {msg}', file=sys.stderr)


def check_reference_fixtures() -> bool:
    # Keep paths aligned with permissions.test_accounts.REFERENCE_FIXTURES /
    # scripts/verify_reference_fixtures.py (no Django import before setup).
    fixtures = (
        ('plan.mpp', 'real-data/plan.mpp'),
        (
            'shiraz_daily_report',
            'real-data/گزارش روزانه پروژه 2000 واحدی کمیل آباد شیراز.xlsx',
        ),
    )
    ok = True
    for label, rel in fixtures:
        path = ROOT / rel
        if path.is_file() and path.stat().st_size > 0:
            _ok(f'reference fixture {label}: {rel} ({path.stat().st_size} bytes)')
        else:
            _fail(f'reference fixture missing or empty: {rel}')
            ok = False
    return ok


def check_postgres() -> bool:
    import dj_database_url
    import psycopg

    url = os.environ.get('DATABASE_URL', '')
    if not url:
        _fail('DATABASE_URL not set')
        return False
    cfg = dj_database_url.parse(url)
    conn = psycopg.connect(
        dbname=cfg['NAME'],
        user=cfg['USER'],
        password=cfg['PASSWORD'],
        host=cfg['HOST'],
        port=cfg['PORT'],
        connect_timeout=5,
    )
    with conn.cursor() as cur:
        cur.execute('SELECT 1')
        cur.fetchone()
    conn.close()
    _ok(f'postgres {cfg["HOST"]}:{cfg["PORT"]}/{cfg["NAME"]}')
    return True


def check_redis() -> bool:
    import redis

    url = os.environ.get('REDIS_URL') or os.environ.get('CELERY_BROKER_URL', '')
    if not url:
        _fail('REDIS_URL / CELERY_BROKER_URL not set')
        return False
    client = redis.from_url(url, socket_connect_timeout=5)
    assert client.ping() is True
    _ok(f'redis {url}')
    return True


def check_rabbitmq() -> bool:
    import pika

    url = os.environ.get('RABBITMQ_URL', '')
    if not url:
        _fail('RABBITMQ_URL not set')
        return False
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    conn = pika.BlockingConnection(params)
    conn.close()
    _ok(f'rabbitmq {url}')
    return True


def check_minio() -> bool:
    import boto3
    from botocore.client import Config

    endpoint = os.environ.get('AWS_S3_ENDPOINT_URL', '')
    bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME', 'ipcas-test-files')
    key = os.environ.get('AWS_ACCESS_KEY_ID', 'ipcas')
    secret = os.environ.get('AWS_SECRET_ACCESS_KEY', 'ipcas-secret')
    if not endpoint:
        _fail('AWS_S3_ENDPOINT_URL not set')
        return False

    client = boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=key,
        aws_secret_access_key=secret,
        config=Config(signature_version='s3v4'),
        region_name=os.environ.get('AWS_S3_REGION_NAME', 'us-east-1'),
    )
    # Live health via list; ensure bucket exists (create if missing).
    existing = {b['Name'] for b in client.list_buckets().get('Buckets', [])}
    if bucket not in existing:
        client.create_bucket(Bucket=bucket)
        _ok(f'minio created bucket {bucket} at {endpoint}')
    else:
        _ok(f'minio bucket {bucket} at {endpoint}')
    return True


def check_blueprint_schema() -> bool:
    from django.core.management import call_command
    from io import StringIO

    out = StringIO()
    err = StringIO()
    try:
        call_command('verify_blueprint_schema', stdout=out, stderr=err)
    except SystemExit as exc:
        if exc.code not in (0, None):
            _fail(f'verify_blueprint_schema exit={exc.code}: {err.getvalue()}')
            return False
    _ok('verify_blueprint_schema')
    return True


def seed_roles() -> bool:
    from business_meta.management.commands.seed_test_roles import run_seed_test_roles

    result = run_seed_test_roles(with_demo=True)
    _ok(f"seed_test_roles users={len(result['users'])} projects={result['projects']}")
    return True


def login_all_roles(api_base: str) -> bool:
    """POST /api/auth/login/ for every reference account; assert JWT + role perms."""
    from django.contrib.auth import get_user_model
    from master_data.models import ProjectMember
    from permissions.constants import DEFAULT_ROLE_PERMISSIONS
    from permissions.services import get_role_permission_codenames
    from permissions.test_accounts import DEV_PASSWORD, TEST_ROLE_ACCOUNTS

    User = get_user_model()
    ok = True
    base = api_base.rstrip('/')

    for account in TEST_ROLE_ACCOUNTS:
        payload = json.dumps(
            {'phone_number': account.mobile, 'password': DEV_PASSWORD}
        ).encode()
        # Keep the real 10/min login limit; one wait covers the 11-account catalog.
        body = None
        for attempt in range(2):
            req = urllib.request.Request(
                f'{base}/api/auth/login/',
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    body = json.loads(resp.read().decode())
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode(errors='replace')
                if exc.code == 429 and attempt == 0:
                    print(
                        'INFO login rate limit reached; waiting 61s for next window',
                        flush=True,
                    )
                    time.sleep(61)
                    continue
                _fail(f'login {account.key} ({account.mobile}): HTTP {exc.code} {detail}')
                ok = False
                break
            except Exception as exc:  # noqa: BLE001 — report and continue
                _fail(f'login {account.key} ({account.mobile}): {exc}')
                ok = False
                break
        if body is None:
            continue

        access = body.get('access')
        if not access or not isinstance(access, str):
            _fail(f'login {account.key}: missing access token')
            ok = False
            continue

        user = User.objects.filter(mobile=account.mobile).first()
        if user is None:
            _fail(f'login {account.key}: user row missing after seed')
            ok = False
            continue

        if account.project_role:
            expected = set(DEFAULT_ROLE_PERMISSIONS[account.project_role])
            members = ProjectMember.objects.filter(user=user).prefetch_related(
                'member_roles__role__role_permissions'
            )
            if not members.exists():
                _fail(f'login {account.key}: no project memberships')
                ok = False
                continue
            for member in members:
                actual = get_role_permission_codenames(member)
                if actual != expected:
                    _fail(
                        f'login {account.key} project={member.project.project_code}: '
                        f'permissions mismatch '
                        f'missing={sorted(expected - actual)} '
                        f'extra={sorted(actual - expected)}'
                    )
                    ok = False
                    break
            else:
                _ok(
                    f'login {account.key} ({account.mobile}) '
                    f'token+role={account.project_role} perms={len(expected)}'
                )
        else:
            _ok(f'login {account.key} ({account.mobile}) token issued')

    return ok


def login_all_roles_django() -> bool:
    """Authenticate via LoginService without a live HTTP server (local/CI)."""
    from authentication.services import LoginService
    from django.contrib.auth import get_user_model
    from master_data.models import ProjectMember
    from permissions.constants import DEFAULT_ROLE_PERMISSIONS
    from permissions.services import get_role_permission_codenames
    from permissions.test_accounts import DEV_PASSWORD, TEST_ROLE_ACCOUNTS

    User = get_user_model()
    service = LoginService()
    ok = True

    for account in TEST_ROLE_ACCOUNTS:
        try:
            user, tokens = service.authenticate_and_issue_tokens(
                account.mobile, DEV_PASSWORD
            )
        except Exception as exc:  # noqa: BLE001
            _fail(f'django-login {account.key}: {exc}')
            ok = False
            continue

        if not tokens.get('access'):
            _fail(f'django-login {account.key}: missing access token')
            ok = False
            continue

        if account.is_superuser and not user.is_superuser:
            _fail(f'django-login {account.key}: expected superuser')
            ok = False
            continue

        if account.project_role:
            expected = set(DEFAULT_ROLE_PERMISSIONS[account.project_role])
            members = (
                ProjectMember.objects.filter(user=user)
                .select_related('project')
                .prefetch_related('member_roles__role__role_permissions')
            )
            for member in members:
                actual = get_role_permission_codenames(member)
                if actual != expected:
                    _fail(
                        f'django-login {account.key} '
                        f'project={member.project.project_code}: perm mismatch'
                    )
                    ok = False
                    break
            else:
                _ok(
                    f'django-login {account.key} ({account.mobile}) '
                    f'role={account.project_role}'
                )
        else:
            _ok(f'django-login {account.key} token ok')

        # Ensure catalog account still exists under expected mobile.
        assert User.objects.filter(mobile=account.mobile, pk=user.pk).exists()

    return ok


def setup_django() -> None:
    sys.path.insert(0, str(API_CORE))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django

    django.setup()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--env-file',
        default=str(ROOT / '.env.test-env'),
        help='Env file to load (defaults do not override existing env)',
    )
    parser.add_argument(
        '--api-base',
        default=os.environ.get('TEST_ENV_API_BASE', ''),
        help='If set, also POST /api/auth/login/ against this base URL',
    )
    parser.add_argument(
        '--skip-seed',
        action='store_true',
        help='Skip seed_test_roles (assume already seeded)',
    )
    parser.add_argument(
        '--skip-login',
        action='store_true',
        help='Skip authentication checks',
    )
    parser.add_argument(
        '--infra-only',
        action='store_true',
        help='Only ping Postgres/Redis/RabbitMQ/MinIO and fixtures',
    )
    parser.add_argument(
        '--skip-minio',
        action='store_true',
        help='Skip MinIO/S3 check (registry may deny minio/minio pulls in some envs)',
    )
    args = parser.parse_args()

    _load_env_file(Path(args.env_file))

    failures = 0

    if not check_reference_fixtures():
        failures += 1

    checkers = [check_postgres, check_redis, check_rabbitmq]
    if not args.skip_minio:
        checkers.append(check_minio)
    for checker in checkers:
        try:
            if not checker():
                failures += 1
        except Exception as exc:  # noqa: BLE001
            _fail(f'{checker.__name__}: {exc}')
            failures += 1

    if args.infra_only:
        return 1 if failures else 0

    setup_django()

    try:
        if not check_blueprint_schema():
            failures += 1
    except Exception as exc:  # noqa: BLE001
        _fail(f'blueprint: {exc}')
        failures += 1

    if not args.skip_seed:
        try:
            if not seed_roles():
                failures += 1
        except Exception as exc:  # noqa: BLE001
            _fail(f'seed: {exc}')
            failures += 1

    if not args.skip_login:
        try:
            if not login_all_roles_django():
                failures += 1
        except Exception as exc:  # noqa: BLE001
            _fail(f'django-login: {exc}')
            failures += 1

        if args.api_base:
            try:
                if not login_all_roles(args.api_base):
                    failures += 1
            except Exception as exc:  # noqa: BLE001
                _fail(f'http-login: {exc}')
                failures += 1

    if failures:
        print(f'\nVerification failed with {failures} check group(s).', file=sys.stderr)
        return 1
    print('\nAll test-env checks passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
