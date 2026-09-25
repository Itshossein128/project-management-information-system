from rest_framework import serializers

from alerts.models import AlertLog, AlertRule, AlertType


class AlertRuleSerializer(serializers.ModelSerializer):
    threshold_value = serializers.DecimalField(
        source='threshold', max_digits=18, decimal_places=4, required=False, allow_null=True
    )
    is_system = serializers.SerializerMethodField()

    class Meta:
        model = AlertRule
        fields = [
            'id', 'project', 'alert_type', 'name', 'threshold_value', 'notify_roles',
            'recipient_ids', 'cooldown_hours', 'is_active', 'is_system',
        ]
        read_only_fields = ['id', 'project', 'is_system']

    def get_is_system(self, obj):
        return obj.project_id is None


class AlertLogSerializer(serializers.ModelSerializer):
    alert_type = serializers.SerializerMethodField()
    rule_name = serializers.SerializerMethodField()

    class Meta:
        model = AlertLog
        fields = [
            'id', 'rule', 'rule_name', 'alert_type', 'fired_at', 'trigger_reference',
            'message', 'notifications_sent', 'acknowledged_at', 'acknowledged_by',
        ]
        read_only_fields = fields

    def get_alert_type(self, obj):
        return obj.rule.alert_type if obj.rule else ''

    def get_rule_name(self, obj):
        return obj.rule.name if obj.rule else ''
