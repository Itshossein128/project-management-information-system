import pytest


BASE = '/api/v1/projects/{project_id}/contracts/'


@pytest.mark.django_db
def test_create_and_retrieve_payment_terms(finance_client, project):
    url = BASE.format(project_id=project.id)
    create = finance_client.post(
        url,
        {
            'contract_number': 'C-PT-1',
            'contract_type': 'main',
            'counterparty': 'Owner',
            'original_amount': '1000000',
            'payment_terms': 'Net 30 after IPC approval',
            'status': 'active',
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    assert create.data['payment_terms'] == 'Net 30 after IPC approval'

    detail = finance_client.get(f'{url}{create.data["id"]}/')
    assert detail.status_code == 200
    assert detail.data['payment_terms'] == 'Net 30 after IPC approval'

    patch = finance_client.patch(
        f'{url}{create.data["id"]}/',
        {'payment_terms': 'Net 45; retention at final'},
        format='json',
    )
    assert patch.status_code == 200
    assert patch.data['payment_terms'] == 'Net 45; retention at final'
