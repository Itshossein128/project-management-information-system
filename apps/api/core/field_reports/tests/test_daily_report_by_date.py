import pytest
from rest_framework import status

from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.fixture
def by_date_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/by-date/'


@pytest.mark.django_db
def test_by_date_ensures_and_returns_aggregation(auth_client, by_date_url, project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr, description='civil work')
    response = auth_client.get(by_date_url, {'date': SUMMARY_DATE.isoformat()})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['is_auto_summary'] is True
    assert 'aggregation' in response.data
    agg = response.data['aggregation']
    assert 'civil' in agg['contributing_disciplines']
    assert agg['is_partial'] is True
    descs = [a['activity_description'] for a in response.data['activities']]
    assert 'civil work' in descs


@pytest.mark.django_db
def test_by_date_empty_day(auth_client, by_date_url):
    response = auth_client.get(by_date_url, {'date': '2024-07-01'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['activities'] == []
    assert response.data['aggregation']['is_partial'] is True
    assert response.data['aggregation']['contributing_disciplines'] == []


@pytest.mark.django_db
def test_by_date_requires_date(auth_client, by_date_url):
    response = auth_client.get(by_date_url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
