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
        node2.refresh_from_db()
        assert node2.wbs_code == '1.1'

    def test_propagate_wbs_codes(self, project):
        from wbs.services import propagate_project_wbs_codes

        root, _ = create_wbs_node(project_id=project.id, wbs_code='X', wbs_name='Root')
        child, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='Y', wbs_name='Child')
        propagate_project_wbs_codes(project.id)
        root.refresh_from_db()
        child.refresh_from_db()
        assert root.wbs_code == '1'
        assert child.wbs_code == '1.1'

    def test_build_tree_queryset(self, project):
        create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1')
        create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2')

        qs = build_tree_queryset(project.id)
        assert qs.count() == 2


from decimal import Decimal
from wbs.services import check_weight_warnings, _sibling_weight_sum, WBSValidationError

@pytest.mark.django_db
class TestWBSServicesExtended:
    def test_check_weight_warnings(self, project):
        root1, warnings1 = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1', weight_physical=Decimal('0.6'))
        assert not warnings1

        root2, warnings2 = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2', weight_physical=Decimal('0.5'))
        assert len(warnings2) == 1
        assert "weight physical" in warnings2[0]

        warnings_root = check_weight_warnings(None, project.id)
        assert len(warnings_root) == 1

        child1, warnings3 = create_wbs_node(project_id=project.id, parent_id=root1.id, wbs_code='1.1', wbs_name='Child 1', weight_financial=Decimal('0.8'))
        assert not warnings3

        root1.refresh_from_db()
        child2, warnings4 = create_wbs_node(project_id=project.id, parent_id=root1.id, wbs_code='1.2', wbs_name='Child 2', weight_financial=Decimal('0.3'))

        root1.refresh_from_db()
        assert len(warnings4) == 1
        assert "weight financial" in warnings4[0]

        warnings_child = check_weight_warnings(root1, project.id)
        assert len(warnings_child) == 1

    def test_sibling_weight_sum_root(self, project):
        root1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1', weight_physical=Decimal('0.4'))
        root2, _ = create_wbs_node(project_id=project.id, wbs_code='2', wbs_name='Root 2', weight_physical=Decimal('0.3'))

        total = _sibling_weight_sum(None, 'weight_physical')
        assert total == Decimal('0')

    def test_sibling_weight_sum_child(self, project):
        root1, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root 1', weight_physical=Decimal('0.4'))
        child1, _ = create_wbs_node(project_id=project.id, parent_id=root1.id, wbs_code='1.1', wbs_name='Child 1', weight_physical=Decimal('0.6'))
        child2, _ = create_wbs_node(project_id=project.id, parent_id=root1.id, wbs_code='1.2', wbs_name='Child 2', weight_physical=Decimal('0.2'))

        root1.refresh_from_db()
        total = _sibling_weight_sum(root1, 'weight_physical')
        assert total == Decimal('0.8')

    def test_move_wbs_node_invalid(self, project):
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        child1, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child 1')
        child2, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.2', wbs_name='Child 2')

        with pytest.raises(Exception):
            move_wbs_node(child2, new_parent_id=child1.id, position='right')
        with pytest.raises(Exception):
            move_wbs_node(child2, new_parent_id=child1.id, position='left')
        with pytest.raises(Exception):
            move_wbs_node(child2, new_parent_id=child1.id, position='first_child')
        with pytest.raises(Exception):
            move_wbs_node(child2, new_parent_id=child1.id, position='last_child')

    def test_max_depth_exceeded(self, project):
        project.max_depth = 2
        project.save()

        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        child1, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child 1')

        with pytest.raises(WBSValidationError, match="exceeds project maximum"):
            create_wbs_node(project_id=project.id, parent_id=child1.id, wbs_code='1.1.1', wbs_name='Child 1.1')

    def test_move_wbs_node_right_raises_when_no_parent(self, project):
        root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        child1, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child 1')
        child2, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.2', wbs_name='Child 2')

        with pytest.raises(WBSValidationError, match="new_parent_id is required for sibling positioning."):
            move_wbs_node(child2, new_parent_id=None, position='right')
        with pytest.raises(WBSValidationError, match="new_parent_id is required for sorted_child position."):
            move_wbs_node(child2, new_parent_id=None, position='sorted_child')
        with pytest.raises(WBSValidationError, match="new_parent_id is required for last_child position."):
            move_wbs_node(child2, new_parent_id=None, position='last_child')
