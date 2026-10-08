from rest_framework import serializers
from django.utils.translation import gettext as _

from config.exceptions import CodedValidationError
from projects.models import (
    PROTECTED_PROJECT_FIELDS,
    FiscalPeriodLock,
    Project,
    ProjectCapabilitySetting,
    ProjectChangeRequest,
    ProjectKickoffCharter,
    ProjectStatus,
)


PROTECTED_WHEN_STATUSES = {
    ProjectStatus.ACTIVE,
    ProjectStatus.SUSPENDED,
    ProjectStatus.COMPLETED,
    ProjectStatus.ARCHIVED,
}


class ProjectListSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id',
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'employer',
            'status',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'currency',
            'member_count',
            'purpose',
            'scope_description',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id',
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'consultant',
            'project_manager',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'status',
            'budget_approved_at',
            'budget_approved_by',
            'cut_off_date',
            'max_depth',
            'owning_unit',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'project_id',
            'id',
            'name',
            'slug',
            'budget_approved_at',
            'budget_approved_by',
            'created_at',
            'updated_at',
            'status',
        ]


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'consultant',
            'project_manager',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'location',
            'start_date',
            'owning_unit',
        ]

    def validate_project_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_('Project code is required.'))
        return value

    def validate(self, attrs):
        if not attrs.get('project_name'):
            raise serializers.ValidationError({'project_name': 'This field is required.'})
        if not attrs.get('employer'):
            raise serializers.ValidationError({'employer': 'This field is required.'})
        if not attrs.get('start_date'):
            raise serializers.ValidationError({'start_date': 'This field is required.'})
        return attrs

    def create(self, validated_data):
        validated_data['status'] = ProjectStatus.DRAFT
        validated_data['budget_approved_at'] = None
        validated_data['budget_approved_by'] = None
        return super().create(validated_data)


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
            'purpose',
            'scope_description',
            'main_deliverables',
            'employer',
            'contractor',
            'consultant',
            'project_manager',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'contract_number',
            'currency',
            'cut_off_date',
            'owning_unit',
        ]

    def validate(self, attrs):
        instance: Project = self.instance
        if instance and instance.status in PROTECTED_WHEN_STATUSES:
            blocked = [k for k in attrs if k in PROTECTED_PROJECT_FIELDS]
            if blocked:
                raise CodedValidationError(
                    {
                        'code': 'protected_field_requires_change_request',
                        'detail': 'Protected fields require a project change request.',
                        'fields': blocked,
                    },
                    code='protected_field_requires_change_request',
                )
        return attrs


# Backward-compatible alias
ProjectSerializer = ProjectDetailSerializer


class ProjectCapabilitySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCapabilitySetting
        fields = [
            'capability_key',
            'enabled',
            'mode',
            'updated_at',
            'updated_by',
        ]
        read_only_fields = ['capability_key', 'updated_at', 'updated_by']


class FiscalPeriodLockSerializer(serializers.ModelSerializer):
    class Meta:
        model = FiscalPeriodLock
        fields = [
            'id',
            'period_start',
            'period_end',
            'reason',
            'closed_at',
            'closed_by',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'closed_at', 'closed_by', 'is_active', 'created_at']


class ProjectKickoffCharterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectKickoffCharter
        fields = [
            'id',
            'justification',
            'success_criteria',
            'constraints',
            'assumptions',
            'key_stakeholders_summary',
            'pm_authority',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectChangeRequest
        fields = [
            'id',
            'reason',
            'status',
            'proposed_changes',
            'previous_values',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'decision_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'previous_values',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'created_at',
            'updated_at',
        ]
