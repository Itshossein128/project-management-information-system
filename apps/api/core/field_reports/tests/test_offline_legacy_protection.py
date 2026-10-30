"""Canonical protection of derived summaries across legacy HTTP mutation paths (T005)."""
import pytest

from field_reports.models import DailyReport, DailyReportActivity, DailyReportDerivedSource
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import SUMMARY_DATE, add_activity, make_sub_report
from sub_reports.models import SubReportStatus

pytestmark = pytest.mark.django_db


@pytest.fixture
def derived_summary(project, user):
    source = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(source, description='original source activity')
    report = ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)
    row = report.activities.get(activity_description='original source activity')
    assert row.is_derived
    assert DailyReportDerivedSource.objects.filter(daily_report=report, derived_row_id=str(row.id)).exists()
    return report, row


def snapshot(report):
    return (
        list(DailyReportActivity.objects.filter(report=report).order_by('id').values()),
        list(DailyReportDerivedSource.objects.filter(daily_report=report).order_by('id').values()),
    )


def assert_derived_readonly(response, *, code='derived_readonly'):
    assert response.status_code == 400
    assert response.data['error']['code'] == code


@pytest.mark.parametrize('method', ['post', 'patch', 'delete'])
def test_summary_child_writes_are_rejected_and_preserve_provenance(auth_client, project, derived_summary, method):
    report, row = derived_summary
    before = snapshot(report)
    url = f'/api/v1/projects/{project.id}/daily-reports/{report.id}/activities/'
    if method == 'post':
        response = auth_client.post(url, {'activity_description': 'manual', 'shift': 'shift_1'}, format='json')
    elif method == 'patch':
        response = auth_client.patch(f'{url}{row.id}/', {'activity_description': 'overwritten'}, format='json')
    else:
        response = auth_client.delete(f'{url}{row.id}/')
    assert snapshot(report) == before
    assert_derived_readonly(response, code='derived_collection_read_only')


@pytest.mark.parametrize('activities', [[], [{'activity_description': 'manual', 'shift': 'shift_1'}]])
def test_summary_patch_rejects_authored_or_empty_activities(auth_client, project, derived_summary, activities):
    report, _ = derived_summary
    before = snapshot(report)
    response = auth_client.patch(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/',
        {'activities': activities}, format='json',
    )
    assert snapshot(report) == before
    assert_derived_readonly(response)


@pytest.mark.parametrize('activities', [[], [{'activity_description': 'manual', 'shift': 'shift_1', 'quantity_measured': False}]])
def test_existing_summary_legacy_batch_rejects_derived_mutation(auth_client, project, derived_summary, activities):
    report, _ = derived_summary
    before = snapshot(report)
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-batch/',
        [{'local_id': 'batch-existing', 'report_date': str(SUMMARY_DATE), 'activities': activities}], format='json',
    )
    assert snapshot(report) == before
    assert response.status_code == 200
    assert response.data['summary']['errors'] == 1
    assert 'derived_readonly' in str(response.data['results'][0])


def test_legacy_create_rejects_authored_activities_without_creating_report(auth_client, project):
    report_date = '2024-06-11'
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/',
        {'report_date': report_date, 'activities': [{'activity_description': 'manual', 'shift': 'shift_1'}]},
        format='json',
    )
    assert not DailyReport.objects.filter(project=project, report_date=report_date).exists()
    assert_derived_readonly(response)


def test_legacy_batch_create_rejects_authored_activities_without_shell(auth_client, project):
    report_date = '2024-06-12'
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-batch/',
        [{'local_id': 'batch-new', 'report_date': report_date,
          'activities': [{'activity_description': 'manual', 'shift': 'shift_1', 'quantity_measured': False}]}],
        format='json',
    )
    assert not DailyReport.objects.filter(project=project, report_date=report_date).exists()
    assert response.status_code == 200
    assert response.data['summary']['errors'] == 1
    assert 'derived_readonly' in str(response.data['results'][0])


def test_invalid_new_header_rolls_back_shell_and_independent_item_succeeds(auth_client, project):
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/sync-batch/',
        [{'local_id': 'bad-header', 'report_date': '2024-06-13', 'temp_min': 40, 'temp_max': 10},
         {'local_id': 'good-header', 'report_date': '2024-06-14', 'site_status': 'active'}],
        format='json',
    )
    assert response.status_code == 200
    assert response.data['summary']['errors'] == 1
    assert response.data['summary']['created'] == 1
    assert not DailyReport.objects.filter(project=project, report_date='2024-06-13').exists()
    assert DailyReport.objects.filter(project=project, report_date='2024-06-14').exists()


@pytest.mark.parametrize('section', ['labor_summary', 'materials_summary', 'attachment_counts', 'aggregation'])
def test_summary_metadata_patch_rejects_derived_totals(auth_client, project, derived_summary, section):
    report, _ = derived_summary
    before = snapshot(report)
    response = auth_client.patch(
        f'/api/v1/projects/{project.id}/daily-reports/{report.id}/',
        {section: []}, format='json',
    )
    assert snapshot(report) == before
    assert_derived_readonly(response)


def test_by_date_cannot_accept_authored_derived_rows(auth_client, project):
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/by-date/',
        {'report_date': '2024-06-15', 'activities': []}, format='json',
    )
    assert not DailyReport.objects.filter(project=project, report_date='2024-06-15').exists()
    assert_derived_readonly(response)
