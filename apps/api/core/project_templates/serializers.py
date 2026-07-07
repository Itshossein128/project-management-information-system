from rest_framework import serializers

from project_templates.models import (
    ProjectTemplate,
    ProjectTemplateActivity,
    ProjectTemplateRole,
    ProjectTemplateWBS,
    ProjectType,
)


class ProjectTemplateWBSNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    activities = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTemplateWBS
        fields = ['id', 'wbs_code', 'wbs_name', 'weight_physical', 'level', 'order', 'children', 'activities']

    def get_children(self, obj):
        children = obj.children.all().order_by('order', 'wbs_code')
        return ProjectTemplateWBSNodeSerializer(children, many=True).data

    def get_activities(self, obj):
        return ProjectTemplateActivitySerializer(obj.activities.all(), many=True).data


class ProjectTemplateActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTemplateActivity
        fields = ['activity_code', 'activity_name', 'unit', 'duration_days', 'weight']


class ProjectTemplateListSerializer(serializers.ModelSerializer):
    template_id = serializers.UUIDField(source='id', read_only=True)
    wbs_node_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTemplate
        fields = [
            'template_id', 'template_name', 'description', 'project_type',
            'is_system', 'created_at', 'updated_at', 'wbs_node_count',
        ]

    def get_wbs_node_count(self, obj):
        return obj.wbs_nodes.count()


class ProjectTemplateDetailSerializer(ProjectTemplateListSerializer):
    wbs_tree = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta(ProjectTemplateListSerializer.Meta):
        fields = [*ProjectTemplateListSerializer.Meta.fields, 'wbs_tree', 'roles']

    def get_wbs_tree(self, obj):
        roots = obj.wbs_nodes.filter(parent__isnull=True).order_by('order', 'wbs_code')
        return ProjectTemplateWBSNodeSerializer(roots, many=True).data

    def get_roles(self, obj):
        return [tr.role.role_name for tr in obj.template_roles.select_related('role')]


class ProjectTemplateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTemplate
        fields = ['template_name', 'description', 'project_type']


class SaveAsTemplateSerializer(serializers.Serializer):
    template_name = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    project_type = serializers.ChoiceField(
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
    )
    is_system = serializers.BooleanField(default=False, required=False)
