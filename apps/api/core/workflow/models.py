from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, TimeStampedModel, UUIDModel


class ExecutionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In progress'
    DONE = 'done', 'Done'
    CANCELLED = 'cancelled', 'Cancelled'


class WorkflowType(models.TextChoices):
    PURCHASE_REQUEST = 'purchase_request', 'Purchase request'
    IPC_APPROVAL = 'ipc_approval', 'IPC approval'
    PAYMENT_APPROVAL = 'payment_approval', 'Payment approval'
    BUDGET_CHANGE = 'budget_change', 'Budget change'
    SCHEDULE_CHANGE = 'schedule_change', 'Schedule change'
    INSPECTION_APPROVAL = 'inspection_approval', 'Inspection approval'
    CUSTOM = 'custom', 'Custom'


class WorkflowDefinitionStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    RETIRED = 'retired', 'Retired'


class ApprovalMode(models.TextChoices):
    ALL = 'all', 'All'
    ANY = 'any', 'Any'


class OnReject(models.TextChoices):
    STOP = 'stop', 'Stop'
    RETURN_PREVIOUS = 'return_previous', 'Return previous'
    RETURN_TO = 'return_to', 'Return to'


class WorkflowInstanceStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In progress'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    RETURNED = 'returned', 'Returned'
    CANCELLED = 'cancelled', 'Cancelled'


class WorkflowAction(models.TextChoices):
    START = 'start', 'Start'
    APPROVE = 'approve', 'Approve'
    REJECT = 'reject', 'Reject'
    RETURN = 'return', 'Return'
    CANCEL = 'cancel', 'Cancel'
    COMMENT = 'comment', 'Comment'


class StageAssignmentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class WorkflowDefinition(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='workflow_definitions',
    )
    name = models.CharField(max_length=200)
    workflow_type = models.CharField(max_length=40, choices=WorkflowType.choices)
    status = models.CharField(
        max_length=20,
        choices=WorkflowDefinitionStatus.choices,
        default=WorkflowDefinitionStatus.DRAFT,
    )
    description = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'workflow_definitions'
        ordering = ['name']


class WorkflowStage(models.Model):
    id = models.BigAutoField(primary_key=True)
    definition = models.ForeignKey(
        WorkflowDefinition, on_delete=models.CASCADE, related_name='stages',
    )
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    approver_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_stages_as_approver',
    )
    approver_role = models.CharField(max_length=60, blank=True, default='')
    approval_mode = models.CharField(
        max_length=10, choices=ApprovalMode.choices, default=ApprovalMode.ANY,
    )
    on_reject = models.CharField(
        max_length=20, choices=OnReject.choices, default=OnReject.STOP,
    )
    return_to_order = models.PositiveIntegerField(null=True, blank=True)
    deadline_days = models.PositiveIntegerField(null=True, blank=True)
    notify_on_enter = models.BooleanField(default=True)

    class Meta:
        db_table = 'workflow_stages'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['definition', 'order'], name='uniq_stage_order_per_def'),
        ]


class WorkflowInstance(AuditSoftDeleteModel):
    definition = models.ForeignKey(
        WorkflowDefinition, on_delete=models.PROTECT, related_name='instances',
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='workflow_instances',
    )
    subject_type = models.CharField(max_length=60)
    subject_id = models.UUIDField()
    status = models.CharField(
        max_length=20,
        choices=WorkflowInstanceStatus.choices,
        default=WorkflowInstanceStatus.PENDING,
    )
    current_stage_order = models.PositiveIntegerField(null=True, blank=True)
    current_due_at = models.DateTimeField(null=True, blank=True)
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='started_workflow_instances',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'workflow_instances'
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['subject_type', 'subject_id']),
        ]


class WorkflowStageAssignment(UUIDModel, TimeStampedModel):
    instance = models.ForeignKey(
        WorkflowInstance, on_delete=models.CASCADE, related_name='stage_assignments',
    )
    stage_order = models.PositiveIntegerField()
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workflow_stage_assignments',
    )
    status = models.CharField(
        max_length=20,
        choices=StageAssignmentStatus.choices,
        default=StageAssignmentStatus.PENDING,
    )

    class Meta:
        db_table = 'workflow_stage_assignments'
        constraints = [
            models.UniqueConstraint(
                fields=['instance', 'stage_order', 'assignee'],
                name='uniq_instance_stage_assignee',
            ),
        ]


class WorkflowActionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    instance = models.ForeignKey(
        WorkflowInstance, on_delete=models.CASCADE, related_name='action_logs',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='workflow_action_logs',
    )
    acted_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=WorkflowAction.choices)
    from_status = models.CharField(max_length=20, blank=True, default='')
    to_status = models.CharField(max_length=20, blank=True, default='')
    stage_order = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'workflow_action_logs'
        ordering = ['acted_at', 'id']


class ManagementDecision(AuditSoftDeleteModel):
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='management_decisions',
    )
    subject = models.TextField()
    options = models.TextField()
    criteria = models.TextField()
    proposer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='proposed_decisions',
    )
    approvers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='decisions_to_approve',
    )
    final_decision = models.TextField(blank=True, default='')
    execution_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_decisions',
    )
    due_date = models.DateField(null=True, blank=True)
    rationale = models.TextField()
    attachment_refs = models.JSONField(default=list, blank=True)
    impact_schedule = models.BooleanField(default=False)
    impact_cost = models.BooleanField(default=False)
    impact_contract = models.BooleanField(default=False)
    impact_risk = models.BooleanField(default=False)
    execution_status = models.CharField(
        max_length=20,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING,
    )
    related_risk = models.ForeignKey(
        'risk.RiskEvent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='management_decisions',
    )
    related_activity = models.ForeignKey(
        'projects.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='management_decisions',
    )
    related_contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='management_decisions',
    )
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='management_decisions',
    )

    class Meta:
        db_table = 'management_decisions'
