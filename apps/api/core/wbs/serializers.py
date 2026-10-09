from rest_framework import serializers

from projects.models import WBS, WBSStatus


class WBSTreeSerializer(serializers.ModelSerializer):
    wbs_id = serializers.UUIDField(source='id', read_only=True)
    depth = serializers.IntegerField(read_only=True)
    weight_physical = serializers.DecimalField(max_digits=8, decimal_places=4, coerce_to_string=True, read_only=True)
    weight_financial = serializers.DecimalField(max_digits=8, decimal_places=4, coerce_to_string=True, read_only=True)
    responsible = serializers.UUIDField(source='responsible_id', read_only=True, allow_null=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = WBS
        fields = [
            'wbs_id',
            'wbs_code',
            'wbs_name',
            'weight_physical',
            'weight_financial',
            'description',
            'responsible',
            'acceptance_criteria',
            'status',
            'depth',
            'children',
        ]

    def get_children(self, obj):
        children_map = self.context.get('children_map', {})
        children = children_map.get(str(obj.id), [])
        return WBSTreeSerializer(children, many=True, context=self.context).data


class WBSFlatSerializer(serializers.ModelSerializer):
    wbs_id = serializers.UUIDField(source='id', read_only=True)
    depth = serializers.IntegerField(read_only=True)
    project = serializers.UUIDField(source='project_id', read_only=True)
    responsible = serializers.UUIDField(source='responsible_id', read_only=True, allow_null=True)

    class Meta:
        model = WBS
        fields = [
            'wbs_id',
            'project',
            'wbs_code',
            'wbs_name',
            'depth',
            'weight_physical',
            'weight_financial',
            'description',
            'responsible',
            'acceptance_criteria',
            'status',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
            'is_deleted',
        ]


class WBSCreateSerializer(serializers.Serializer):
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    wbs_code = serializers.CharField(max_length=30)
    wbs_name = serializers.CharField(max_length=200)
    weight_physical = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    weight_financial = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    responsible = serializers.UUIDField(required=False, allow_null=True)
    acceptance_criteria = serializers.CharField(required=False, allow_blank=True, default='')
    status = serializers.ChoiceField(choices=WBSStatus.choices, required=False, default=WBSStatus.ACTIVE)


class WBSUpdateSerializer(serializers.Serializer):
    wbs_name = serializers.CharField(max_length=200, required=False)
    weight_physical = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    weight_financial = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    responsible = serializers.UUIDField(required=False, allow_null=True)
    acceptance_criteria = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=WBSStatus.choices, required=False)


class WBSMoveSerializer(serializers.Serializer):
    new_parent_id = serializers.UUIDField(required=False, allow_null=True)
    position = serializers.ChoiceField(
        choices=['first-child', 'last-child', 'left', 'right', 'first_child', 'last_child', 'sorted_child', 'sorted-child'],
    )
