"""WBS tree operations using django-treebeard."""
from decimal import Decimal

from django.db import transaction

from projects.models import Activity, WBS


class WBSConflictError(Exception):
    pass


class WBSValidationError(Exception):
    pass


def get_project_roots(project_id):
    return WBS.get_root_nodes().filter(project_id=project_id)


def _sibling_weight_sum(parent, field: str) -> Decimal:
    if parent is None:
        siblings = get_project_roots(parent.project_id if hasattr(parent, 'project_id') else parent)
    else:
        siblings = parent.get_children()

    total = Decimal('0')
    for node in siblings:
        val = getattr(node, field)
        if val is not None:
            total += val
    return total


def check_weight_warnings(parent, project_id, field: str = 'weight_physical') -> list[str]:
    warnings = []
    if parent is None:
        siblings = get_project_roots(project_id)
    else:
        siblings = parent.get_children()

    for weight_field in ('weight_physical', 'weight_financial'):
        total = Decimal('0')
        for node in siblings:
            val = getattr(node, weight_field)
            if val is not None:
                total += val
        if total > Decimal('1'):
            warnings.append(
                f'Sibling {weight_field.replace("_", " ")} weights sum to {total}, which exceeds 1.0.'
            )
    return warnings


@transaction.atomic
def create_wbs_node(
    *,
    project_id,
    parent_id=None,
    wbs_code: str,
    wbs_name: str,
    weight_physical=None,
    weight_financial=None,
    description: str = '',
) -> tuple[WBS, list[str]]:
    wbs_code = wbs_code.strip()
    if WBS.objects.filter(project_id=project_id, wbs_code=wbs_code).exists():
        raise WBSValidationError('wbs_code must be unique within the project.')

    parent = None
    if parent_id:
        parent = WBS.objects.get(pk=parent_id, project_id=project_id)

    if parent:
        node = parent.add_child(
            project_id=project_id,
            wbs_code=wbs_code,
            wbs_name=wbs_name,
            weight_physical=weight_physical,
            weight_financial=weight_financial,
            description=description,
        )
        warnings = check_weight_warnings(parent, project_id)
    else:
        node = WBS.add_root(
            project_id=project_id,
            wbs_code=wbs_code,
            wbs_name=wbs_name,
            weight_physical=weight_physical,
            weight_financial=weight_financial,
            description=description,
        )
        warnings = check_weight_warnings(None, project_id)

    return node, warnings


@transaction.atomic
def update_wbs_node(node: WBS, **fields) -> tuple[WBS, list[str]]:
    for key, value in fields.items():
        if value is not None or key in ('weight_physical', 'weight_financial'):
            setattr(node, key, value)
    node.save()
    parent = node.get_parent()
    warnings = check_weight_warnings(parent, node.project_id)
    return node, warnings


@transaction.atomic
def delete_wbs_node(node: WBS) -> None:
    if node.numchild > 0:
        raise WBSConflictError('Cannot delete a WBS node that has children.')
    if Activity.objects.filter(wbs=node).exists():
        raise WBSConflictError('Cannot delete a WBS node that has activities attached.')
    node.delete()


@transaction.atomic
def move_wbs_node(node: WBS, new_parent_id, position: str) -> WBS:
    target_parent = None
    if new_parent_id:
        target_parent = WBS.objects.get(pk=new_parent_id, project_id=node.project_id)

    pos = position.replace('-', '_')
    if pos == 'first_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for first_child position.')
        node.move(target_parent, pos='first-child')
    elif pos == 'sorted_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for sorted_child position.')
        node.move(target_parent, pos='sorted-child')
    elif pos == 'last_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for last_child position.')
        node.move(target_parent, pos='last-child')
    elif pos in ('left', 'right'):
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for sibling positioning.')
        node.move(target_parent, pos=pos)
    else:
        raise WBSValidationError(f'Invalid position: {position}')

    return WBS.objects.get(pk=node.pk)


def build_tree_queryset(project_id):
    return WBS.objects.filter(project_id=project_id).order_by('path')
