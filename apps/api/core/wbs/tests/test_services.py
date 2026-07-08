import pytest




from projects.models import Activity, WBS
from wbs.services import (
    WBSConflictError,
    WBSValidationError,

    create_wbs_node,
    update_wbs_node,
    delete_wbs_node,
    move_wbs_node,
    build_tree_queryset,
)


@pytest.mark.django_db
class TestWBSServices:
    def test_create_wbs_node_duplicate_code(self, project):
        create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        with pytest.raises(WBSValidationError):
            create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Duplicate')

    def test_update_wbs_node(self, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        updated_node, warnings = update_wbs_node(node, wbs_name='Updated Root')
        assert updated_node.wbs_name == 'Updated Root'
        assert not warnings

    def test_delete_wbs_node_with_children(self, project):
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child')

        root.refresh_from_db()

        with pytest.raises(WBSConflictError):
            delete_wbs_node(root)

    def test_delete_wbs_node_with_activities(self, project, user):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        Activity.objects.create(
            project=project,
            wbs=node,
            activity_code='A1',
            activity_name='Activity 1',
            created_by=user,
            updated_by=user,
        )

        with pytest.raises(WBSConflictError):
            delete_wbs_node(node)

    def test_delete_wbs_node_success(self, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        delete_wbs_node(node)
        assert WBS.objects.filter(id=node.id).count() == 0

    def test_move_wbs_node_invalid_position(self, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Node 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Node 2')

        with pytest.raises(WBSValidationError):
            move_wbs_node(node2, new_parent_id=node1.id, position='invalid_pos')

    def test_move_wbs_node_first_child_missing_parent(self, project):
        node, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Node 1')
        with pytest.raises(WBSValidationError):
            move_wbs_node(node, new_parent_id=None, position='first_child')

    def test_move_wbs_node_success(self, project):
        node1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Node 1')
        node2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Node 2')

        moved_node = move_wbs_node(node2, new_parent_id=node1.id, position='sorted_child')
        assert moved_node.get_parent().id == node1.id

    def test_build_tree_queryset(self, project):
        create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')

        qs = build_tree_queryset(project.id)
        assert qs.count() == 2
