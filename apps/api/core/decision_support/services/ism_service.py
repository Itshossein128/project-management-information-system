"""Pure independent binary ISM; no database or HTTP dependencies."""
from decision_support.services.validators import validate_ism_inputs, raise_issues, _issue

DERIVATION_POLICY = {
    'version': 'ism-v1', 'self_inclusion': 'binary_or', 'closure': 'transitive',
    'layer_rule': 'reach_equals_intersection', 'layer_order': 'top_to_bottom',
    'mutual_groups': 'maximal_non_singleton',
}


def _extract_layers(names, reach):
    active = set(range(len(names)))
    layers = []
    while active:
        members = []
        for i in sorted(active):
            reachable = {j for j in active if reach[i][j]}
            antecedent = {j for j in active if reach[j][i]}
            if reachable == reachable & antecedent:
                members.append(i)
        if not members or len(layers) >= len(names):
            raise_issues([_issue('ism_derivation_failed', 'ism_matrix', 'Structural analysis could not be completed.')])
        layers.append(members)
        active.difference_update(members)
    return layers


def compute_ism(criteria, matrix):
    data = validate_ism_inputs(criteria, matrix)
    names = data['criteria']
    n = len(names)
    reach = [row[:] for row in data['ism_matrix']]
    for i in range(n):
        reach[i][i] = 1
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = int(reach[i][j] or (reach[i][k] and reach[k][j]))
    indices = _extract_layers(names, reach)
    levels = {index: level for level, members in enumerate(indices, 1) for index in members}
    remaining = set(range(n))
    groups = []
    while remaining:
        first = min(remaining)
        members = [j for j in sorted(remaining) if reach[first][j] and reach[j][first]]
        if not members or any(levels[j] != levels[first] for j in members):
            raise_issues([_issue('ism_derivation_failed', 'ism_matrix', 'Structural analysis could not be completed.')])
        remaining.difference_update(members)
        if len(members) > 1:
            groups.append((levels[first], first, members))
    return {
        'reachability_matrix': reach,
        'layers': [{'level': level, 'criteria': [names[i] for i in members]} for level, members in enumerate(indices, 1)],
        'mutual_groups': [{'level': level, 'criteria': [names[i] for i in members]} for level, _, members in sorted(groups)],
        'derivation_policy': dict(DERIVATION_POLICY),
    }
