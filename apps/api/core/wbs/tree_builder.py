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
    Builds a fully nested, hierarchical JSON representation of the WBS tree
    for a specific project. It uses django-treebeard's get_annotated_list_qs
    to fetch the nodes iteratively without recursive database calls, ensuring optimal performance.
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
        keys_to_delete = []
        for k in parents.keys():
            if k > level:
                keys_to_delete.append(k)
        for stale in keys_to_delete:
            del parents[stale]

    return roots
