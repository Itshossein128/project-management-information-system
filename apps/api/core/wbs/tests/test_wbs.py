import pytest
from decimal import Decimal
from rest_framework import status

from projects.models import Activity, WBS
from wbs.services import create_wbs_node, delete_wbs_node


@pytest.mark.django_db
class TestWBSTree:
    def test_nested_tree_format(self, auth_client, project):
        root, _ = create_wbs_node(
            project_id=project.id,
            wbs_code='1',
            wbs_name='Root',
        )
        create_wbs_node(
            project_id=project.id,
            parent_id=root.id,
            wbs_code='1.1',
            wbs_name='Child',
        )
        response = auth_client.get(f'/api/v1/projects/{project.id}/wbs/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['wbs_code'] == '1'
        assert len(response.data[0]['children']) == 1
        assert response.data[0]['children'][0]['wbs_code'] == '1.1'

    def test_duplicate_wbs_code_returns_400(self, auth_client, project):
        create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {'wbs_code': '1', 'wbs_name': 'Duplicate'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_with_children_returns_409(self, auth_client, project):
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child')
        response = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{root.id}/')
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_delete_with_activities_returns_409(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        Activity.objects.create(
            project=project,
            wbs=node,
            activity_code='A1',
            activity_name='Activity 1',
        )
        response = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_weight_warning_when_siblings_exceed_one(self, auth_client, project):
        create_wbs_node(
            project_id=project.id,
            wbs_code='1',
            wbs_name='A',
            weight_physical=Decimal('0.6'),
        )
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {
                'wbs_code': '2',
                'wbs_name': 'B',
                'weight_physical': '0.5',
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert 'warnings' in response.data
        assert any('exceeds 1.0' in w for w in response.data['warnings'])

    def test_deep_tree_six_levels(self, auth_client, project):
        parent = None
        for i in range(1, 7):
            code = '.'.join(str(j) for j in range(1, i + 1))
            node, _ = create_wbs_node(
                project_id=project.id,
                parent_id=parent.id if parent else None,
                wbs_code=code,
                wbs_name=f'Level {i}',
            )
            parent = node
        response = auth_client.get(f'/api/v1/projects/{project.id}/wbs/')
        assert response.status_code == status.HTTP_200_OK
        current = response.data[0]
        depth = 1
        while current.get('children'):
            depth += 1
            current = current['children'][0]
        assert depth == 6

    def test_max_depth_blocks_create(self, auth_client, project):
        project.max_depth = 2
        project.save(update_fields=['max_depth'])
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        child, _ = create_wbs_node(
            project_id=project.id,
            parent_id=root.id,
            wbs_code='1.1',
            wbs_name='Child',
        )
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {'parent_id': str(child.id), 'wbs_code': '1.1.1', 'wbs_name': 'Too deep'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
