"""US6: disabled capability blocks create, allows history GET."""
import pytest

from projects.capability_service import update_capability_setting
from risk.models import EventType, RiskEvent, Severity


@pytest.mark.django_db
def test_disabled_risk_blocks_create_allows_list(auth_client, project, user):
    update_capability_setting(
        project, 'risk', enabled=False, mode='disabled', user=user
    )
    existing = RiskEvent.objects.create(
        project=project,
        event_type=EventType.RISK,
        description='Historical',
        severity=Severity.MEDIUM,
        created_by=user,
        updated_by=user,
    )

    list_resp = auth_client.get(f'/api/v1/projects/{project.id}/risk-events/')
    assert list_resp.status_code == 200
    ids = [str(r['id']) for r in list_resp.json().get('results', list_resp.json())]
    assert str(existing.id) in ids or any(
        str(existing.id) == str(r.get('id')) for r in (list_resp.json() if isinstance(list_resp.json(), list) else list_resp.json().get('results', []))
    )

    create_resp = auth_client.post(
        f'/api/v1/projects/{project.id}/risk-events/',
        {
            'event_type': EventType.RISK,
            'description': 'New blocked',
            'severity': Severity.LOW,
        },
        format='json',
    )
    assert create_resp.status_code in (403, 400)
    body = create_resp.json()
    blob = str(body)
    assert 'capability_disabled' in blob
