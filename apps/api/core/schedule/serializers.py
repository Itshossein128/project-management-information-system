"""Activity and relation serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from projects.models import Activity, ActivityRelation, ActivityStatus, RelationType


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
    wbs_id = serializers.UUIDField(source='wbs.id', read_only=True)
    wbs_code = serializers.CharField(source='wbs.wbs_code', read_only=True)
    wbs_name = serializers.CharField(source='wbs.wbs_name', read_only=True)
    unit_id = serializers.UUIDField(source='unit.id', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.unit_name', read_only=True, allow_null=True)
    responsible_id = serializers.UUIDField(source='responsible.id', read_only=True, allow_null=True)
    responsible_full_name = serializers.CharField(source='responsible.full_name', read_only=True, allow_null=True)
    planned_start = JalaliDateField(required=False, allow_null=True)
    planned_finish = JalaliDateField(required=False, allow_null=True)
    actual_start = JalaliDateField(required=False, allow_null=True)
    actual_finish = JalaliDateField(required=False, allow_null=True)
    planned_duration = serializers.IntegerField(read_only=True)
    actual_duration = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    predecessor_count = serializers.IntegerField(read_only=True)
    successor_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Activity
        fields = [
            'activity_id',
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
    planned_start = JalaliDateField(required=False, allow_null=True)
    planned_finish = JalaliDateField(required=False, allow_null=True)
    actual_start = JalaliDateField(required=False, allow_null=True)
    actual_finish = JalaliDateField(required=False, allow_null=True)

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

    def create(self, validated_data):
        wbs_id = validated_data.pop('wbs_id')
        unit_id = validated_data.pop('unit_id', None)
        responsible_id = validated_data.pop('responsible_id', None)
        return Activity.objects.create(
            project_id=self.context['project_id'],
            wbs_id=wbs_id,
            unit_id=unit_id,
            responsible_id=responsible_id,
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
