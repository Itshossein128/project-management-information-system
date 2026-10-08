import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APIRequestFactory

from business_meta.serializers import ProjectMemberCreateSerializer
from field_reports.models import DailyReport, DailyReportLabor, LaborCategory, ReportStatus
from field_reports.serializers import DailyReportLaborSerializer
from field_reports.tasks import recalculate_activity_progress
from hr.models import ApprovedLaborRate, ResourceAllocation
from master_data.models import ProjectMember, ProjectMemberRole, ProjectPosition, Role, RolePermission
from permissions.constants import PERMISSIONS
from schedule.models import ActivityProgress


@pytest.mark.django_db
def test_hr_permission_codes_exist():
    for code in ('view_hr', 'edit_hr', 'approve_hr', 'view_wage', 'edit_wage'):
        assert code in PERMISSIONS


@pytest.mark.django_db
def test_wage_omitted_without_view_wage(api_client, project, other_user, member):
    member.wage = 1500000
    member.wage_type = 'hourly'
    member.weekly_total = 100
    member.monthly_total = 400
    member.save()

    hr_only = Role.objects.create(role_name='hr_view_only_test')
    RolePermission.objects.create(role=hr_only, permission_codename='view_hr')
    RolePermission.objects.create(role=hr_only, permission_codename='view_project')
    ProjectMemberRole.objects.filter(member=member).delete()
    ProjectMemberRole.objects.create(member=member, role=hr_only)

    api_client.force_authenticate(user=other_user)
    url = reverse('authentication:user-assignments-list', kwargs={'user_id': other_user.id})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    rows = resp.data['results'] if isinstance(resp.data, dict) and 'results' in resp.data else resp.data
    row = rows[0]
    assert 'wage' not in row
    assert 'wage_type' not in row
    assert 'weekly_total' not in row
    assert 'monthly_total' not in row


@pytest.mark.django_db
def test_labor_cost_estimate_missing_rate(auth_client, project, other_user, member):
    url = reverse('labor-cost-estimate', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'approved_hours': '8.00',
            'as_of': '2026-04-10',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['warning'] == 'missing_approved_rate'
    assert resp.data['amount'] is None


@pytest.mark.django_db
def test_labor_cost_estimate_with_rate(auth_client, project, other_user, member, user):
    ApprovedLaborRate.objects.create(
        project=project,
        person=other_user,
        amount='1500000.00',
        currency='IRR',
        effective_from='2026-01-01',
        created_by=user,
    )
    url = reverse('labor-cost-estimate', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'approved_hours': '8.00',
            'as_of': '2026-04-10',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['amount'] == '12000000.00'
    assert resp.data['rate_amount'] == '1500000.00'


@pytest.mark.django_db
def test_allocation_does_not_change_activity_progress(
    auth_client, project, other_user, member, activity, user
):
    before = ActivityProgress.objects.filter(activity=activity).count()
    url = reverse('resource-allocation-list', kwargs={'project_pk': project.id})
    resp = auth_client.post(
        url,
        {
            'person_id': str(other_user.id),
            'activity_id': str(activity.id),
            'start_date': '2026-04-01',
            'end_date': '2026-04-30',
            'role': 'labor',
            'capacity_percent': '100.00',
        },
        format='json',
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert ResourceAllocation.objects.filter(activity=activity).exists()
    after = ActivityProgress.objects.filter(activity=activity).count()
    assert after == before


@pytest.mark.django_db
def test_member_create_rejects_wage_without_edit_wage(api_client, project, other_user, member):
    position = ProjectPosition.objects.create(project=project, position_name='Tech')
    factory = APIRequestFactory()
    request = factory.post('/')
    request.user = other_user
    serializer = ProjectMemberCreateSerializer(
        data={
            'phone_number': '+989121111122',
            'full_name': 'No Wage User',
            'job_position': position.id,
            'wage': '999',
            'wage_type': 'hourly',
        },
        context={'request': request, 'project_pk': project.id},
    )
    with pytest.raises(PermissionDenied):
        serializer.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_daily_rate_omitted_without_view_wage(api_client, project, other_user, member, user):
    labor = DailyReportLabor.objects.create(
        project=project,
        report_date='2026-04-01',
        labor_category=LaborCategory.DIRECT,
        job_title='Welder',
        shift_1_count=2,
        daily_rate='1500000',
    )
    hr_only = Role.objects.create(role_name='hr_no_wage_labor')
    RolePermission.objects.create(role=hr_only, permission_codename='view_hr')
    RolePermission.objects.create(role=hr_only, permission_codename='view_project')
    RolePermission.objects.create(role=hr_only, permission_codename='view_reports')
    ProjectMemberRole.objects.filter(member=member).delete()
    ProjectMemberRole.objects.create(member=member, role=hr_only)

    factory = APIRequestFactory()
    request = factory.get('/')
    request.user = other_user
    data = DailyReportLaborSerializer(labor, context={'request': request}).data
    assert 'daily_rate' not in data


@pytest.mark.django_db
def test_labor_headcount_alone_does_not_change_activity_progress(project, user, activity):
    before = ActivityProgress.objects.filter(activity=activity).count()
    report = DailyReport.objects.create(
        project=project,
        report_date='2026-04-05',
        status=ReportStatus.APPROVED,
        approved_by=user,
        created_by=user,
        updated_by=user,
    )
    DailyReportLabor.objects.create(
        report=report,
        project=project,
        report_date='2026-04-05',
        labor_category=LaborCategory.DIRECT,
        job_title='Crew',
        shift_1_count=10,
        daily_rate='1000',
    )
    recalculate_activity_progress(str(report.id))
    after = ActivityProgress.objects.filter(activity=activity).count()
    assert after == before
