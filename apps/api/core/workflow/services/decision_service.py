"""Management decision validation and persistence helpers."""

from __future__ import annotations

from config.exceptions import CodedValidationError
from workflow.models import ManagementDecision


def validate_rationale(value: str | None) -> str:
    if value is None or not str(value).strip():
        raise CodedValidationError(detail='Rationale is required.', code='rationale_required')
    return str(value).strip()


def validate_execution_owner(value) -> None:
    if not value:
        raise CodedValidationError(detail='Execution owner is required.', code='execution_owner_required')


def validate_same_project_links(project_id, related_risk=None, related_activity=None, related_contract=None):
    if related_risk is not None and str(related_risk.project_id) != str(project_id):
        raise CodedValidationError(
            detail='Related risk must belong to the same project.',
            code='cross_project_link',
        )
    if related_activity is not None and str(related_activity.project_id) != str(project_id):
        raise CodedValidationError(
            detail='Related activity must belong to the same project.',
            code='cross_project_link',
        )
    if related_contract is not None and str(related_contract.project_id) != str(project_id):
        raise CodedValidationError(
            detail='Related contract must belong to the same project.',
            code='cross_project_link',
        )


def apply_decision_create(*, project_id, data: dict) -> dict:
    data = dict(data)
    data['rationale'] = validate_rationale(data.get('rationale'))
    validate_execution_owner(data.get('execution_owner'))
    validate_same_project_links(
        project_id,
        related_risk=data.get('related_risk'),
        related_activity=data.get('related_activity'),
        related_contract=data.get('related_contract'),
    )
    return data


def apply_decision_update(instance: ManagementDecision, data: dict) -> dict:
    data = dict(data)
    if 'rationale' in data:
        data['rationale'] = validate_rationale(data.get('rationale'))
    if 'execution_owner' in data:
        validate_execution_owner(data.get('execution_owner'))
    project_id = instance.project_id
    validate_same_project_links(
        project_id,
        related_risk=data.get('related_risk', instance.related_risk),
        related_activity=data.get('related_activity', instance.related_activity),
        related_contract=data.get('related_contract', instance.related_contract),
    )
    return data
