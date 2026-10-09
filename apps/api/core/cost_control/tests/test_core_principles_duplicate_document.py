"""US7: duplicate invoice_number warning."""
from datetime import date

import pytest

from cost_control.models import ActualCost, CostCategory


@pytest.mark.django_db
def test_duplicate_invoice_requires_ack(auth_client, project, user, wbs):
    ActualCost.objects.create(
        project=project,
        wbs=wbs,
        cost_date=date(2024, 5, 1),
        cost_category=CostCategory.MATERIAL,
        amount=100,
        invoice_number='INV-100',
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'wbs': str(wbs.id),
            'cost_date': '2024-05-02',
            'cost_category': CostCategory.MATERIAL,
            'amount': '200',
            'invoice_number': 'INV-100',
            'description': 'dup',
        },
        format='json',
    )
    assert resp.status_code == 400
    assert 'warnings_unacknowledged' in str(resp.json()) or 'duplicate_document_ref' in str(
        resp.json()
    )

    ok = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'wbs': str(wbs.id),
            'cost_date': '2024-05-02',
            'cost_category': CostCategory.MATERIAL,
            'amount': '200',
            'invoice_number': 'INV-100',
            'description': 'dup-ack',
            'acknowledge_warnings': True,
        },
        format='json',
    )
    assert ok.status_code == 201, ok.content
