"""US2: WBS soft-delete hygiene."""
import pytest

from projects.models import WBS
from wbs.services import create_wbs_node, delete_wbs_node


@pytest.mark.django_db
def test_soft_delete_sets_flag_and_excludes_from_flat(auth_client, project, user):
    node, _ = create_wbs_node(
        project_id=project.id,
        wbs_code='9',
        wbs_name='Temp',
        created_by=user,
    )
    url = f'/api/v1/projects/{project.id}/wbs/{node.id}/'
    resp = auth_client.delete(url)
    assert resp.status_code == 204

    node.refresh_from_db()
    assert node.is_deleted is True
    assert node.deleted_at is not None

    flat = auth_client.get(f'/api/v1/projects/{project.id}/wbs/flat/')
    assert flat.status_code == 200
    ids = {row['wbs_id'] for row in flat.json()}
    assert str(node.id) not in ids
    assert WBS.objects.filter(pk=node.id, is_deleted=True).exists()


@pytest.mark.django_db
def test_delete_wbs_node_service_soft_deletes(project, user):
    node, _ = create_wbs_node(
        project_id=project.id,
        wbs_code='8',
        wbs_name='Service delete',
        created_by=user,
    )
    delete_wbs_node(node, user=user)
    node.refresh_from_db()
    assert node.is_deleted is True
