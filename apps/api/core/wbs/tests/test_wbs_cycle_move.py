import pytest

from wbs.services import create_wbs_node, move_wbs_node, WBSValidationError


@pytest.mark.django_db
def test_move_under_descendant_rejected_api(auth_client, project):
    root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    child, _ = create_wbs_node(
        project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child'
    )
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/{root.id}/move/',
        {'new_parent_id': str(child.id), 'position': 'last-child'},
        format='json',
    )
    assert resp.status_code == 400
    payload = resp.json()
    blob = str(payload)
    assert 'wbs_cycle' in blob


@pytest.mark.django_db
def test_move_under_self_rejected(project):
    root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    with pytest.raises(WBSValidationError) as exc:
        move_wbs_node(root, new_parent_id=root.id, position='last-child')
    assert getattr(exc.value, 'code', '') == 'wbs_cycle' or 'cycle' in str(exc.value).lower()
