"""WBS tree operations using django-treebeard."""
from decimal import Decimal

from django.db import transaction

from projects.models import Activity, Project, WBS


class WBSConflictError(Exception):
    pass


class WBSValidationError(Exception):
    pass


def get_project_roots(project_id):
    """
    Retrieves all root nodes (depth=1) of the WBS tree for a specific project.
    Root nodes have no parent and represent the highest level of the breakdown structure.
    """
    return WBS.get_root_nodes().filter(project_id=project_id)


def _sibling_weight_sum(parent, field: str) -> Decimal:
    """
    Calculates the total sum of a specific weight field (physical or financial)
    across all sibling nodes under a given parent.
    If parent is None, it calculates the sum across all root nodes in the project.
    """
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
    """
    Validates that the sum of weights (both physical and financial) for a group
    of sibling nodes does not exceed 1.0 (100%). Returns a list of warning messages if exceeded.
    This is used to warn users if their breakdown exceeds the parent's total allocation.
    """
    warnings = []
    if parent is None:
        siblings = list(get_project_roots(project_id))
    else:
        siblings = list(parent.get_children())

    total_physical = Decimal('0')
    total_financial = Decimal('0')

    for node in siblings:
        if node.weight_physical is not None:
            total_physical += node.weight_physical
        if node.weight_financial is not None:
            total_financial += node.weight_financial

    if total_physical > Decimal('1'):
        warnings.append(
            f'Sibling weight physical weights sum to {total_physical}, which exceeds 1.0.'
        )
    if total_financial > Decimal('1'):
        warnings.append(
            f'Sibling weight financial weights sum to {total_financial}, which exceeds 1.0.'
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
    """
    Creates a new WBS node within the tree hierarchy and attaches it to a project.
    Validates max depth constraints and returns any weight capacity warnings.
    If parent_id is provided, it's added as a child; otherwise, it's created as a root node.
    """
    wbs_code = wbs_code.strip()
    if WBS.objects.filter(project_id=project_id, wbs_code=wbs_code).exists():
        raise WBSValidationError('wbs_code must be unique within the project.')

    parent = None
    new_depth = 1
    if parent_id:
        parent = WBS.objects.get(pk=parent_id, project_id=project_id)
        new_depth = parent.depth + 1

    project = Project.objects.get(pk=project_id)
    if project.max_depth is not None and new_depth > project.max_depth:
        raise WBSValidationError(
            f'WBS depth {new_depth} exceeds project maximum of {project.max_depth}.'
        )

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

    propagate_project_wbs_codes(project_id)
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
    project_id = node.project_id
    node.delete()
    propagate_project_wbs_codes(project_id)


def propagate_project_wbs_codes(project_id) -> None:
    """
    Recomputes and normalizes the hierarchical wbs_code (e.g., 1, 1.1, 1.1.2) for all nodes
    in a project based on their structural tree order (path).
    This is typically called after nodes are moved or structurally modified.
    """
    # ⚡ Bolt: Iterative single-query traversal instead of recursive N+1 query pattern
    qs = WBS.objects.filter(project_id=project_id).order_by('path')

    annotated = WBS.get_annotated_list_qs(qs)

    level_counters = {}
    level_codes = {}
    updates = []

    for node, info in annotated:
        depth = info['level'] + 1

        if depth not in level_counters:
            level_counters[depth] = 1
        else:
            level_counters[depth] += 1

        keys_to_delete = [k for k in level_counters.keys() if k > depth]
        for k in keys_to_delete:
            del level_counters[k]

        counter = level_counters[depth]

        if depth == 1:
            code = str(counter)
        else:
            parent_code = level_codes.get(depth - 1, "")
            code = f"{parent_code}.{counter}"

        level_codes[depth] = code

        if node.wbs_code != code:
            node.wbs_code = code
            updates.append(node)

    if updates:
        # ⚡ Bolt: Bulk update efficiently updates DB in a single roundtrip
        WBS.objects.bulk_update(updates, ['wbs_code'], batch_size=1000)


@transaction.atomic
def move_wbs_node(node: WBS, new_parent_id, position: str) -> WBS:
    """
    Moves an existing WBS node to a new location in the tree hierarchy using django-treebeard's move logic.
    Supports positions like 'first-child', 'last-child', 'left' (sibling), and 'right' (sibling).
    Automatically triggers a full recomputation of WBS codes for the project afterwards.
    """
    target_parent = None
    if new_parent_id:
        target_parent = WBS.objects.get(pk=new_parent_id, project_id=node.project_id)

    pos = position.replace('-', '_')
    # treebeard requires sorted-* positions when node_order_by is set on the model.
    if pos == 'first_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for first_child position.')
        node.move(target_parent, pos='sorted-child')
    elif pos == 'sorted_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for sorted_child position.')
        node.move(target_parent, pos='sorted-child')
    elif pos == 'last_child':
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for last_child position.')
        node.move(target_parent, pos='sorted-child')
    elif pos in ('left', 'right'):
        if target_parent is None:
            raise WBSValidationError('new_parent_id is required for sibling positioning.')
        node.move(target_parent, pos='sorted-sibling')
    else:
        raise WBSValidationError(f'Invalid position: {position}')

    propagate_project_wbs_codes(node.project_id)
    return WBS.objects.get(pk=node.pk)


def build_tree_queryset(project_id):
    return WBS.objects.filter(project_id=project_id).order_by('path')
