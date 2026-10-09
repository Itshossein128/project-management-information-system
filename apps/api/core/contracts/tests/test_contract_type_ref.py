import pytest

from contracts.models import Contract
from master_data.models import ManagedContractType


@pytest.mark.django_db
def test_create_contract_with_contract_type_ref(finance_client, project, user):
    ct = ManagedContractType.objects.create(
        code='subcontract',
        name_fa='پیمانکاری',
        name_en='Subcontract',
    )
    resp = finance_client.post(
        f'/api/v1/projects/{project.id}/contracts/',
        {
            'contract_number': 'CT-REF-1',
            'contract_type': 'subcontract',
            'contract_type_ref': str(ct.id),
            'counterparty': 'Sub Co',
            'original_amount': '100000',
            'adjusted_amount': '100000',
            'retention_pct': '10',
            'tax_pct': '9',
            'insurance_pct': '1',
            'advance_payment_pct': '0',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    contract = Contract.objects.get(pk=resp.json()['id'])
    assert contract.contract_type_ref_id == ct.id
    assert resp.json().get('contract_type_ref') == str(ct.id)


@pytest.mark.django_db
def test_contract_type_ref_without_legacy_enum_still_persists(finance_client, project):
    """Legacy contract_type enum is blank-able; catalog ref alone is enough."""
    ct = ManagedContractType.objects.create(
        code='consulting',
        name_fa='مشاوره',
        name_en='Consulting',
    )
    resp = finance_client.post(
        f'/api/v1/projects/{project.id}/contracts/',
        {
            'contract_number': 'CT-REF-2',
            'contract_type_ref': str(ct.id),
            'counterparty': 'Consult Co',
            'original_amount': '50000',
            'adjusted_amount': '50000',
            'retention_pct': '0',
            'tax_pct': '0',
            'insurance_pct': '0',
            'advance_payment_pct': '0',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert Contract.objects.get(pk=resp.json()['id']).contract_type_ref_id == ct.id
