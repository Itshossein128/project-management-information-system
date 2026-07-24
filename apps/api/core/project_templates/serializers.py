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
        children_map = self.context.get('children_map', {})
        children = children_map.get(str(obj.id), [])
        return ProjectTemplateWBSNodeSerializer(children, many=True, context=self.context).data

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
        # ⚡ Bolt: Read annotated wbs_node_count if available to prevent N+1 queries.
        count = getattr(obj, 'annotated_wbs_node_count', None)
        if count is not None:
            return count
        return obj.wbs_nodes.count()


class ProjectTemplateDetailSerializer(ProjectTemplateListSerializer):
    wbs_tree = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta(ProjectTemplateListSerializer.Meta):
        fields = [*ProjectTemplateListSerializer.Meta.fields, 'wbs_tree', 'roles']

    def get_wbs_tree(self, obj):
        # ⚡ Bolt: Fetch all nodes and build the tree iteratively in memory to avoid N+1 recursive queries.
        nodes = list(obj.wbs_nodes.all())
        children_map = {}
        roots = []
        for node in nodes:
            children_map[str(node.id)] = []

        for node in nodes:
            if node.parent_id:
                parent_id_str = str(node.parent_id)
                if parent_id_str in children_map:
                    children_map[parent_id_str].append(node)
            else:
                roots.append(node)

        # Sort roots and children according to the original logic
        roots.sort(key=lambda x: (x.order, x.wbs_code))
        for children in children_map.values():
            children.sort(key=lambda x: (x.order, x.wbs_code))

        return ProjectTemplateWBSNodeSerializer(roots, many=True, context={'children_map': children_map}).data

    def get_roles(self, obj):
        # ⚡ Bolt: Removed .select_related() and used .all() to utilize prefetch cache and avoid N+1 queries.
        return [tr.role.role_name for tr in obj.template_roles.all()]


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
