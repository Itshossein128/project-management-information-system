import pytest

from projects.models import WBS
from wbs.services import create_wbs_node


@pytest.mark.django_db
def test_create_and_list_responsible_acceptance_status(auth_client, project, user):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {
            'wbs_code': '1',
            'wbs_name': 'Root',
            'responsible': str(user.id),
            'acceptance_criteria': 'Signed off',
            'status': 'active',
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    body = resp.json()
    assert body.get('responsible') == str(user.id)
    assert body.get('acceptance_criteria') == 'Signed off'
    assert body.get('status') == 'active'

    node = WBS.objects.get(pk=body['wbs_id'])
    assert node.responsible_id == user.id
    assert node.acceptance_criteria == 'Signed off'
    assert node.status == 'active'

    tree = auth_client.get(f'/api/v1/projects/{project.id}/wbs/')
    assert tree.status_code == 200
    assert tree.json()[0]['responsible'] == str(user.id)
    assert tree.json()[0]['acceptance_criteria'] == 'Signed off'


@pytest.mark.django_db
def test_three_level_tree_with_leaf_package_fields(auth_client, project, user):
    root = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {'wbs_code': '1', 'wbs_name': 'Project', 'status': 'active'},
        format='json',
    )
    assert root.status_code == 201, root.content
    root_id = root.json()['wbs_id']

    phase = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {'parent_id': root_id, 'wbs_code': '1.1', 'wbs_name': 'Phase', 'status': 'active'},
        format='json',
    )
    assert phase.status_code == 201, phase.content
    phase_id = phase.json()['wbs_id']

    leaf = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {
            'parent_id': phase_id,
            'wbs_code': '1.1.1',
            'wbs_name': 'WP',
            'responsible': str(user.id),
            'acceptance_criteria': 'Complete pour',
            'status': 'active',
        },
        format='json',
    )
    assert leaf.status_code == 201, leaf.content
    assert leaf.json()['acceptance_criteria'] == 'Complete pour'

    tree = auth_client.get(f'/api/v1/projects/{project.id}/wbs/').json()
    assert len(tree) == 1
    assert len(tree[0]['children']) == 1
    assert len(tree[0]['children'][0]['children']) == 1
    wp = tree[0]['children'][0]['children'][0]
    assert wp['responsible'] == str(user.id)
    assert wp['acceptance_criteria'] == 'Complete pour'


@pytest.mark.django_db
def test_patch_acceptance_and_status(auth_client, project):
    node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    resp = auth_client.patch(
        f'/api/v1/projects/{project.id}/wbs/{node.id}/',
        {'acceptance_criteria': 'Done', 'status': 'completed'},
        format='json',
    )
    assert resp.status_code == 200, resp.content
    assert resp.json()['acceptance_criteria'] == 'Done'
    assert resp.json()['status'] == 'completed'


@pytest.mark.django_db
def test_responsible_must_be_active_project_member(auth_client, project, other_user):
    """T033: responsible must be an active ProjectMember of the same project."""
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {
            'wbs_code': '1',
            'wbs_name': 'Root',
            'responsible': str(other_user.id),
        },
        format='json',
    )
    assert resp.status_code == 400, resp.content
    assert resp.json()['error']['code'] == 'invalid_responsible'


@pytest.mark.django_db
def test_responsible_rejects_inactive_member(auth_client, project, member):
    from master_data.models import MemberStatus

    member.status = MemberStatus.INACTIVE
    member.save(update_fields=['status'])

    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {
            'wbs_code': '1',
            'wbs_name': 'Root',
            'responsible': str(member.user_id),
        },
        format='json',
    )
    assert resp.status_code == 400, resp.content
    assert resp.json()['error']['code'] == 'invalid_responsible'


@pytest.mark.django_db
def test_responsible_accepts_active_member(auth_client, project, member):
    resp = auth_client.post(
        f'/api/v1/projects/{project.id}/wbs/',
        {
            'wbs_code': '1',
            'wbs_name': 'Root',
            'responsible': str(member.user_id),
        },
        format='json',
    )
    assert resp.status_code == 201, resp.content
    assert resp.json()['responsible'] == str(member.user_id)
