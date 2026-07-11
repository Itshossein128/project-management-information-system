import pytest

from cash_flow.models import CashTransaction, CashTransactionType

BASE = '/api/v1/projects/{project_id}/cash-flow'


@pytest.fixture
def cash_tx(db, project, user):
    return CashTransaction.objects.create(
        project=project,
        tx_date='2024-04-15',
        tx_type=CashTransactionType.IN,
        category='other_income',
        amount='1000000',
        description='Test inflow',
        counterparty='Employer',
        created_by=user,
        updated_by=user,
    )


def test_list_cash_flow(auth_client, project, cash_tx):
    url = f'{BASE.format(project_id=project.id)}/'
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['summary']['total_inflow'] == 1000000.0
    assert len(resp.data['results']) == 1


def test_create_transaction(auth_client, project):
    url = f'{BASE.format(project_id=project.id)}/transactions/'
    resp = auth_client.post(
        url,
        {
            'tx_date': '1403/01/15',
            'tx_type': 'out',
            'category': 'salary',
            'amount': '500000',
            'description': 'Payroll',
            'counterparty': 'Staff',
        },
        format='json',
    )
    assert resp.status_code == 201
    assert resp.data['amount'] == '500000.00'


def test_reject_zero_amount(auth_client, project):
    url = f'{BASE.format(project_id=project.id)}/transactions/'
    resp = auth_client.post(
        url,
        {
            'tx_date': '2024-04-01',
            'tx_type': 'in',
            'category': 'other_income',
            'amount': '0',
        },
        format='json',
    )
    assert resp.status_code == 400


def test_monthly_summary(auth_client, project, cash_tx):
    url = f'{BASE.format(project_id=project.id)}/monthly/'
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) >= 1
    assert resp.data['results'][0]['inflow'] == 1000000.0


def test_gap_analysis(auth_client, project, user):
    from cash_flow.models import CashFlowForecast

    CashFlowForecast.objects.create(
        project=project,
        month='2024-05-01',
        expected_inflow='100',
        expected_outflow='500',
        created_by=user,
        updated_by=user,
    )
    url = f'{BASE.format(project_id=project.id)}/gap-analysis/'
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data['results']) == 1
    assert resp.data['results'][0]['net'] < 0


def test_forecast_upsert(auth_client, project):
    url = f'{BASE.format(project_id=project.id)}/forecast/2024-06/'
    resp = auth_client.put(
        url,
        {'expected_inflow': '2000000', 'expected_outflow': '1500000', 'confidence_pct': '80'},
        format='json',
    )
    assert resp.status_code == 200
    assert float(resp.data['expected_inflow']) == 2000000.0
