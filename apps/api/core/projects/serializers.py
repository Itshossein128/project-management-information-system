from rest_framework import serializers

from projects.models import Project, ProjectStatus


class ProjectListSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id',
            'id',
            'project_code',
            'project_name',
            'name',
            'slug',
            'employer',
            'status',
            'start_date',
            'planned_finish_date',
            'contract_amount',
            'member_count',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    project_id = serializers.UUIDField(source='id', read_only=True)
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField(source='project_name', read_only=True)
    slug = serializers.CharField(source='project_code', read_only=True)

    class Meta:
        model = Project
        fields = [
            'project_id',
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
            'max_depth',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['project_id', 'id', 'name', 'slug', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
            'employer',
            'contractor',
            'consultant',
            'planned_finish_date',
            'contract_amount',
            'contract_type',
            'location',
            'start_date',
        ]

    def validate_project_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Project code is required.')
        return value

    def validate(self, attrs):
        if not attrs.get('project_name'):
            raise serializers.ValidationError({'project_name': 'This field is required.'})
        if not attrs.get('employer'):
            raise serializers.ValidationError({'employer': 'This field is required.'})
        if not attrs.get('start_date'):
            raise serializers.ValidationError({'start_date': 'This field is required.'})
        return attrs


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'project_code',
            'project_name',
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
        ]

    def validate_status(self, value):
        if value not in ProjectStatus.values:
            raise serializers.ValidationError('Invalid status.')
        return value


# Backward-compatible alias
ProjectSerializer = ProjectDetailSerializer
