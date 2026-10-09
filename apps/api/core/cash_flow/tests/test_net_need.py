from datetime import date

import pytest

from cash_flow.services.net_need_service import suggested_net_need


@pytest.mark.django_db
def test_suggested_net_need_formula(project, approved_ipc, approved_commitment):
    # due_commitments=800k, essential=0, certain_planned_receipts=1.2M → -400k
    result = suggested_net_need(project.id, date(2026, 10, 1), date(2026, 10, 31))
    assert result['due_commitments'] == 800000.0
    assert result['essential_costs'] == 0.0
    assert result['certain_planned_receipts'] == 1200000.0
    assert result['suggested_net_need'] == -400000.0
    assert result['meta']['essential_costs_rule'] == 'approved_actuals_in_categories_or_zero'


@pytest.mark.django_db
def test_suggested_need_api(auth_client, project, approved_ipc, approved_commitment):
    url = (
        f'/api/v1/projects/{project.id}/cash-flow/suggested-need/'
        f'?from=2026-10&to=2026-10'
    )
    resp = auth_client.get(url)
    assert resp.status_code == 200
    assert resp.data['suggested_net_need'] == -400000.0
