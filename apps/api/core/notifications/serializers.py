from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    notification_type_label = serializers.CharField(
        source='get_notification_type_display',
        read_only=True,
    )

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
            'is_read',
            'read_at',
            'created_at',
        ]
        read_only_fields = fields
