#!/usr/bin/env python3
"""Strict R.0 live HTTP/DB/RabbitMQ smoke for a seeded isolated test database.

Uses the same environment as the API. Creates a disposable project and removes
it in finally; never seeds or resets existing accounts. No required check skips.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from uuid import uuid4

from verify_test_env import _load_env_file, check_blueprint_schema, setup_django

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Smoke:
    def __init__(self, api_base):
        self.base = api_base.rstrip('/')
        self.passed = 0
        self.failed = 0
        self.tokens = {}

    def check(self, name, action):
        try:
            action()
        except Exception as exc:
            self.failed += 1
            # Never print HTTP bodies, JWTs, environment values, or broker URLs.
            print(f'FAIL {name}: {type(exc).__name__}: {exc}', flush=True)
        else:
            self.passed += 1
            print(f'PASS {name}', flush=True)

    def request(self, path, *, token=None, data=None, expected=200, raw=False):
        headers = {'Accept': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        if data is not None:
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(self.base + path, headers=headers,
                                     data=None if data is None else json.dumps(data).encode())
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status, body = response.status, response.read()
        except urllib.error.HTTPError as exc:
            status, body = exc.code, exc.read()
        require(status == expected, f'{req.get_method()} {path}: expected HTTP {expected}, got {status}')
        return body if raw or expected != 200 else json.loads(body)

    def login(self, account):
        from django.contrib.auth import get_user_model
        from permissions.test_accounts import DEV_PASSWORD
        from rest_framework_simplejwt.tokens import AccessToken

        # The real API limits logins to 10/minute per IP. Keep that protection;
        # wait for a fresh window once if the 11-account run hits it.
        payload = {'phone_number': account.mobile, 'password': DEV_PASSWORD}
        try:
            body = self.request('/api/auth/login/', data=payload)
        except RuntimeError as exc:
            if 'got 429' not in str(exc):
                raise
            print('INFO login rate limit reached; waiting 61s for next window', flush=True)
            time.sleep(61)
            body = self.request('/api/auth/login/', data=payload)
        require(isinstance(body.get('access'), str) and bool(body['access']), 'missing JWT access token')
        token = AccessToken(body['access'])  # signature, expiry, and token_type
        user = get_user_model().objects.get(mobile=account.mobile)
        require(str(token['user_id']) == str(user.pk), 'JWT belongs to a different user/database')
        self.tokens[account.key] = body['access']

    def projects(self, account):
        from django.contrib.auth import get_user_model
        from master_data.models import MemberStatus, ProjectMember
        from projects.models import Project

        user = get_user_model().objects.get(mobile=account.mobile)
        if account.is_superuser:
            expected = {str(pk) for pk in Project.objects.values_list('pk', flat=True)}
        else:
            expected = {str(pk) for pk in ProjectMember.objects.filter(
                user=user, status=MemberStatus.ACTIVE).values_list('project_id', flat=True)}
        require(bool(expected), 'reference account has no projects')
        found = []
        path = '/api/v1/projects/?page_size=100'
        visited = set()
        while path:
            require(path not in visited, 'pagination loop')
            visited.add(path)
            body = self.request(path, token=self.tokens[account.key])
            rows = body if isinstance(body, list) else body['results']
            require(isinstance(rows, list), 'projects response is not a list')
            found.extend(str(row['id']) for row in rows)
            next_url = None if isinstance(body, list) else body.get('next')
            path = None
            if next_url:
                target = urllib.parse.urlsplit(urllib.parse.urljoin(self.base, next_url))
                require((target.scheme, target.netloc) == (
                    urllib.parse.urlsplit(self.base).scheme, urllib.parse.urlsplit(self.base).netloc),
                    'pagination points outside the API')
                require(target.path == '/api/v1/projects/', 'unexpected pagination endpoint')
                path = target.path + ('?' + target.query if target.query else '')
        require(set(found) == expected and len(found) == len(expected),
                'project listing differs from active membership scope')

    def sync(self, project):
        path = f'/api/v1/projects/{project.pk}/daily-reports/sync-batch/'
        local_id = f'r0-{uuid4().hex}'
        body = self.request(path, token=self.tokens['site_supervisor'], data=[{
            'local_id': local_id, 'report_date': date.today().isoformat(), 'site_status': 'active',
        }])
        require(body['summary'] == {'created': 1, 'merged': 0, 'skipped': 0, 'conflicts': 0, 'errors': 0},
                'sync-batch returned errors, conflicts, or did not create a report')
        require(len(body['results']) == 1 and body['results'][0]['status'] == 'created',
                'sync-batch result is not created')
        from field_reports.models import DailyReport
        report = DailyReport.objects.get(pk=body['results'][0]['server_id'], project=project)
        require(report.local_id == local_id and report.synced_from_offline, 'sync result was not persisted')

    def progress(self, project):
        body = self.request(f'/api/v1/projects/{project.pk}/progress/s-curve/?interval=daily',
                            token=self.tokens['project_controls'])
        require(isinstance(body.get('results'), list) and bool(body['results']), 'missing S-curve series')
        point = body['results'][-1]
        require(point.get('planned_progress') == 60 and point.get('actual_progress') == 40
                and point.get('variance') == -20, 'S-curve differs from seeded 60% planned / 40% actual')

    def costs(self, project):
        body = self.request(f'/api/v1/projects/{project.pk}/costs/summary/', token=self.tokens['finance_manager'])
        expected = {'total_budget': 1000, 'total_actual': 250, 'total_committed': 0,
                    'budget_consumption_pct': 25}
        require(all(isinstance(body.get(key), (int, float)) and body[key] == value
                    for key, value in expected.items()), 'cost totals differ from seeded budget/actual')
        require(bool(body.get('currency')), 'missing cost currency')

    def summary(self):
        total = self.passed + self.failed
        print(f'SMOKE {self.passed}/{total} passed; {self.failed} failed'
              + (' (100% pass)' if total and not self.failed else ''), flush=True)
        return 1 if self.failed or not total else 0


def rabbitmq_smoke():
    import pika
    from events.publisher import get_rabbitmq_url
    from events.topology import TOPIC_EXCHANGE, TOPIC_QUEUE_MAP

    params = pika.URLParameters(get_rabbitmq_url())
    params.socket_timeout = params.blocked_connection_timeout = 5
    params.connection_attempts = 1
    connection = pika.BlockingConnection(params)
    try:
        channel = connection.channel()
        # Verify provisioned production topology; do not silently repair it.
        channel.exchange_declare(exchange=TOPIC_EXCHANGE, passive=True)
        for queue in TOPIC_QUEUE_MAP.values():
            channel.queue_declare(queue=queue, passive=True)
        queue = channel.queue_declare(queue='', exclusive=True, auto_delete=True).method.queue
        routing_key = f'r0.smoke.{uuid4().hex}'
        channel.queue_bind(queue=queue, exchange=TOPIC_EXCHANGE, routing_key=routing_key)
        channel.confirm_delivery()
        payload = json.dumps({'rehearsal': routing_key}).encode()
        channel.basic_publish(exchange=TOPIC_EXCHANGE, routing_key=routing_key,
                              body=payload, mandatory=True)
        for method, _properties, received in channel.consume(queue, inactivity_timeout=5):
            require(method is not None and received == payload, 'RabbitMQ event did not round-trip')
            channel.basic_ack(method.delivery_tag)
            break
        channel.cancel()
    finally:
        connection.close()


def seed_smoke_data(project):
    from django.contrib.auth import get_user_model
    from cost_control.models import ActualCost, Budget, CostCategory
    from cost_control.services.actual_cost_service import approve_actual_cost
    from permissions.test_accounts import TEST_ROLE_ACCOUNTS_BY_KEY
    from projects.models import Activity
    from schedule.models import ActivityProgress
    from wbs.services import create_wbs_node

    creator = get_user_model().objects.get(mobile=TEST_ROLE_ACCOUNTS_BY_KEY['project_manager'].mobile)
    approver = get_user_model().objects.get(mobile=TEST_ROLE_ACCOUNTS_BY_KEY['finance_manager'].mobile)
    wbs, _warnings = create_wbs_node(project_id=project.pk, wbs_code='1', wbs_name='Smoke', created_by=creator)
    activity = Activity.objects.create(project=project, wbs=wbs, activity_code='SMOKE',
                                       activity_name='Smoke', weight=1, created_by=creator, updated_by=creator)
    ActivityProgress.objects.create(activity=activity, report_date=date.today(),
                                    planned_progress='0.600', actual_progress='0.400')
    Budget.objects.create(project=project, wbs=wbs, cost_category=CostCategory.LABOR,
                           budget_amount=1000, created_by=creator, updated_by=creator)
    actual = ActualCost.objects.create(project=project, wbs=wbs, cost_category=CostCategory.LABOR,
                                       cost_date=date.today(), amount=250, created_by=creator, updated_by=creator)
    approve_actual_cost(actual, approver)


def cleanup_project(project):
    from field_reports.models import DailyReport
    from projects.models import Project

    pk = project.pk
    project.delete()
    require(not Project.objects.filter(pk=pk).exists()
            and not DailyReport.all_objects.filter(project_id=pk).exists(), 'smoke fixture cleanup incomplete')


def run(api_base):
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from business_meta.management.commands.seed_test_roles import assign_project_role
    from master_data.models import Role
    from permissions.test_accounts import TEST_ROLE_ACCOUNTS
    from projects.models import Project

    # This runner writes a report/project. Its defaults must never target real data.
    require(re.search(r'(^|_)test(_|$)', str(settings.DATABASES['default']['NAME']).lower()),
            'smoke writes require an isolated database named test_* or *_test[_*]')
    smoke = Smoke(api_base)
    smoke.check('API health', lambda: require(
        smoke.request('/api/health/').get('status') == 'ok', 'health is not ok'))
    smoke.check('OpenAPI schema HTTP 200', lambda: require(
        bool(smoke.request('/api/schema/', raw=True)), 'empty schema'))
    smoke.check('blueprint database schema', lambda: require(check_blueprint_schema(), 'schema verification failed'))
    for account in TEST_ROLE_ACCOUNTS:
        smoke.check(f'JWT login {account.key}', lambda account=account: smoke.login(account))
    if len(smoke.tokens) != 11:
        smoke.check('all 11 roles authenticated (core smoke cannot proceed)', lambda: require(False, 'missing role tokens'))
        return smoke.summary()

    project = None
    try:
        project = Project.objects.create(project_code=f'r0_smoke_{uuid4().hex[:12]}',
                                         project_name='R.0 disposable smoke project', start_date=date.today())
        for key in ('project_manager', 'site_supervisor', 'project_controls', 'finance_manager'):
            account = next(a for a in TEST_ROLE_ACCOUNTS if a.key == key)
            assign_project_role(user=get_user_model().objects.get(mobile=account.mobile), project=project,
                                role=Role.objects.get(role_name=account.project_role))
        seed_smoke_data(project)
        for account in TEST_ROLE_ACCOUNTS:
            smoke.check(f'scoped project listing {account.key}', lambda account=account: smoke.projects(account))
        smoke.check('nonmember project access denied', lambda: smoke.request(
            f'/api/v1/projects/{project.pk}/costs/summary/', token=smoke.tokens['visitor'], expected=403))
        smoke.check('daily report batch sync and persistence', lambda: smoke.sync(project))
        smoke.check('progress S-curve', lambda: smoke.progress(project))
        smoke.check('cost control summary', lambda: smoke.costs(project))
        smoke.check('RabbitMQ topology and confirmed event round-trip', rabbitmq_smoke)
    except Exception as exc:
        smoke.check('smoke fixture setup', lambda: require(False, f'{type(exc).__name__}: fixture setup failed'))
    finally:
        if project is not None:
            smoke.check('disposable project cleanup', lambda: cleanup_project(project))
    return smoke.summary()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file', default=str(ROOT / '.env.test-env'))
    parser.add_argument('--api-base', help='API origin (defaults to TEST_ENV_API_BASE or http://localhost:8001)')
    args = parser.parse_args()
    try:
        require(Path(args.env_file).is_file(), 'environment file does not exist')
        _load_env_file(Path(args.env_file))
        setup_django()
        return run(args.api_base or os.environ.get('TEST_ENV_API_BASE', 'http://localhost:8001'))
    except Exception as exc:
        print(f'FAIL smoke setup: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
