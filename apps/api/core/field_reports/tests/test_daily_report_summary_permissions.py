import pytest
from rest_framework import status

from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, RolePermission
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_view_reports_without_edit_can_get_by_date_but_not_create_sub_report(
    api_client, project, user, other_user,
):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    role = Role.objects.create(role_name='summary_viewer_only', description='Summary viewer')
    RolePermission.objects.create(role=role, permission_codename='view_project')
    RolePermission.objects.create(role=role, permission_codename='view_reports')
    member = ProjectMember.objects.create(
        project=project, user=other_user, status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=role)
    api_client.force_authenticate(user=other_user)

    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
    assert api_client.get(by_date, {'date': SUMMARY_DATE.isoformat()}).status_code == status.HTTP_200_OK

    sub_url = f'/api/v1/projects/{project.id}/sub-reports/'
    resp = api_client.post(
        sub_url,
        {'report_date': '1403/03/21', 'discipline': 'civil'},
        format='json',
    )
    assert resp.status_code == status.HTTP_403_FORBIDDEN
