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


@pytest.mark.django_db
def test_by_date_get_is_safe_and_does_not_mutate_derived_rows(auth_client, by_date_url, project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr, description='poured slab')
    # First ensure via POST
    post_res = auth_client.post(by_date_url, {'report_date': SUMMARY_DATE.isoformat()}, format='json')
    assert post_res.status_code == status.HTTP_200_OK

    from field_reports.models import DailyReport
    report = DailyReport.objects.get(project=project, report_date=SUMMARY_DATE, is_deleted=False)
    initial_activity_ids = list(report.activities.values_list('id', flat=True))
    assert len(initial_activity_ids) == 1

    # Multiple subsequent GET requests must NOT mutate derived rows or churn primary keys
    get_res_1 = auth_client.get(by_date_url, {'date': SUMMARY_DATE.isoformat()})
    assert get_res_1.status_code == status.HTTP_200_OK

    get_res_2 = auth_client.get(by_date_url, {'date': SUMMARY_DATE.isoformat()})
    assert get_res_2.status_code == status.HTTP_200_OK

    report.refresh_from_db()
    current_activity_ids = list(report.activities.values_list('id', flat=True))
    assert current_activity_ids == initial_activity_ids
