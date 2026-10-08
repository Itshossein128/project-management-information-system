from rest_framework import serializers

from common.viewsets import ProjectScopedViewSet
from projects.models import Stakeholder


class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = [
            'id',
            'name',
            'organization_name',
            'role',
            'email',
            'phone',
            'influence',
            'interest',
            'communication_need',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_influence(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Must be between 1 and 5')
        return value

    def validate_interest(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('Must be between 1 and 5')
        return value


class StakeholderViewSet(ProjectScopedViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer
    view_permission = 'view_project'
    edit_permission = 'edit_project'
