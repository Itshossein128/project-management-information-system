import pytest
from rest_framework import status

from field_reports.models import DailyReport
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, RolePermission
from sub_reports.models import SubReportStatus


@pytest.fixture
def viewer_member(project, other_user):
    role = Role.objects.create(role_name='summary_viewer_only', description='Summary viewer')
    RolePermission.objects.create(role=role, permission_codename='view_project')
    RolePermission.objects.create(role=role, permission_codename='view_reports')
    member = ProjectMember.objects.create(
        project=project, user=other_user, status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=role)
    return member


@pytest.mark.django_db
def test_view_reports_without_edit_can_get_by_date_existing_but_cannot_post(
    api_client, project, user, other_user, viewer_member,
):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    api_client.force_authenticate(user=other_user)
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'

    # GET existing returns 200
    assert api_client.get(by_date, {'date': SUMMARY_DATE.isoformat()}).status_code == status.HTTP_200_OK

    # POST returns 403 Forbidden because user lacks edit_reports
    post_res = api_client.post(by_date, {'date': SUMMARY_DATE.isoformat()}, format='json')
    assert post_res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_view_reports_without_edit_gets_404_on_missing_date_and_creates_no_records(
    api_client, project, other_user, viewer_member,
):
    api_client.force_authenticate(user=other_user)
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
    initial_count = DailyReport.objects.filter(project=project).count()

    res = api_client.get(by_date, {'date': '2026-08-01'})
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert DailyReport.objects.filter(project=project).count() == initial_count

    # POST returns 403 and still creates nothing
    post_res = api_client.post(by_date, {'date': '2026-08-01'}, format='json')
    assert post_res.status_code == status.HTTP_403_FORBIDDEN
    assert DailyReport.objects.filter(project=project).count() == initial_count


@pytest.mark.django_db
def test_editor_can_post_by_date_and_ensures_single_summary(
    auth_client, project, user,
):
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
    post_res_1 = auth_client.post(by_date, {'date': '2026-08-15'}, format='json')
    assert post_res_1.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    # Calling post again for the same date returns the same report, exactly 1 row
    post_res_2 = auth_client.post(by_date, {'date': '2026-08-15'}, format='json')
    assert post_res_2.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    assert DailyReport.objects.filter(project=project, report_date='2026-08-15', is_deleted=False).count() == 1
