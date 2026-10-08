from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_label = serializers.CharField(
        source='get_notification_type_display',
        read_only=True,
    )
    responsible_user_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id',
            'project',
            'notification_type',
            'notification_type_label',
            'title',
            'message',
            'link',
            'responsible_user',
            'responsible_user_name',
            'due_at',
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = fields

    def get_responsible_user_name(self, obj):
        if obj.responsible_user_id and obj.responsible_user:
            return getattr(obj.responsible_user, 'full_name', None) or str(obj.responsible_user)
        return None
