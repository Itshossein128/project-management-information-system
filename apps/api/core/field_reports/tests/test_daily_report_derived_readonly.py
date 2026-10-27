from uuid import uuid4

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


@pytest.mark.django_db
def test_v2_project_metadata_cannot_author_derived_rows(auth_client, project, user, settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True
    source = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(source, description='original source activity')
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    before = list(report.activities.order_by('id').values_list('id', 'activity_description', 'is_derived'))
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/',
        {
            'contract_version': 2,
            'operations': [{
                'operation_id': str(uuid4()),
                'local_report_id': str(uuid4()),
                'scope': {'kind': 'project_metadata', 'report_date': str(SUMMARY_DATE), 'report_id': str(report.id)},
                'action': 'create',
                'target': {'kind': 'activity', 'client_id': str(uuid4()), 'server_id': None},
                'base_revision': None,
                'depends_on': [],
                'payload': {'activity_description': 'injected derived row'},
            }],
        },
        format='json',
    )
    assert response.status_code == 200, response.content
    assert response.data['results'][0]['error']['code'] == 'derived_readonly'
    assert response.data['synced_ids'] == []
    report.refresh_from_db()
    assert list(report.activities.order_by('id').values_list('id', 'activity_description', 'is_derived')) == before
