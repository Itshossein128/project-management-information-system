import pytest
from rest_framework import status

from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.mark.django_db
def test_cannot_post_activity_on_auto_summary(auth_client, project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    url = f'/api/v1/projects/{project.id}/daily-reports/{report.id}/activities/'
    response = auth_client.post(
        url,
        {
            'activity_description': 'manual',
            'shift': 'shift_1',
            'quantity_measured': False,
        },
        format='json',
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'تخصصی' in str(response.data) or 'derived' in str(response.data).lower()
