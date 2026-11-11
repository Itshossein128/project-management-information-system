"""Extend the isolated A6 fixture with one active member per default project role."""
import contextlib
import io
import json
import runpy
from pathlib import Path

captured = io.StringIO()
with contextlib.redirect_stdout(captured):
    runpy.run_path(str(Path(__file__).with_name('seed.py')), run_name='__main__')
fixture = json.loads(captured.getvalue())

from django.contrib.auth import get_user_model
from django.db import transaction
from authentication.utils import get_tokens_for_user
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from field_reports.models import DailyReport

with transaction.atomic():
    fixture['role_review'] = {}
    for index, (role_name, codenames) in enumerate(DEFAULT_ROLE_PERMISSIONS.items(), 30):
        role, _ = Role.objects.get_or_create(role_name=role_name)
        for codename in codenames:
            RolePermission.objects.get_or_create(role=role, permission_codename=codename)
        user = get_user_model().objects.create_user(
            username=f"a604_{fixture['run']}_{role_name}",
            mobile=f"+199{int(fixture['run'], 16):010d}{index:02d}",
            full_name=f"A604 {role_name}", password=fixture['password'],
        )
        member = ProjectMember.objects.create(project_id=fixture['project_a'], user=user, status='active')
        ProjectMemberRole.objects.create(member=member, role=role)
        fixture['users'][role_name] = {'id': str(user.pk), 'username': user.username, 'mobile': user.mobile, 'name': user.full_name}
        fixture['tokens'][role_name] = get_tokens_for_user(user)['access']
        fixture['role_review'][role_name] = str(member.pk)

    report = DailyReport.objects.create(
        project_id=fixture['project_a'], report_date='2026-11-11',
        prepared_by_id=fixture['users']['manager']['id'],
        created_by_id=fixture['users']['manager']['id'],
        updated_by_id=fixture['users']['manager']['id'], status='draft',
    )
    fixture['daily_report'] = str(report.pk)

print(json.dumps(fixture))
