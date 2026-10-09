"""Activity, calendar, baseline, and schedule-change serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from projects.models import Activity, ActivityRelation, ActivityStatus, RelationType
from schedule.models import (
    BaselineActivity,
    BaselineSchedule,
    CalendarException,
    ScheduleChangeItem,
    ScheduleChangeRequest,
    WorkingCalendar,
)
from schedule.services.activity_validation import validate_activity_payload


class PredecessorLinkSerializer(serializers.ModelSerializer):
    activity_id = serializers.UUIDField(source='predecessor.id', read_only=True)
    activity_code = serializers.CharField(source='predecessor.activity_code', read_only=True)
    activity_name = serializers.CharField(source='predecessor.activity_name', read_only=True)

    class Meta:
        model = ActivityRelation
        fields = ['activity_id', 'activity_code', 'activity_name', 'relation_type', 'lag_days']


class SuccessorLinkSerializer(serializers.ModelSerializer):
    activity_id = serializers.UUIDField(source='successor.id', read_only=True)
    activity_code = serializers.CharField(source='successor.activity_code', read_only=True)
    activity_name = serializers.CharField(source='successor.activity_name', read_only=True)

    class Meta:
        model = ActivityRelation
        fields = ['activity_id', 'activity_code', 'activity_name', 'relation_type', 'lag_days']


class ActivityListSerializer(serializers.ModelSerializer):
    activity_id = serializers.UUIDField(source='id', read_only=True)
    project_id = serializers.UUIDField(read_only=True)
    wbs_id = serializers.UUIDField(source='wbs.id', read_only=True)
    wbs_code = serializers.CharField(source='wbs.wbs_code', read_only=True)
    wbs_name = serializers.CharField(source='wbs.wbs_name', read_only=True)
    unit_id = serializers.UUIDField(source='unit.id', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True, allow_null=True)
    responsible_id = serializers.UUIDField(source='responsible.id', read_only=True, allow_null=True)
    responsible_full_name = serializers.CharField(source='responsible.full_name', read_only=True, allow_null=True)
    working_calendar_id = serializers.UUIDField(source='working_calendar.id', read_only=True, allow_null=True)
    planned_start = JalaliDateField(required=False, allow_null=True)
    planned_finish = JalaliDateField(required=False, allow_null=True)
    actual_start = JalaliDateField(required=False, allow_null=True)
    actual_finish = JalaliDateField(required=False, allow_null=True)
    forecast_start = JalaliDateField(required=False, allow_null=True)
    forecast_finish = JalaliDateField(required=False, allow_null=True)
    planned_duration = serializers.IntegerField(read_only=True)
    actual_duration = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    predecessor_count = serializers.IntegerField(read_only=True)
    successor_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = [
            'activity_id',
            'project_id',
            'activity_code',
            'activity_name',
            'unit_id',
            'unit_name',
            'total_quantity',
            'weight',
            'planned_start',
            'planned_finish',
            'actual_start',
            'actual_finish',
            'forecast_start',
            'forecast_finish',
            'duration_days',
            'is_milestone',
            'working_calendar_id',
            'planned_duration',
            'actual_duration',
            'is_overdue',
            'responsible_id',
            'responsible_full_name',
            'status',
            'description',
            'wbs_id',
            'wbs_code',
            'wbs_name',
            'predecessor_count',
            'successor_count',
            'created_at',
            'updated_at',
        ]


class ActivityDetailSerializer(ActivityListSerializer):
    predecessors = serializers.SerializerMethodField()
    successors = serializers.SerializerMethodField()

    class Meta(ActivityListSerializer.Meta):
        fields = ActivityListSerializer.Meta.fields + ['predecessors', 'successors']

    def get_predecessors(self, obj):
        rels = obj.predecessor_relations.select_related('predecessor').all()
        return PredecessorLinkSerializer(rels, many=True).data

    def get_successors(self, obj):
        rels = obj.successor_relations.select_related('successor').all()
        return SuccessorLinkSerializer(rels, many=True).data


class ActivityCreateUpdateSerializer(serializers.ModelSerializer):
    wbs_id = serializers.UUIDField(write_only=True)
    unit_id = serializers.UUIDField(required=False, allow_null=True)
    responsible_id = serializers.UUIDField(required=False, allow_null=True)
    working_calendar_id = serializers.UUIDField(required=False, allow_null=True)
    planned_start = JalaliDateField(required=False, allow_null=True)
    planned_finish = JalaliDateField(required=False, allow_null=True)
    actual_start = JalaliDateField(required=False, allow_null=True)
    actual_finish = JalaliDateField(required=False, allow_null=True)
    forecast_start = JalaliDateField(required=False, allow_null=True)
    forecast_finish = JalaliDateField(required=False, allow_null=True)
    duration_days = serializers.IntegerField(required=False, allow_null=True)
    is_milestone = serializers.BooleanField(required=False)

    class Meta:
        model = Activity
        fields = [
            'activity_code',
            'activity_name',
            'wbs_id',
            'unit_id',
            'total_quantity',
            'weight',
            'planned_start',
            'planned_finish',
            'actual_start',
            'actual_finish',
            'forecast_start',
            'forecast_finish',
            'duration_days',
            'is_milestone',
            'working_calendar_id',
            'responsible_id',
            'status',
            'description',
        ]

    def validate_status(self, value):
        if value not in dict(ActivityStatus.choices):
            raise serializers.ValidationError('وضعیت نامعتبر است.')
        return value

    def validate_wbs_id(self, value):
        project_id = self.context.get('project_id')
        from projects.models import WBS

        if not WBS.objects.filter(pk=value, project_id=project_id).exists():
            raise serializers.ValidationError('گره WBS یافت نشد.')
        return value

    def validate(self, attrs):
        project_id = self.context['project_id']
        # Include write_only UUID fields for validation merge
        payload = dict(attrs)
        if 'working_calendar_id' in self.initial_data:
            payload['working_calendar_id'] = attrs.get('working_calendar_id')
        validate_activity_payload(project_id, payload, instance=self.instance)
        return attrs

    def create(self, validated_data):
        wbs_id = validated_data.pop('wbs_id')
        unit_id = validated_data.pop('unit_id', None)
        responsible_id = validated_data.pop('responsible_id', None)
        working_calendar_id = validated_data.pop('working_calendar_id', None)
        return Activity.objects.create(
            project_id=self.context['project_id'],
            wbs_id=wbs_id,
            unit_id=unit_id,
            responsible_id=responsible_id,
            working_calendar_id=working_calendar_id,
            created_by=self.context['request'].user,
            updated_by=self.context['request'].user,
            **validated_data,
        )

    def update(self, instance, validated_data):
        if 'wbs_id' in validated_data:
            instance.wbs_id = validated_data.pop('wbs_id')
        if 'unit_id' in validated_data:
            instance.unit_id = validated_data.pop('unit_id')
        if 'responsible_id' in validated_data:
            instance.responsible_id = validated_data.pop('responsible_id')
        if 'working_calendar_id' in validated_data:
            instance.working_calendar_id = validated_data.pop('working_calendar_id')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.updated_by = self.context['request'].user
        instance.save()
        return instance


class ActivityRelationCreateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['predecessor', 'successor'])
    predecessor_id = serializers.UUIDField(required=False)
    successor_id = serializers.UUIDField(required=False)
    relation_type = serializers.ChoiceField(choices=RelationType.choices, default=RelationType.FS)
    lag_days = serializers.IntegerField(default=0)

    def validate(self, attrs):
        role = attrs['role']
        if role == 'predecessor' and not attrs.get('successor_id'):
            raise serializers.ValidationError({'successor_id': 'این فیلد الزامی است.'})
        if role == 'successor' and not attrs.get('predecessor_id'):
            raise serializers.ValidationError({'predecessor_id': 'این فیلد الزامی است.'})
        return attrs


class WeightSummarySerializer(serializers.Serializer):
    total_weight = serializers.FloatField()
    remaining = serializers.FloatField()
    is_balanced = serializers.BooleanField()
    warning = serializers.CharField(allow_null=True)


class WorkingCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingCalendar
        fields = [
            'id',
            'name',
            'is_default',
            'work_monday',
            'work_tuesday',
            'work_wednesday',
            'work_thursday',
            'work_friday',
            'work_saturday',
            'work_sunday',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CalendarExceptionSerializer(serializers.ModelSerializer):
    exception_date = JalaliDateField()

    class Meta:
        model = CalendarException
        fields = ['id', 'exception_date', 'is_working', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BaselineScheduleSerializer(serializers.ModelSerializer):
    approved_by = serializers.UUIDField(source='approved_by_id', read_only=True, allow_null=True)
    locked_by = serializers.UUIDField(source='locked_by_id', read_only=True, allow_null=True)
    source_change_request_id = serializers.UUIDField(read_only=True, allow_null=True)

    class Meta:
        model = BaselineSchedule
        fields = [
            'id',
            'version_name',
            'is_current',
            'is_locked',
            'approved_at',
            'approved_by',
            'locked_at',
            'locked_by',
            'source_change_request_id',
        ]


class BaselineCreateSerializer(serializers.Serializer):
    version_name = serializers.CharField(max_length=60, required=False, allow_blank=True, default='')
    make_current = serializers.BooleanField(required=False, default=False)


class BaselineActivitySerializer(serializers.ModelSerializer):
    planned_start = JalaliDateField(required=False, allow_null=True)
    planned_finish = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = BaselineActivity
        fields = [
            'id',
            'activity_id',
            'planned_start',
            'planned_finish',
            'planned_duration',
            'planned_quantity',
            'total_float',
            'free_float',
            'is_critical',
        ]
        read_only_fields = ['id', 'activity_id']


class ScheduleChangeItemSerializer(serializers.ModelSerializer):
    activity_id = serializers.UUIDField()
    proposed_planned_start = JalaliDateField(required=False, allow_null=True)
    proposed_planned_finish = JalaliDateField(required=False, allow_null=True)
    proposed_forecast_start = JalaliDateField(required=False, allow_null=True)
    proposed_forecast_finish = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = ScheduleChangeItem
        fields = [
            'id',
            'activity_id',
            'proposed_planned_start',
            'proposed_planned_finish',
            'proposed_duration_days',
            'proposed_forecast_start',
            'proposed_forecast_finish',
            'notes',
        ]
        read_only_fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['activity_id'] = str(instance.activity_id)
        return data


class ScheduleChangeRequestSerializer(serializers.ModelSerializer):
    items = ScheduleChangeItemSerializer(many=True, required=False)
    base_baseline_id = serializers.UUIDField(read_only=True, allow_null=True)
    resulting_baseline_id = serializers.UUIDField(read_only=True, allow_null=True)
    created_by = serializers.UUIDField(source='created_by_id', read_only=True)
    decided_by = serializers.UUIDField(source='decided_by_id', read_only=True, allow_null=True)

    class Meta:
        model = ScheduleChangeRequest
        fields = [
            'id',
            'reason',
            'milestone_impact',
            'cost_impact',
            'contract_impact',
            'status',
            'base_baseline_id',
            'resulting_baseline_id',
            'created_by',
            'submitted_at',
            'decided_by',
            'decided_at',
            'decision_notes',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'base_baseline_id',
            'resulting_baseline_id',
            'created_by',
            'submitted_at',
            'decided_by',
            'decided_at',
            'decision_notes',
            'created_at',
            'updated_at',
        ]


class ScheduleChangeDecisionSerializer(serializers.Serializer):
    decision_notes = serializers.CharField(required=False, allow_blank=True, default='')
