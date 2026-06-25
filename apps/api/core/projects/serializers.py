from rest_framework import serializers

from projects.models import Project, ProjectStatus


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='project_name', required=False)
    slug = serializers.CharField(source='project_code', required=False)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'employer',
            'contractor',
            'consultant',
            'project_manager',
            'location',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'status',
            'cut_off_date',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_project_code(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError('Project code is required.')
        return value

    def create(self, validated_data):
        if 'project_name' not in validated_data and 'name' in self.initial_data:
            validated_data['project_name'] = self.initial_data['name']
        if 'project_code' not in validated_data and 'slug' in self.initial_data:
            validated_data['project_code'] = self.initial_data['slug']
        return super().create(validated_data)
