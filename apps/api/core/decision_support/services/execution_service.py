"""Validate → execute method → append immutable DecisionRun."""

from __future__ import annotations

import copy

from django.db import transaction
from django.shortcuts import get_object_or_404

from django.utils import timezone
from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError

from decision_support.models import CRITERIA_METHODS, METHOD_IDS, RANKING_METHODS, DecisionCase, DecisionRun
from decision_support.services.ahp_service import compute_ahp
from decision_support.services.ism_service import compute_ism
from decision_support.services.saw_service import compute_saw
from decision_support.services.topsis_service import compute_topsis
from decision_support.services.validators import _issue, raise_issues, validate_criteria_only, validate_ranking_inputs


def _snapshot_from_case(case: DecisionCase, *, weights_normalized: list[float] | None = None) -> dict:
    snap = {
        'title': case.title,
        'criteria': case.criteria or [],
        'alternatives': case.alternatives or [],
        'weights': case.weights or [],
        'types': case.types or [],
        'performance_matrix': case.performance_matrix or [],
        'ahp_matrix': case.ahp_matrix or [],
        'dematel_matrix': case.dematel_matrix or [],
        'ism_matrix': case.ism_matrix,
        'selected_methods': case.selected_methods or [],
    }
    if weights_normalized is not None:
        snap['weights_normalized'] = weights_normalized
    return copy.deepcopy(snap)


@transaction.atomic
def create_run(case: DecisionCase, method: str, user) -> DecisionRun:
    """Lock authoritative persisted input, then append one independent frozen run."""
    case = get_object_or_404(DecisionCase.objects.select_for_update(), pk=case.pk, project_id=case.project_id)
    method = (method or '').strip()
    if method not in METHOD_IDS:
        raise_issues([
            _issue('invalid_method', 'method', _('Unknown method id: %(method)s.') % {'method': repr(method)}),
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

    if method == 'saw':
        saw_out = compute_saw(
            case.criteria or [],
            case.alternatives or [],
            case.weights or [],
            case.types or [],
            case.performance_matrix or [],
        )
        snapshot = _snapshot_from_case(case, weights_normalized=saw_out['weights_normalized'])
        result = {
            'status': 'ok',
            'engine': 'saw',
            'ranking': saw_out['ranking'],
        }
    elif method == 'topsis':
        topsis_out = compute_topsis(
            case.criteria or [],
            case.alternatives or [],
            case.weights or [],
            case.types or [],
            case.performance_matrix or [],
        )
        snapshot = _snapshot_from_case(case, weights_normalized=topsis_out['weights_normalized'])
        result = {
            'status': 'ok',
            'engine': 'topsis',
            'ranking': topsis_out['ranking'],
        }
    elif method == 'ahp':
        ahp_out = compute_ahp(
            case.criteria or [],
            case.ahp_matrix or [],
        )
        snapshot = _snapshot_from_case(case)
        result = {
            'status': 'ok',
            'engine': 'ahp',
            'weights': ahp_out['weights'],
            'lambda_max': ahp_out['lambda_max'],
            'ci': ahp_out['ci'],
            'cr': ahp_out['cr'],
            'is_consistent': ahp_out['is_consistent'],
        }
    elif method == 'ism':
        output = compute_ism(case.criteria, case.ism_matrix)
        snapshot = _snapshot_from_case(case)
        result = {'status': 'ok', 'engine': 'ism', **output}
    elif method in RANKING_METHODS:
        # future ranking methods — Phase 1 stub until their engine phases
        validate_ranking_inputs(
            case.criteria or [],
            case.alternatives or [],
            case.weights or [],
            case.types or [],
            case.performance_matrix or [],
        )
        snapshot = _snapshot_from_case(case)
        result = {'status': 'stub', 'engine': None}
    elif method in CRITERIA_METHODS:
        validate_criteria_only(case.criteria or [])
        snapshot = _snapshot_from_case(case)
        result = {'status': 'stub', 'engine': None}
    else:
        raise_issues([_issue('invalid_method', 'method', _('Unknown method id: %(method)s.') % {'method': repr(method)})])

    return DecisionRun.objects.create(
        case=case,
        project_id=case.project_id,
        method=method,
        input_snapshot=snapshot,
        result=copy.deepcopy(result),
        extracted_at=timezone.now(),
        extracted_by=user,
    )


# Back-compat alias for any remaining imports
create_stub_run = create_run
