"""Workflow instance transitions and action log."""

from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from config.exceptions import CodedValidationError
from master_data.models import MemberStatus, ProjectMember
from workflow.models import (
    ApprovalMode,
    OnReject,
    StageAssignmentStatus,
    WorkflowAction,
    WorkflowActionLog,
    WorkflowDefinitionStatus,
    WorkflowInstance,
    WorkflowInstanceStatus,
    WorkflowStage,
    WorkflowStageAssignment,
)

TERMINAL_STATUSES = frozenset({
    WorkflowInstanceStatus.APPROVED,
    WorkflowInstanceStatus.REJECTED,
    WorkflowInstanceStatus.CANCELLED,
})


def _append_log(
    instance: WorkflowInstance,
    *,
    actor,
    action: str,
    from_status: str,
    to_status: str,
    stage_order: int | None,
    comment: str = '',
) -> WorkflowActionLog:
    return WorkflowActionLog.objects.create(
        instance=instance,
        actor=actor,
        action=action,
        from_status=from_status or '',
        to_status=to_status or '',
        stage_order=stage_order,
        comment=comment or '',
    )


def _ordered_stages(definition) -> list[WorkflowStage]:
    return list(definition.stages.order_by('order'))


def _stage_by_order(definition, order: int | None) -> WorkflowStage | None:
    if order is None:
        return None
    return definition.stages.filter(order=order).first()


def _resolve_assignee_user_ids(stage: WorkflowStage, project_id) -> list:
    user_ids: list = []
    if stage.approver_user_id:
        user_ids.append(stage.approver_user_id)
    role_name = (stage.approver_role or '').strip()
    if role_name:
        members = (
            ProjectMember.objects.filter(project_id=project_id, status=MemberStatus.ACTIVE)
            .prefetch_related('member_roles__role')
        )
        for member in members:
            for mr in member.member_roles.all():
                if mr.role.role_name == role_name and member.user_id not in user_ids:
                    user_ids.append(member.user_id)
    return user_ids


def _sync_stage_assignments(instance: WorkflowInstance, stage_order: int) -> None:
    stage = _stage_by_order(instance.definition, stage_order)
    if stage is None:
        return
    WorkflowStageAssignment.objects.filter(
        instance=instance, stage_order=stage_order,
    ).delete()
    for uid in _resolve_assignee_user_ids(stage, instance.project_id):
        WorkflowStageAssignment.objects.create(
            instance=instance,
            stage_order=stage_order,
            assignee_id=uid,
            status=StageAssignmentStatus.PENDING,
        )


def _set_due_at(instance: WorkflowInstance, stage: WorkflowStage | None) -> None:
    if stage and stage.deadline_days:
        instance.current_due_at = timezone.now() + timedelta(days=stage.deadline_days)
    else:
        instance.current_due_at = None


def user_can_act_on_stage(instance: WorkflowInstance, user, stage_order: int | None) -> bool:
    if stage_order is None:
        return False
    stage = _stage_by_order(instance.definition, stage_order)
    if stage is None:
        return False
    if stage.approver_user_id == user.id:
        return True
    role_name = (stage.approver_role or '').strip()
    if not role_name:
        return False
    member = (
        ProjectMember.objects.filter(
            project_id=instance.project_id,
            user_id=user.id,
            status=MemberStatus.ACTIVE,
        )
        .prefetch_related('member_roles__role')
        .first()
    )
    if member is None:
        return False
    return any(mr.role.role_name == role_name for mr in member.member_roles.all())


def _ensure_can_act(instance: WorkflowInstance, user) -> WorkflowStage:
    if instance.status in TERMINAL_STATUSES:
        raise CodedValidationError(detail='Instance is already finished.', code='invalid_status')
    if instance.status not in (
        WorkflowInstanceStatus.IN_PROGRESS,
        WorkflowInstanceStatus.RETURNED,
    ):
        raise CodedValidationError(detail='Instance is not actionable.', code='invalid_status')
    stage = _stage_by_order(instance.definition, instance.current_stage_order)
    if stage is None:
        raise CodedValidationError(detail='No active stage.', code='invalid_status')
    if not user_can_act_on_stage(instance, user, instance.current_stage_order):
        raise CodedValidationError(detail='Not an approver for this stage.', code='not_approver')
    return stage


@transaction.atomic
def start_instance(
    *,
    definition,
    project_id,
    subject_type: str,
    subject_id,
    user,
    comment: str = '',
) -> WorkflowInstance:
    if definition.status != WorkflowDefinitionStatus.ACTIVE:
        raise CodedValidationError(detail='Definition must be active.', code='definition_not_active')
    if str(definition.project_id) != str(project_id):
        raise CodedValidationError(detail='Definition project mismatch.', code='validation_error')

    stages = _ordered_stages(definition)
    if not stages:
        raise CodedValidationError(detail='Definition has no stages.', code='incomplete_stages')

    now = timezone.now()
    first = stages[0]
    instance = WorkflowInstance.objects.create(
        definition=definition,
        project_id=project_id,
        subject_type=subject_type,
        subject_id=subject_id,
        status=WorkflowInstanceStatus.IN_PROGRESS,
        current_stage_order=first.order,
        started_by=user,
        started_at=now,
        created_by=user,
        updated_by=user,
    )
    _set_due_at(instance, first)
    instance.save(update_fields=['current_due_at'])
    _sync_stage_assignments(instance, first.order)

    _append_log(
        instance,
        actor=user,
        action=WorkflowAction.START,
        from_status=WorkflowInstanceStatus.PENDING,
        to_status=WorkflowInstanceStatus.IN_PROGRESS,
        stage_order=first.order,
        comment=comment,
    )
    return instance


def _advance_or_complete(instance: WorkflowInstance, user, comment: str = '') -> WorkflowInstance:
    stages = _ordered_stages(instance.definition)
    current_order = instance.current_stage_order
    from_status = instance.status

    idx = next((i for i, s in enumerate(stages) if s.order == current_order), None)
    if idx is None:
        raise CodedValidationError(detail='Invalid stage.', code='invalid_status')

    if idx + 1 >= len(stages):
        from permissions.sod import assert_not_self_final_approve

        creator_id = instance.started_by_id or instance.created_by_id
        assert_not_self_final_approve(creator_id, user)
        instance.status = WorkflowInstanceStatus.APPROVED
        instance.completed_at = timezone.now()
        instance.current_stage_order = current_order
        instance.current_due_at = None
        instance.updated_by = user
        instance.save(
            update_fields=[
                'status', 'completed_at', 'current_due_at', 'updated_by', 'updated_at',
            ],
        )
        _append_log(
            instance,
            actor=user,
            action=WorkflowAction.APPROVE,
            from_status=from_status,
            to_status=WorkflowInstanceStatus.APPROVED,
            stage_order=current_order,
            comment=comment,
        )
        return instance

    next_stage = stages[idx + 1]
    if instance.status == WorkflowInstanceStatus.RETURNED:
        instance.status = WorkflowInstanceStatus.IN_PROGRESS
    instance.current_stage_order = next_stage.order
    _set_due_at(instance, next_stage)
    instance.updated_by = user
    instance.save(
        update_fields=[
            'status', 'current_stage_order', 'current_due_at', 'updated_by', 'updated_at',
        ],
    )
    _sync_stage_assignments(instance, next_stage.order)
    _append_log(
        instance,
        actor=user,
        action=WorkflowAction.APPROVE,
        from_status=from_status,
        to_status=WorkflowInstanceStatus.IN_PROGRESS,
        stage_order=current_order,
        comment=comment,
    )
    return instance


@transaction.atomic
def approve_instance(instance: WorkflowInstance, user, comment: str = '') -> WorkflowInstance:
    stage = _ensure_can_act(instance, user)
    stage_order = instance.current_stage_order
    assert stage_order is not None

    if stage.approval_mode == ApprovalMode.ALL:
        assignment = WorkflowStageAssignment.objects.filter(
            instance=instance,
            stage_order=stage_order,
            assignee=user,
        ).first()
        if assignment is None:
            raise CodedValidationError(detail='Not assigned to this stage.', code='not_approver')
        assignment.status = StageAssignmentStatus.APPROVED
        assignment.save(update_fields=['status', 'updated_at'])
        pending = WorkflowStageAssignment.objects.filter(
            instance=instance,
            stage_order=stage_order,
            status=StageAssignmentStatus.PENDING,
        ).exists()
        if pending:
            instance.updated_by = user
            instance.save(update_fields=['updated_by', 'updated_at'])
            return instance

    return _advance_or_complete(instance, user, comment=comment)


@transaction.atomic
def reject_instance(instance: WorkflowInstance, user, comment: str = '') -> WorkflowInstance:
    stage = _ensure_can_act(instance, user)
    from_status = instance.status
    stage_order = instance.current_stage_order

    on_reject = stage.on_reject
    if on_reject == OnReject.STOP:
        instance.status = WorkflowInstanceStatus.REJECTED
        instance.completed_at = timezone.now()
        instance.current_due_at = None
        instance.updated_by = user
        instance.save(
            update_fields=['status', 'completed_at', 'current_due_at', 'updated_by', 'updated_at'],
        )
        _append_log(
            instance,
            actor=user,
            action=WorkflowAction.REJECT,
            from_status=from_status,
            to_status=WorkflowInstanceStatus.REJECTED,
            stage_order=stage_order,
            comment=comment,
        )
        return instance

    instance.status = WorkflowInstanceStatus.RETURNED
    target_order = stage_order
    if on_reject == OnReject.RETURN_PREVIOUS:
        stages = _ordered_stages(instance.definition)
        idx = next((i for i, s in enumerate(stages) if s.order == stage_order), 0)
        if idx > 0:
            target_order = stages[idx - 1].order
    elif on_reject == OnReject.RETURN_TO and stage.return_to_order:
        target_order = stage.return_to_order

    instance.current_stage_order = target_order
    target_stage = _stage_by_order(instance.definition, target_order)
    _set_due_at(instance, target_stage)
    instance.updated_by = user
    instance.save(
        update_fields=[
            'status', 'current_stage_order', 'current_due_at', 'updated_by', 'updated_at',
        ],
    )
    if target_order is not None:
        _sync_stage_assignments(instance, target_order)
    _append_log(
        instance,
        actor=user,
        action=WorkflowAction.REJECT,
        from_status=from_status,
        to_status=WorkflowInstanceStatus.RETURNED,
        stage_order=stage_order,
        comment=comment,
    )
    return instance


@transaction.atomic
def cancel_instance(instance: WorkflowInstance, user, comment: str = '') -> WorkflowInstance:
    if instance.status in TERMINAL_STATUSES:
        raise CodedValidationError(detail='Instance is already finished.', code='invalid_status')
    from_status = instance.status
    instance.status = WorkflowInstanceStatus.CANCELLED
    instance.completed_at = timezone.now()
    instance.current_due_at = None
    instance.updated_by = user
    instance.save(
        update_fields=['status', 'completed_at', 'current_due_at', 'updated_by', 'updated_at'],
    )
    _append_log(
        instance,
        actor=user,
        action=WorkflowAction.CANCEL,
        from_status=from_status,
        to_status=WorkflowInstanceStatus.CANCELLED,
        stage_order=instance.current_stage_order,
        comment=comment,
    )
    return instance
