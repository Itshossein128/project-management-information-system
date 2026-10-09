from django.contrib.auth import get_user_model
from rest_framework import serializers

from config.exceptions import CodedValidationError
from workflow.models import (
    ManagementDecision,
    WorkflowActionLog,
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStage,
)
from workflow.services import decision_service


class WorkflowStageSerializer(serializers.ModelSerializer):
    approver_user = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        required=False,
        queryset=get_user_model().objects.all(),
    )

    class Meta:
        model = WorkflowStage
        fields = (
            'order',
            'name',
            'approver_user',
            'approver_role',
            'approval_mode',
            'on_reject',
            'return_to_order',
            'deadline_days',
            'notify_on_enter',
        )


class WorkflowDefinitionSerializer(serializers.ModelSerializer):
    stages = WorkflowStageSerializer(many=True, required=False)

    class Meta:
        model = WorkflowDefinition
        fields = (
            'id',
            'name',
            'workflow_type',
            'status',
            'description',
            'stages',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'status', 'created_at', 'updated_at')


class ManagementDecisionSerializer(serializers.ModelSerializer):
    approver_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
    )
    rationale = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = ManagementDecision
        fields = (
            'id',
            'subject',
            'options',
            'criteria',
            'proposer',
            'approver_ids',
            'final_decision',
            'execution_owner',
            'due_date',
            'rationale',
            'attachment_refs',
            'impact_schedule',
            'impact_cost',
            'impact_contract',
            'impact_risk',
            'execution_status',
            'related_risk',
            'related_activity',
            'related_contract',
            'workflow_instance',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'workflow_instance', 'created_at', 'updated_at')

    def validate_rationale(self, value):
        return decision_service.validate_rationale(value)

    def validate(self, attrs):
        project_id = self.context.get('project_id')
        if project_id is None and self.instance is not None:
            project_id = self.instance.project_id
        if self.instance is None and 'rationale' not in attrs:
            raise CodedValidationError(detail='Rationale is required.', code='rationale_required')
        merged = {**self._instance_data(), **attrs}
        if self.instance is None:
            merged = decision_service.apply_decision_create(project_id=project_id, data=merged)
            attrs['rationale'] = merged['rationale']
        else:
            decision_service.apply_decision_update(self.instance, merged)
            if 'rationale' in attrs:
                attrs['rationale'] = merged['rationale']
        return attrs

    def _instance_data(self):
        if self.instance is None:
            return {}
        return {
            'rationale': self.instance.rationale,
            'execution_owner': self.instance.execution_owner,
            'related_risk': self.instance.related_risk,
            'related_activity': self.instance.related_activity,
            'related_contract': self.instance.related_contract,
        }

    def create(self, validated_data):
        approver_ids = validated_data.pop('approver_ids', [])
        decision = ManagementDecision.objects.create(**validated_data)
        if approver_ids:
            decision.approvers.set(approver_ids)
        return decision

    def update(self, instance, validated_data):
        approver_ids = validated_data.pop('approver_ids', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if approver_ids is not None:
            instance.approvers.set(approver_ids)
        return instance


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    definition = serializers.PrimaryKeyRelatedField(queryset=WorkflowDefinition.objects.all())

    class Meta:
        model = WorkflowInstance
        fields = (
            'id',
            'definition',
            'subject_type',
            'subject_id',
            'status',
            'current_stage_order',
            'current_due_at',
            'started_by',
            'started_at',
            'completed_at',
            'created_at',
        )
        read_only_fields = (
            'id',
            'status',
            'current_stage_order',
            'current_due_at',
            'started_by',
            'started_at',
            'completed_at',
            'created_at',
        )


class WorkflowInstanceStartSerializer(serializers.Serializer):
    definition = serializers.PrimaryKeyRelatedField(queryset=WorkflowDefinition.objects.all())
    subject_type = serializers.CharField(max_length=60)
    subject_id = serializers.UUIDField()
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class WorkflowCommentSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True, default='')


class WorkflowActionLogSerializer(serializers.ModelSerializer):
    actor = serializers.UUIDField(source='actor_id')

    class Meta:
        model = WorkflowActionLog
        fields = (
            'actor',
            'acted_at',
            'action',
            'from_status',
            'to_status',
            'stage_order',
            'comment',
        )
