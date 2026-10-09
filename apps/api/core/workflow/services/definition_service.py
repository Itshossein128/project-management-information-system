"""Workflow definition lifecycle."""

from __future__ import annotations

from django.db import transaction

from config.exceptions import CodedValidationError
from workflow.models import WorkflowDefinition, WorkflowDefinitionStatus, WorkflowStage


def stage_has_approver(stage: WorkflowStage) -> bool:
    if stage.approver_user_id:
        return True
    return bool(stage.approver_role and str(stage.approver_role).strip())


def validate_stages_complete(definition: WorkflowDefinition) -> None:
    stages = list(definition.stages.order_by('order'))
    if not stages:
        raise CodedValidationError(detail='Definition has no stages.', code='incomplete_stages')
    for stage in stages:
        if not stage_has_approver(stage):
            raise CodedValidationError(
                detail='Every stage must have approver_user or approver_role.',
                code='incomplete_stages',
            )


@transaction.atomic
def activate_definition(definition: WorkflowDefinition, user) -> WorkflowDefinition:
    if definition.status == WorkflowDefinitionStatus.RETIRED:
        raise CodedValidationError(detail='Cannot activate a retired definition.', code='invalid_status')
    validate_stages_complete(definition)
    definition.status = WorkflowDefinitionStatus.ACTIVE
    definition.updated_by = user
    definition.save(update_fields=['status', 'updated_by', 'updated_at'])
    return definition


@transaction.atomic
def retire_definition(definition: WorkflowDefinition, user) -> WorkflowDefinition:
    definition.status = WorkflowDefinitionStatus.RETIRED
    definition.updated_by = user
    definition.save(update_fields=['status', 'updated_by', 'updated_at'])
    return definition


@transaction.atomic
def replace_stages(definition: WorkflowDefinition, stages_data: list[dict]) -> WorkflowDefinition:
    definition.stages.all().delete()
    for row in stages_data:
        approver = row.get('approver_user')
        approver_user_id = approver.id if hasattr(approver, 'id') else approver
        WorkflowStage.objects.create(
            definition=definition,
            order=row['order'],
            name=row['name'],
            approver_user_id=approver_user_id,
            approver_role=row.get('approver_role') or '',
            approval_mode=row.get('approval_mode', 'any'),
            on_reject=row.get('on_reject', 'stop'),
            return_to_order=row.get('return_to_order'),
            deadline_days=row.get('deadline_days'),
            notify_on_enter=row.get('notify_on_enter', True),
        )
    return definition
