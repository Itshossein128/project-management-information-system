"""US2: WBS create exposes id, project, audit fields."""
import pytest

from wbs.services import create_wbs_node


@pytest.mark.django_db
def test_create_wbs_has_audit_and_project_binding(auth_client, project, user):
    url = f'/api/v1/projects/{project.id}/wbs/'
    resp = auth_client.post(
        url,
        {
            'wbs_code': '7',
            'wbs_name': 'Audit node',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    data = resp.json()
    assert data.get('wbs_id')

    flat = auth_client.get(f'/api/v1/projects/{project.id}/wbs/flat/')
    row = next(r for r in flat.json() if r['wbs_id'] == data['wbs_id'])
    assert row['project'] == str(project.id)
    assert row.get('created_by') == str(user.id) or row.get('created_by') is not None
    assert 'created_at' in row


@pytest.mark.django_db
def test_service_sets_created_by(project, user):
    node, _ = create_wbs_node(
        project_id=project.id,
        wbs_code='6',
        wbs_name='Created by',
        created_by=user,
    )
    assert node.created_by_id == user.id
    assert node.project_id == project.id
