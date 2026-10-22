import pytest
from rest_framework import status

from field_reports.models import DailyReport
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from sub_reports.models import SubReportStatus


@pytest.fixture
def by_date_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/by-date/'


@pytest.fixture
def collection_url(project):
    return f'/api/v1/projects/{project.id}/daily-reports/'


@pytest.mark.django_db
def test_by_date_get_existing_returns_200(auth_client, by_date_url, project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr, description='civil work')
    # First create via POST
    post_res = auth_client.post(by_date_url, {'date': SUMMARY_DATE.isoformat()}, format='json')
    assert post_res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    # Now GET returns existing report
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
def test_by_date_get_missing_returns_404_without_mutating(auth_client, by_date_url, project):
    initial_count = DailyReport.objects.filter(project=project).count()
    response = auth_client.get(by_date_url, {'date': '2026-07-01'})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert DailyReport.objects.filter(project=project).count() == initial_count


@pytest.mark.django_db
def test_by_date_post_ensures_and_returns_aggregation(auth_client, by_date_url, project, user):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr, description='poured slab')

    post_res = auth_client.post(by_date_url, {'date': SUMMARY_DATE.isoformat()}, format='json')
    assert post_res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    assert post_res.data['is_auto_summary'] is True
    assert DailyReport.objects.filter(project=project, report_date=SUMMARY_DATE).count() == 1


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
    assert post_res.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

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


@pytest.mark.django_db
def test_raw_collection_post_returns_400_auto_summary_only(auth_client, collection_url):
    payload = {
        'report_date': '2026-10-22',
        'shift': 'full',
    }
    response = auth_client.post(collection_url, payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data.get('code') == 'auto_summary_only' or response.data.get('error', {}).get('code') == 'auto_summary_only'
