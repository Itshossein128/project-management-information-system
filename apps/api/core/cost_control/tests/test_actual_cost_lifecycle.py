"""US2: actual cost occurrence/register dates, approve/void, document policy."""

from decimal import Decimal

import pytest
from rest_framework import status

from cost_control.models import ActualCostStatus, CostCategory
from projects.models import CapabilityMode, ProjectCapabilitySetting
from cost_control.services.actual_cost_service import REQUIRE_COST_DOCUMENT_KEY


@pytest.mark.django_db
def test_approve_requires_wbs_or_cbs(auth_client, project):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'amount': '100',
            'cost_date': '2024-06-01',
            'cost_category': CostCategory.LABOR,
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    body = create.json()
    assert body['status'] == ActualCostStatus.DRAFT
    assert body.get('registered_at')
    approve = auth_client.post(f'/api/v1/projects/{project.id}/costs/{body["id"]}/approve/')
    assert approve.status_code == status.HTTP_400_BAD_REQUEST
    assert 'wbs_or_cbs_required' in str(approve.json())


@pytest.mark.django_db
def test_approve_and_void_with_classification(auth_client, project, wbs):
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'amount': '250',
            'cost_date': '2024-06-01',
            'registered_at': '2024-06-02',
            'wbs': str(wbs.id),
            'cost_category': CostCategory.LABOR,
            'invoice_number': 'INV-AC-1',
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    cid = create.json()['id']
    approve = auth_client.post(f'/api/v1/projects/{project.id}/costs/{cid}/approve/')
    assert approve.status_code == status.HTTP_200_OK, approve.content
    assert approve.json()['status'] == ActualCostStatus.APPROVED
    void = auth_client.post(f'/api/v1/projects/{project.id}/costs/{cid}/void/')
    assert void.status_code == status.HTTP_200_OK, void.content
    assert void.json()['status'] == ActualCostStatus.VOID


@pytest.mark.django_db
def test_document_required_when_policy_enabled(auth_client, project, wbs, user):
    ProjectCapabilitySetting.objects.create(
        project=project,
        capability_key=REQUIRE_COST_DOCUMENT_KEY,
        enabled=True,
        mode=CapabilityMode.OPTIONAL,
        created_by=user,
        updated_by=user,
    )
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'amount': '50',
            'cost_date': '2024-06-01',
            'wbs': str(wbs.id),
            'cost_category': CostCategory.LABOR,
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    approve = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/{create.json()["id"]}/approve/'
    )
    assert approve.status_code == status.HTTP_400_BAD_REQUEST
    assert 'cost_document_required' in str(approve.json())


@pytest.mark.django_db
def test_commitment_and_actual_separate_in_ledger(auth_client, project, wbs, user):
    from cost_control.models import Commitment, CommitmentStatus

    commitment = Commitment.objects.create(
        project=project,
        commitment_number='CM-LED-1',
        amount=Decimal('600'),
        commitment_date='2024-01-01',
        wbs=wbs,
        status=CommitmentStatus.APPROVED,
        document_ref='PO-LED-1',
        created_by=user,
        updated_by=user,
    )
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/costs/',
        {
            'amount': '400',
            'cost_date': '2024-02-01',
            'wbs': str(wbs.id),
            'commitment': str(commitment.id),
            'cost_category': CostCategory.LABOR,
            'document_ref': 'INV-LED-1',
        },
        format='json',
    )
    assert create.status_code == status.HTTP_201_CREATED, create.content
    auth_client.post(f'/api/v1/projects/{project.id}/costs/{create.json()["id"]}/approve/')
    report = auth_client.get(f'/api/v1/projects/{project.id}/costs/ledger-report/')
    assert report.status_code == status.HTTP_200_OK, report.content
    types = {r['row_type'] for r in report.json()['rows']}
    assert 'commitment' in types
    assert 'actual' in types
    amounts = {
        (r['row_type'], r['document_ref']): r['amount'] for r in report.json()['rows']
    }
    assert amounts[('commitment', 'PO-LED-1')] == 600.0
    assert amounts[('actual', 'INV-LED-1')] == 400.0
