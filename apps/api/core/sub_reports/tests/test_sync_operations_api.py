"""v2 batch outcomes (feature 037, T032)."""
from datetime import date
from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_v2_sync(settings):
    settings.V2_OFFLINE_SYNC_ENABLED = True


def endpoint(project):
    return f'/api/v1/projects/{project.id}/daily-reports/sync-operations/v2/'


def create_report(day):
    return {
        'operation_id': str(uuid4()),
        'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': day, 'report_id': None},
        'action': 'create_report',
        'target': {'kind': 'header'},
        'base_revision': None,
        'depends_on': [],
        'payload': {'form_code': f'B-{day}'},
    }


def test_independent_operations_commit_and_invalid_header_leaves_no_shell(project, user):
    client = APIClient()
    client.force_authenticate(user)
    operations = [create_report(f'2026-11-{day:02d}') for day in range(1, 11)]
    invalid = create_report('2026-11-20')
    invalid['scope']['unit'] = 'not-a-unit'
    response = client.post(endpoint(project), {'contract_version': 2, 'operations': [*operations, invalid]}, format='json')
    assert response.status_code == 200, response.content
    by_id = {item['operation_id']: item for item in response.data['results']}
    assert response.data['synced_ids'] == [item['operation_id'] for item in operations]
    assert all(by_id[item['operation_id']]['outcome'] == 'success' for item in operations)
    assert by_id[invalid['operation_id']]['outcome'] == 'validation_error'
    assert invalid['operation_id'] not in response.data['synced_ids']
    assert DisciplineSubReport.objects.filter(project=project, report_date__gte=date(2026, 11, 1), report_date__lte=date(2026, 11, 10)).count() == 10
    assert not DisciplineSubReport.objects.filter(project=project, report_date=date(2026, 11, 20)).exists()
    assert not DisciplineSubReportActivity.objects.filter(sub_report__project=project, sub_report__report_date=date(2026, 11, 20)).exists()


def test_reordered_results_still_identify_operations_by_id(project, user):
    client = APIClient()
    client.force_authenticate(user)
    first = create_report('2026-12-01')
    second = create_report('2026-12-02')
    response = client.post(endpoint(project), {'contract_version': 2, 'operations': [first, second]}, format='json')
    assert {item['operation_id'] for item in response.data['results']} == {first['operation_id'], second['operation_id']}
    assert set(response.data['synced_ids']) == {first['operation_id'], second['operation_id']}
