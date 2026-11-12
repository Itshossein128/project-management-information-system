"""Regression coverage for mutable display codes in a multi-project WBS forest."""
import pytest

from projects.models import Project, WBS
from wbs.services import move_wbs_node


def _root(project, code):
    return WBS.add_root(project=project, wbs_code=code, wbs_name=code)


@pytest.mark.django_db
def test_root_after_soft_deleted_root_in_another_project(project):
    """Equal codes are valid across projects; a tombstone must not break insertion."""
    projects = [project]
    for i in range(3):
        projects.append(Project.objects.create(
            project_code=f'TREE-ORDER-{i}', project_name=f'Tree order {i}',
            employer='Test', start_date='2026-01-01',
        ))
    first, deleted, last = [_root(p, '1') for p in projects[:3]]
    deleted.soft_delete()
    paths = dict(WBS.objects.values_list('pk', 'path'))
    new = _root(projects[3], '1')
    assert new.path > last.path
    assert dict(WBS.objects.filter(pk__in=paths).values_list('pk', 'path')) == paths
    assert WBS.find_problems() == ([], [], [], [], [])


@pytest.mark.django_db
def test_children_keep_source_order_after_a_tombstone(project):
    root = _root(project, '1')
    children = [root.add_child(project=project, wbs_code=code, wbs_name=code) for code in ('1.1', '1.2', '1.3')]
    children[1].soft_delete()
    root.refresh_from_db()
    new = root.add_child(project=project, wbs_code='1.2', wbs_name='Replacement')
    assert list(root.get_children().values_list('pk', flat=True)) == [
        *(child.pk for child in children), new.pk,
    ]
    assert WBS.find_problems() == ([], [], [], [], [])


@pytest.mark.django_db
def test_explicit_first_child_move_controls_order_and_codes(project):
    root = _root(project, '1')
    children = [root.add_child(project=project, wbs_code=code, wbs_name=code) for code in ('1.1', '1.2', '1.3')]
    moved = move_wbs_node(children[2], new_parent_id=root.pk, position='first_child')
    assert moved.wbs_code == '1.1'
    assert list(root.get_children().values_list('pk', flat=True)) == [
        children[2].pk, children[0].pk, children[1].pk,
    ]
    assert WBS.find_problems() == ([], [], [], [], [])
