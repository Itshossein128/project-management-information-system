from rest_framework import serializers

from decision_support.models import DecisionCase, DecisionRun


class DecisionCaseSerializer(serializers.ModelSerializer):
    criteria_count = serializers.SerializerMethodField()
    alternatives_count = serializers.SerializerMethodField()

    class Meta:
        model = DecisionCase
        fields = [
            'id',
            'title',
            'selected_methods',
            'criteria',
            'alternatives',
            'weights',
            'types',
            'performance_matrix',
            'ahp_matrix',
            'dematel_matrix',
            'ism_matrix',
            'criteria_count',
            'alternatives_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'criteria_count', 'alternatives_count', 'created_at', 'updated_at']

    def get_criteria_count(self, obj):
        return len(obj.criteria or [])

    def get_alternatives_count(self, obj):
        return len(obj.alternatives or [])


class DecisionCaseListSerializer(serializers.ModelSerializer):
    criteria_count = serializers.SerializerMethodField()
    alternatives_count = serializers.SerializerMethodField()

    class Meta:
        model = DecisionCase
        fields = [
            'id',
            'title',
            'selected_methods',
            'criteria_count',
            'alternatives_count',
            'updated_at',
        ]

    def get_criteria_count(self, obj):
        return len(obj.criteria or [])

    def get_alternatives_count(self, obj):
        return len(obj.alternatives or [])


class DecisionRunSerializer(serializers.ModelSerializer):
    extracted_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DecisionRun
        fields = [
            'id',
            'method',
            'input_snapshot',
            'result',
            'extracted_at',
            'extracted_by',
            'extracted_by_name',
            'created_at',
        ]
        read_only_fields = fields

    def get_extracted_by_name(self, obj):
        user = obj.extracted_by
        if user is None:
            return ''
        return getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'phone', '') or str(user.pk)


class DecisionRunCreateSerializer(serializers.Serializer):
    method = serializers.CharField(max_length=32)
