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

    def test_delete_with_activities_returns_409(self, auth_client, project, user):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        Activity.objects.create(
            project=project,
            wbs=node,
            activity_code='A1',
            activity_name='Activity 1',
            created_by=user,
            updated_by=user,
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


from unittest.mock import patch
from wbs.services import WBSValidationError
from wbs.tree_builder import build_nested_wbs_tree

@pytest.mark.django_db
class TestWBSViewsMocks:
    def test_update_wbs_node_api(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        response = auth_client.patch(
            f'/api/v1/projects/{project.id}/wbs/{node.id}/',
            {'wbs_name': 'Updated Root'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['wbs_name'] == 'Updated Root'

    def test_update_wbs_node_api_invalid(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        with patch('wbs.views.update_wbs_node', side_effect=WBSValidationError("Test update validation error")):
            response = auth_client.patch(
                f'/api/v1/projects/{project.id}/wbs/{node.id}/',
                {'wbs_name': 'Updated Root'},
                format='json'
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_move_wbs_node_api(self, auth_client, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')
        with patch('wbs.views.move_wbs_node', return_value=node2) as mock_move:
            response = auth_client.post(
                f'/api/v1/projects/{project.id}/wbs/{node2.id}/move/',
                {'new_parent_id': str(node1.id), 'position': 'first-child'},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK

    def test_move_wbs_node_api_invalid(self, auth_client, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/{node2.id}/move/',
            {'new_parent_id': str(node1.id), 'position': 'invalid_pos'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_move_wbs_node_api_invalid_parent(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/{node.id}/move/',
            {'new_parent_id': None, 'position': 'first-child'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_move_wbs_node_api_invalid_wbs_id(self, auth_client, project):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/00000000-0000-0000-0000-000000000000/move/',
            {'new_parent_id': None, 'position': 'first-child'},
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_wbs_node_api(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        response = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{node.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_flat_list(self, auth_client, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')
        response = auth_client.get(f'/api/v1/projects/{project.id}/wbs/flat/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_wbs_node_api_validation_error(self, auth_client, project):
        project.max_depth = 1
        project.save(update_fields=['max_depth'])
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/wbs/',
            {'parent_id': str(root.id), 'wbs_code': '1.1', 'wbs_name': 'Child'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_wbs_node_api_conflict(self, auth_client, project):
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        child, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child')
        response = auth_client.delete(f'/api/v1/projects/{project.id}/wbs/{root.id}/')
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_build_nested_wbs_tree_empty(self, auth_client, project):
        response = auth_client.get(f'/api/v1/projects/{project.id}/wbs/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_update_wbs_node_api_warnings(self, auth_client, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root', weight_physical=Decimal('0.8'))
        response = auth_client.patch(
            f'/api/v1/projects/{project.id}/wbs/{node.id}/',
            {'weight_physical': '1.2'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'warnings' in response.data

    def test_move_wbs_node_api_validation_error2(self, auth_client, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')
        with patch('wbs.views.move_wbs_node', side_effect=WBSValidationError("Test move validation error")):
            response = auth_client.post(
                f'/api/v1/projects/{project.id}/wbs/{node2.id}/move/',
                {'new_parent_id': str(node1.id), 'position': 'sorted_child'},
                format='json'
            )
            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_build_nested_wbs_tree_orphans_deleted(self, project):
        root1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        child1, _ = create_wbs_node(project_id=project.id, parent_id=root1.id, wbs_code='1.1', wbs_name='Child 1')
        root2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')
        tree = build_nested_wbs_tree(project.id)
        assert len(tree) == 2
        assert len(tree[0]['children']) == 1

    def test_build_nested_wbs_tree_missing_parent(self, project):
        mock_annotated = [
            (WBS(id="00000000-0000-0000-0000-000000000001", wbs_code='1.1', wbs_name='Orphan', project=project, depth=2), {'level': 1})
        ]
        with patch('projects.models.WBS.get_annotated_list_qs', return_value=mock_annotated):
            with patch('projects.models.WBS.objects.filter') as mock_filter:
                mock_filter.return_value.exists.return_value = True
                result = build_nested_wbs_tree(project.id)
                assert len(result) == 0
