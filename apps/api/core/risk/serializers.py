from rest_framework import serializers

from common.serializers import JalaliDateField
from risk.models import BarrierCategory, BarrierStatus, EventType, RiskEvent


class BarrierSerializer(serializers.ModelSerializer):
    """
    Standardizes data flow between the API and DB for barrier risk events.

    Maps dates between Jalali for the frontend and Gregorian for the DB, and
    provides logic to ensure a resolved_date is supplied when a barrier
    is marked as resolved.
    """

    log_date = JalaliDateField(source='event_date')
    resolved_date = JalaliDateField(required=False, allow_null=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    responsible_user_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskEvent
        fields = [
            'id',
            'log_date',
            'description',
            'category',
            'category_label',
            'impact_on_schedule',
            'impact_on_cost',
            'status',
            'status_label',
            'resolved_date',
            'corrective_action',
            'responsible_user',
            'responsible_user_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_user_name(self, obj):
        if not obj.responsible_user:
            return ''
        return obj.responsible_user.get_full_name() or obj.responsible_user.username

    def validate(self, attrs):
        status = attrs.get('status', getattr(self.instance, 'status', BarrierStatus.OPEN))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if status == BarrierStatus.RESOLVED and not resolved_date:
            raise serializers.ValidationError(
                {'resolved_date': 'برای وضعیت «رفع شده» تاریخ رفع الزامی است.'},
            )
        return attrs


class BarrierCreateSerializer(BarrierSerializer):
    """
    A specialized serializer for creating new barriers.

    Overrides the create method to strictly enforce the `EventType.BARRIER`
    event type regardless of user input.
    """

    log_date = JalaliDateField(source='event_date')

    def create(self, validated_data):
        validated_data['event_type'] = EventType.BARRIER
        return super().create(validated_data)
