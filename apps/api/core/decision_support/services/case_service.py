"""Create/update decision cases."""

from __future__ import annotations

import copy
from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import JSONField, Value

from decision_support.models import DecisionCase
from decision_support.services.validators import (
    raise_issues,
    validate_method_ids,
    validate_names,
    validate_ranking_inputs,
    validate_ahp_draft_numbers,
    validate_ism_draft_numbers,
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
        'ism_matrix': copy.deepcopy(case.ism_matrix),
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
        out[key] = val if key == 'ism_matrix' or val is not None else []

    validate_ahp_draft_numbers(out["ahp_matrix"])
    validate_ism_draft_numbers(out['ism_matrix'])

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
    # JSON null is a recoverable malformed draft, distinct from SQL NULL.
    if fields['ism_matrix'] is None:
        fields['ism_matrix'] = Value(None, output_field=JSONField())
    case = DecisionCase.objects.create(
        project_id=project_id,
        created_by=user,
        updated_by=user,
        **fields,
    )
    case.refresh_from_db()
    return case


@transaction.atomic
def update_case(case: DecisionCase, user, data: dict[str, Any]) -> DecisionCase:
    caller = case
    case = get_object_or_404(DecisionCase.objects.select_for_update(), pk=case.pk, project_id=case.project_id)
    allowed = {'title', *CASE_JSON_FIELDS}
    changes = {key: value for key, value in data.items() if key in allowed}
    # Pairwise draft saves must not normalize/revalidate unrelated ranking drafts.
    if set(changes) <= {'ahp_matrix'} or set(changes) <= {'ism_matrix'}:
        if 'ahp_matrix' in changes:
            validate_ahp_draft_numbers(changes['ahp_matrix'])
        if 'ism_matrix' in changes:
            validate_ism_draft_numbers(changes['ism_matrix'])
        fields = changes
    else:
        case.refresh_from_db()
        merged = {**_case_dict(case), **changes}
        normalized = _normalize_case_fields(merged)
        fields = {key: normalized[key] for key in changes}
    for key, value in fields.items():
        if key == 'ism_matrix' and value is None:
            value = Value(None, output_field=JSONField())
        setattr(case, key, value)
    case.updated_by = user
    case.save(update_fields=[*fields, 'updated_by', 'updated_at'])
    caller.refresh_from_db()
    return caller
