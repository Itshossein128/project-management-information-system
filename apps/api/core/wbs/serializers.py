from rest_framework import serializers

from projects.models import WBS


class WBSTreeSerializer(serializers.ModelSerializer):
    wbs_id = serializers.UUIDField(source='id', read_only=True)
    depth = serializers.IntegerField(read_only=True)
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

    class Meta:
        model = WBS
        fields = [
            'wbs_id',
            'wbs_code',
            'wbs_name',
            'depth',
            'weight_physical',
            'weight_financial',
        ]


class WBSCreateSerializer(serializers.Serializer):
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    wbs_code = serializers.CharField(max_length=30)
    wbs_name = serializers.CharField(max_length=200)
    weight_physical = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    weight_financial = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')


class WBSUpdateSerializer(serializers.Serializer):
    wbs_name = serializers.CharField(max_length=200, required=False)
    weight_physical = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    weight_financial = serializers.DecimalField(max_digits=8, decimal_places=4, required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)


class WBSMoveSerializer(serializers.Serializer):
    new_parent_id = serializers.UUIDField(required=False, allow_null=True)
    position = serializers.ChoiceField(
        choices=['first-child', 'last-child', 'left', 'right', 'first_child', 'last_child'],
    )
