"""FR-COL US4: correspondence related_contract same-project validation."""

from datetime import date

import pytest

from contracts.models import Contract, ContractType
from projects.services import create_project_with_creator


@pytest.mark.django_db
def test_correspondence_same_project_contract(auth_client, project, user, contract):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/correspondence/',
        {
            'corr_number': 'CORR-C-001',
            'corr_type': 'incoming',
            'subject': 'Contract notice',
            'from_party': 'Employer',
            'to_party': 'Contractor',
            'corr_date': date.today().isoformat(),
            'related_contract': str(contract.id),
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    corr_id = resp.json()['id']
    assert str(resp.json().get('related_contract')) == str(contract.id)

    listing = auth_client.get(f'/api/v1/projects/{project.id}/correspondence/')
    assert listing.status_code == 200
    rows = listing.data['results']
    row = next(r for r in rows if r['id'] == corr_id)
    assert str(row.get('related_contract')) == str(contract.id)


@pytest.mark.django_db
def test_correspondence_cross_project_contract_rejected(auth_client, project, user):
    other = create_project_with_creator(
        creator=user,
        project_code='PRJ-OTHER',
        project_name='Other Project',
        employer='Other',
        start_date='2024-06-01',
    )
    foreign = Contract.objects.create(
        project=other,
        contract_number='C-FOREIGN',
        contract_type=ContractType.MAIN,
        counterparty='Other Co',
        original_amount='100',
        adjusted_amount='100',
        retention_pct='0',
        tax_pct='0',
        insurance_pct='0',
        advance_payment_pct='0',
        created_by=user,
        updated_by=user,
    )

    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/correspondence/',
        {
            'corr_number': 'CORR-BAD-001',
            'corr_type': 'outgoing',
            'subject': 'Bad link',
            'from_party': 'A',
            'to_party': 'B',
            'corr_date': date.today().isoformat(),
            'related_contract': str(foreign.id),
        },
        format='json',
    )
    assert resp.status_code == 400
