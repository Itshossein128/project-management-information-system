import pytest

from cost_control.models import CostBreakdownNode


@pytest.mark.django_db
def test_create_cbs_node(auth_client, project):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/cbs/',
        {'cbs_code': 'C.1', 'cbs_name': 'Labor', 'cost_type': 'labor'},
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert CostBreakdownNode.objects.filter(project=project, cbs_code='C.1', is_deleted=False).exists()


@pytest.mark.django_db
def test_list_cbs(auth_client, project, user):
    CostBreakdownNode.add_root(
        project_id=project.id,
        cbs_code='C.2',
        cbs_name='Material',
        cost_type='material',
        created_by=user,
        updated_by=user,
    )
    resp = auth_client.get(f'/api/v1/projects/{project.id}/cbs/')
    assert resp.status_code == 200
    assert any(r['cbs_code'] == 'C.2' for r in resp.json())


@pytest.mark.django_db
def test_cannot_delete_cbs_with_child(auth_client, project, user):
    from cost_control.cbs_services import create_cbs_node

    parent = create_cbs_node(
        project_id=project.id,
        cbs_code='P.1',
        cbs_name='Parent',
        created_by=user,
    )
    create_cbs_node(
        project_id=project.id,
        parent_id=parent.id,
        cbs_code='P.1.1',
        cbs_name='Child',
        created_by=user,
    )
    resp = auth_client.delete(f'/api/v1/projects/{project.id}/cbs/{parent.id}/')
    assert resp.status_code == 409
