"""Approval serializers."""
from rest_framework import serializers

from procurement.models import ApprovalLog


class ApprovalLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()
    step_from_display = serializers.SerializerMethodField()
    step_to_display = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ApprovalLog
        fields = [
            'id', 'requisition', 'step_from', 'step_from_display',
            'step_to', 'step_to_display', 'action', 'action_display',
            'performed_by', 'performed_by_name', 'performed_at', 'comments',
        ]
        read_only_fields = ['id', 'performed_at']

    def get_performed_by_name(self, obj):
        return str(obj.performed_by) if obj.performed_by else None

    def _status_display(self, code):
        from procurement.models import RequisitionStatus
        try:
            return RequisitionStatus(code).label
        except ValueError:
            return code

    def get_step_from_display(self, obj):
        return self._status_display(obj.step_from)

    def get_step_to_display(self, obj):
        return self._status_display(obj.step_to)


class ApprovalActionSerializer(serializers.Serializer):
    """Input for approve/reject/return actions."""
    comments = serializers.CharField(required=False, allow_blank=True, default='')
