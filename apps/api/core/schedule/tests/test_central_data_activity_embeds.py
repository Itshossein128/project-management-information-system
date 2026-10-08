import pytest

from wbs.services import create_wbs_node


@pytest.mark.django_db
def test_activity_list_embeds_project_and_wbs(auth_client, project, user):
    wbs, _ = create_wbs_node(project_id=project.id, wbs_code='EMB', wbs_name='Embed')
    wbs.refresh_from_db()
    create = auth_client.post(
        f'/api/v1/projects/{project.id}/activities/',
        {
            'activity_code': 'EMB-1',
            'activity_name': 'Embed activity',
            'wbs_id': str(wbs.id),
            'total_quantity': '10',
        },
        format='json',
    )
    assert create.status_code == 201, create.content
    listing = auth_client.get(f'/api/v1/projects/{project.id}/activities/')
    assert listing.status_code == 200
    rows = listing.json()
    if isinstance(rows, dict):
        rows = rows.get('results', rows)
    match = next(r for r in rows if r.get('activity_code') == 'EMB-1')
    assert match['project_id'] == str(project.id)
    assert match['wbs_id'] == str(wbs.id)
    assert match['wbs_code'] == wbs.wbs_code
    assert match['wbs_code']  # non-empty drill-up identifier
