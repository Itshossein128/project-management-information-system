"""DFS cycle detection for activity predecessor/successor graphs."""

from uuid import UUID

from projects.models import ActivityRelation

CYCLE_ERROR_MESSAGE = 'این ارتباط باعث ایجاد حلقه در شبکه فعالیت‌ها می‌شود'


def _build_adjacency(project_id) -> dict[UUID, list[UUID]]:
    """Map activity id -> list of successor ids (edges predecessor -> successor)."""
    adj: dict[UUID, list[UUID]] = {}
    relations = ActivityRelation.objects.filter(
        predecessor__project_id=project_id,
        successor__project_id=project_id,
    ).values_list('predecessor_id', 'successor_id')
    for pred_id, succ_id in relations:
        adj.setdefault(pred_id, []).append(succ_id)
        adj.setdefault(succ_id, adj.get(succ_id, []))
    return adj


def would_create_cycle(
    project_id,
    predecessor_id: UUID,
    successor_id: UUID,
    *,
    exclude_relation_id: UUID | None = None,
) -> bool:
    """
    Return True if adding edge predecessor -> successor creates a cycle.
    DFS from successor following successor edges; if predecessor is reachable, cycle exists.
    """
    if predecessor_id == successor_id:
        return True

    adj = _build_adjacency(project_id)
    if exclude_relation_id:
        rel = ActivityRelation.all_objects.filter(pk=exclude_relation_id).first()
        if rel:
            succs = adj.get(rel.predecessor_id, [])
            if rel.successor_id in succs:
                succs = [s for s in succs if s != rel.successor_id]
                adj[rel.predecessor_id] = succs

    adj.setdefault(predecessor_id, adj.get(predecessor_id, []))
    if successor_id not in adj[predecessor_id]:
        adj[predecessor_id] = [*adj[predecessor_id], successor_id]

    stack = [successor_id]
    visited: set[UUID] = set()
    while stack:
        node = stack.pop()
        if node == predecessor_id:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(adj.get(node, []))
    return False
