"""Freeze snapshot and append immutable stub runs (Phase 1 — no engines)."""

from __future__ import annotations

import copy

from django.utils import timezone

from config.exceptions import CodedValidationError

from decision_support.models import CRITERIA_METHODS, METHOD_IDS, RANKING_METHODS, DecisionCase, DecisionRun
from decision_support.services.validators import raise_issues, validate_criteria_only, validate_ranking_inputs, _issue


def _snapshot_from_case(case: DecisionCase) -> dict:
    return copy.deepcopy(
        {
            'title': case.title,
            'criteria': case.criteria or [],
            'alternatives': case.alternatives or [],
            'weights': case.weights or [],
            'types': case.types or [],
            'performance_matrix': case.performance_matrix or [],
            'ahp_matrix': case.ahp_matrix or [],
            'dematel_matrix': case.dematel_matrix or [],
            'ism_matrix': case.ism_matrix or [],
            'selected_methods': case.selected_methods or [],
        },
    )


def create_stub_run(case: DecisionCase, method: str, user) -> DecisionRun:
    method = (method or '').strip()
    if method not in METHOD_IDS:
        raise_issues([
            _issue('invalid_method', 'method', f'Unknown method id: {method!r}.'),
        ])

    selected = list(case.selected_methods or [])
    if method not in selected:
        raise CodedValidationError(
            detail={
                'issues': [
                    _issue(
                        'method_not_selected',
                        'method',
                        'Method is not selected on this case.',
                    ),
                ],
            },
            code='method_not_selected',
        )

    if method in RANKING_METHODS:
        validate_ranking_inputs(
            case.criteria or [],
            case.alternatives or [],
            case.weights or [],
            case.types or [],
            case.performance_matrix or [],
        )
    elif method in CRITERIA_METHODS:
        validate_criteria_only(case.criteria or [])

    return DecisionRun.objects.create(
        case=case,
        project_id=case.project_id,
        method=method,
        input_snapshot=_snapshot_from_case(case),
        result={'status': 'stub', 'engine': None},
        extracted_at=timezone.now(),
        extracted_by=user,
    )
