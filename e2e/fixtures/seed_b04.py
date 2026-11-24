"""Seed B04 in an empty isolated database via manage.py shell."""
import json
import os
from datetime import date, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from django.utils import timezone

from field_reports.models import DailyReport, DailyReportActivity, ReportStatus
from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission
from projects.models import ProjectStatus, Stakeholder
from projects.services import create_project_with_creator


def seed():
    if not connection.settings_dict['NAME'].startswith('velora_b04_'):
        raise RuntimeError('Use an isolated velora_b04_ database')
    password = os.environ['B04_TEST_PASSWORD']
    user_model = get_user_model()
    users = {
        name: user_model.objects.create_user(username=f'b04-{name}', password=password)
        for name in ('author', 'approver', 'viewer-1', 'viewer-2', 'no-reports', 'other-project')
    }
    project = create_project_with_creator(
        creator=users['author'], project_code='B04-UAT', project_name='B04 reference selection',
        employer='Fixture employer', start_date='2024-01-01',
    )
    other = create_project_with_creator(
        creator=users['other-project'], project_code='B04-OTHER', project_name='B04 other project',
        employer='Fixture employer', start_date='2024-01-01',
    )
    for item in (project, other):
        item.status = ProjectStatus.ACTIVE
        item.save(update_fields=['status'])
    for name, permissions in {
        'viewer': ('view_project', 'view_reports'),
        'approver': ('view_project', 'view_reports', 'approve_reports'),
        'no-reports': ('view_project',),
    }.items():
        role = Role.objects.create(role_name=f'b04-{name}')
        for permission in permissions:
            RolePermission.objects.create(role=role, permission_codename=permission)
        names = ('viewer-1', 'viewer-2') if name == 'viewer' else (name,)
        for actor in names:
            member = ProjectMember.objects.create(project=project, user=users[actor], status='active')
            ProjectMemberRole.objects.create(member=member, role=role)

    contractor = Stakeholder.objects.create(project=project, name='آرماتوربند الف', role='contractor', created_by=users['author'])
    alternative = Stakeholder.objects.create(project=project, name='Contractor B', role='contractor', created_by=users['author'])

    def report(day, **overrides):
        fields = {'status': ReportStatus.APPROVED, **overrides}
        return DailyReport.objects.create(project=project, report_date=day, created_by=users['author'], **fields)

    def activity(parent, number, company=contractor, **overrides):
        fields = {
            'source_discipline': 'CIVIL', 'block': 'Block 1', 'shift': 'shift_1',
            'activity_description': f'B04 row {number:02}', 'quantity': Decimal('1.25'),
            'unit': 'm²', 'headcount': 1, **overrides,
        }
        return DailyReportActivity.objects.create(report=parent, contractor_ref=company, **fields)

    start = date(2027, 5, 22)
    daily_ids = []
    for i in range(21):
        parent = report(start + timedelta(days=i))
        daily_ids.append(str(parent.pk))
        activity(parent, i)
        if i == 0:
            activity(parent, i)
    split = report(start + timedelta(days=21))
    activity(split, 90, block='Block 2')
    activity(split, 91, company=alternative)
    excluded = report(start + timedelta(days=22))
    activity(excluded, 92, is_deleted=True)

    activity_day = date(2027, 4, 1)
    approved = report(activity_day)
    for i in range(51):
        overrides = {
            0: {'quantity': Decimal(0)},
            1: {'quantity': None},
            2: {'quantity': Decimal('555'), 'quantity_measured': False},
            3: {'quantity': Decimal('777'), 'unit': None},
            4: {'quantity': None, 'unit': 'kg'},
        }.get(i, {'quantity': Decimal('2.5'), 'unit': 'm³'} if i >= 41 else {})
        activity(approved, i, parcel='P1' if i < 25 else 'P2', **overrides)
    activity(approved, 93, company=alternative, parcel='P1')
    activity(approved, 94, is_deleted=True, parcel='P1')
    historical = report(activity_day, is_current=False, lineage_id=approved.lineage_id)
    activity(historical, 95, parcel='P1')
    deleted = report(activity_day, is_deleted=True)
    activity(deleted, 96, parcel='P1')

    today = timezone.localdate(timezone=ZoneInfo('Asia/Tehran'))
    month_end = today.replace(day=1) - timedelta(days=1)
    month_start = month_end.replace(day=1)
    timing_report = report(month_start, status=ReportStatus.SUBMITTED, submitted_by=users['author'], prepared_by=users['author'])
    for i in range(51, 102):
        activity(timing_report, i, parcel='P1')
    return {
        'B04_TEST_PROJECT': str(project.pk),
        'B04_TEST_CONTRACTOR': str(contractor.pk),
        'B04_TEST_MATCHED_REPORTS': ','.join(reversed(daily_ids)),
        'B04_TEST_TIMING_REPORT': str(timing_report.pk),
        'B04_TEST_TIMING_FROM': month_start.isoformat(),
        'B04_TEST_TIMING_TO': month_end.isoformat(),
    }


with transaction.atomic():
    print(json.dumps(seed()))
