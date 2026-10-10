"""Create/update decision cases."""

from __future__ import annotations

from typing import Any

from decision_support.models import DecisionCase
from decision_support.services.validators import (
    raise_issues,
    validate_method_ids,
    validate_names,
    validate_ranking_inputs,
    _issue,
)


CASE_JSON_FIELDS = (
    'selected_methods',
    'criteria',
    'alternatives',
    'weights',
    'types',
    'performance_matrix',
    'ahp_matrix',
    'dematel_matrix',
    'ism_matrix',
)


def _ranking_payload_present(data: dict[str, Any]) -> bool:
    """Full ranking validation when a performance matrix is supplied (non-empty)."""
    matrix = data.get('performance_matrix')
    return isinstance(matrix, list) and len(matrix) > 0



def _case_dict(case: DecisionCase) -> dict[str, Any]:
    return {
        'title': case.title,
        'selected_methods': list(case.selected_methods or []),
        'criteria': list(case.criteria or []),
        'alternatives': list(case.alternatives or []),
        'weights': list(case.weights or []),
        'types': list(case.types or []),
        'performance_matrix': list(case.performance_matrix or []),
        'ahp_matrix': list(case.ahp_matrix or []),
        'dematel_matrix': list(case.dematel_matrix or []),
        'ism_matrix': list(case.ism_matrix or []),
    }


def _normalize_case_fields(data: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    title = data.get('title', '')
    title = title.strip() if isinstance(title, str) else str(title or '').strip()
    if not title:
        raise_issues([_issue('name_empty', 'title', 'Title cannot be empty.')])
    if len(title) > 200:
        raise_issues([_issue('invalid_type', 'title', 'Title max length is 200.')])
    out['title'] = title

    out['selected_methods'] = validate_method_ids(data.get('selected_methods') or [])
    out['criteria'] = validate_names(data.get('criteria') or [], 'criteria', require_non_empty=False)
    out['alternatives'] = validate_names(
        data.get('alternatives') or [],
        'alternatives',
        require_non_empty=False,
    )

    for key in ('weights', 'types', 'performance_matrix', 'ahp_matrix', 'dematel_matrix', 'ism_matrix'):
        val = data.get(key)
        out[key] = val if val is not None else []

    if _ranking_payload_present(out):
        validated = validate_ranking_inputs(
            out['criteria'],
            out['alternatives'],
            out['weights'],
            out['types'],
            out['performance_matrix'],
        )
        out['criteria'] = validated['criteria']
        out['alternatives'] = validated['alternatives']
        out['weights'] = validated['weights']
        out['types'] = validated['types']
        out['performance_matrix'] = validated['performance_matrix']

    return out


def create_case(project_id, user, data: dict[str, Any]) -> DecisionCase:
    payload = {key: data.get(key, [] if key != 'title' else '') for key in ('title', *CASE_JSON_FIELDS)}
    for key in CASE_JSON_FIELDS:
        if key not in data:
            payload[key] = []
    if 'title' in data:
        payload['title'] = data['title']
    fields = _normalize_case_fields(payload)
    return DecisionCase.objects.create(
        project_id=project_id,
        created_by=user,
        updated_by=user,
        **fields,
    )


def update_case(case: DecisionCase, user, data: dict[str, Any]) -> DecisionCase:
    merged = _case_dict(case)
    for key, value in data.items():
        if key in merged or key == 'title':
            merged[key] = value
    fields = _normalize_case_fields(merged)
    for key, value in fields.items():
        setattr(case, key, value)
    case.updated_by = user
    case.save()
    return case
