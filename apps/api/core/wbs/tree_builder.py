"""Iterative WBS tree serialization — no recursive Python calls."""

from __future__ import annotations

from projects.models import WBS


def node_to_dict(node: WBS) -> dict:
    return {
        'wbs_id': str(node.id),
        'wbs_code': node.wbs_code,
        'wbs_name': node.wbs_name,
        'weight_physical': node.weight_physical,
        'weight_financial': node.weight_financial,
        'description': node.description,
        'depth': node.depth,
        'children': [],
    }


def build_nested_wbs_tree(project_id) -> list[dict]:
    """
    Build nested WBS JSON using treebeard's annotated list (iterative, any depth).
    """
    qs = WBS.objects.filter(project_id=project_id)
    if not qs.exists():
        return []

    tree_qs = qs.order_by("path")
    annotated = WBS.get_annotated_list_qs(tree_qs)

    roots: list[dict] = []
    # parents[level] -> most recent node dict at that outline level (0-based)
    parents: dict[int, dict] = {}

    for node, info in annotated:
        level = info['level']
        item = node_to_dict(node)

        if level == 0:
            roots.append(item)
        else:
            parent = parents.get(level - 1)
            if parent is not None:
                parent['children'].append(item)

        parents[level] = item
        # Drop deeper stale parents when going back up the tree
        for stale in [k for k in parents if k > level]:
            del parents[stale]

    return roots
