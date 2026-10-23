from rest_framework import serializers

from common.reporting_units import SpecialtyUnit, is_canonical_unit
from project_templates.models import (
    LaborTitleCatalog,
    LaborTitleCatalogTitle,
    ProjectReportingConfiguration,
    ProjectReportingConfigurationLaborTitle,
    ProjectReportingConfigurationStoppageReason,
    ProjectReportingConfigurationUnit,
    ProjectTemplate,
    ProjectTemplateActivity,
    ProjectTemplateRequiredUnit,
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
    required_daily_report_units = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTemplate
        fields = [
            'template_id', 'template_name', 'description', 'project_type',
            'is_system', 'created_at', 'updated_at', 'wbs_node_count',
            'required_daily_report_units',
        ]

    def get_wbs_node_count(self, obj):
        # ⚡ Bolt: Use len(all()) instead of .count() on prefetched relation to avoid N+1 queries
        return len(obj.wbs_nodes.all())

    def get_required_daily_report_units(self, obj):
        return [u.unit for u in obj.required_units.all().order_by('display_order', 'id')]


class ProjectTemplateDetailSerializer(ProjectTemplateListSerializer):
    wbs_tree = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta(ProjectTemplateListSerializer.Meta):
        fields = [*ProjectTemplateListSerializer.Meta.fields, 'wbs_tree', 'roles']

    def get_wbs_tree(self, obj):
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

        roots.sort(key=lambda x: (x.order, x.wbs_code))
        for children in children_map.values():
            children.sort(key=lambda x: (x.order, x.wbs_code))

        return ProjectTemplateWBSNodeSerializer(roots, many=True, context={'children_map': children_map}).data

    def get_roles(self, obj):
        return [tr.role.role_name for tr in obj.template_roles.all()]


class ProjectTemplateCreateSerializer(serializers.ModelSerializer):
    required_daily_report_units = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = ProjectTemplate
        fields = ['template_name', 'description', 'project_type', 'required_daily_report_units']

    def validate_required_daily_report_units(self, value):
        if value is None:
            return value
        if len(value) == 0:
            raise serializers.ValidationError(
                'Reporting templates must specify at least one required canonical unit.',
                code='invalid_required_units',
            )
        seen = set()
        for item in value:
            if not is_canonical_unit(item):
                raise serializers.ValidationError(
                    f"'{item}' is not a valid canonical specialty unit.",
                    code='invalid_required_units',
                )
            if item in seen:
                raise serializers.ValidationError(
                    f"Duplicate unit '{item}' in required units list.",
                    code='invalid_required_units',
                )
            seen.add(item)
        return value

    def create(self, validated_data):
        units_data = validated_data.pop('required_daily_report_units', None)
        template = super().create(validated_data)
        if units_data:
            for order, unit in enumerate(units_data):
                ProjectTemplateRequiredUnit.objects.create(
                    template=template,
                    unit=unit,
                    display_order=order,
                )
        return template

    def update(self, instance, validated_data):
        units_data = validated_data.pop('required_daily_report_units', None)
        template = super().update(instance, validated_data)
        if units_data is not None:
            template.required_units.all().delete()
            for order, unit in enumerate(units_data):
                ProjectTemplateRequiredUnit.objects.create(
                    template=template,
                    unit=unit,
                    display_order=order,
                )
        return template

    def to_representation(self, instance):
        return ProjectTemplateDetailSerializer(instance, context=self.context).data


class SaveAsTemplateSerializer(serializers.Serializer):
    template_name = serializers.CharField(max_length=120)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    project_type = serializers.ChoiceField(
        choices=ProjectType.choices,
        default=ProjectType.OTHER,
    )
    is_system = serializers.BooleanField(default=False, required=False)


# ---------------------------------------------------------------------------
# Project Reporting Configurations (Feature 032, contracts/report-template-api.md)
# ---------------------------------------------------------------------------


class ProjectReportingConfigurationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectReportingConfigurationUnit
        fields = ['unit', 'display_order']


class ProjectReportingConfigurationLaborTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectReportingConfigurationLaborTitle
        fields = [
            'title_code', 'title_label', 'title_label_fa', 'category',
            'display_order', 'legacy_alias', 'source_catalog_version',
        ]


class ProjectReportingConfigurationStoppageReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectReportingConfigurationStoppageReason
        fields = ['reason_code', 'reason_label', 'reason_label_fa', 'display_order']


class ProjectReportingConfigurationSerializer(serializers.ModelSerializer):
    source_template = serializers.SerializerMethodField()
    required_units = serializers.SerializerMethodField()
    activated_by = serializers.SerializerMethodField()
    activated_at = serializers.SerializerMethodField()
    labor_titles = serializers.SerializerMethodField()
    stoppage_reasons = serializers.SerializerMethodField()
    man_hours_rule = serializers.SerializerMethodField()

    class Meta:
        model = ProjectReportingConfiguration
        fields = [
            'id',
            'project_id',
            'source_template',
            'effective_from',
            'required_units',
            'labor_titles',
            'man_hours_rule',
            'stoppage_reasons',
            'supersedes',
            'activated_by',
            'activated_at',
        ]

    def get_source_template(self, obj):
        name = obj.source_template_name_snapshot or (
            obj.source_template.template_name if obj.source_template else ''
        )
        return {
            'id': str(obj.source_template_id),
            'name': name,
        }

    def get_required_units(self, obj):
        return [u.unit for u in obj.required_units.all().order_by('display_order', 'id')]

    def get_labor_titles(self, obj):
        titles = obj.labor_titles.all().order_by('display_order', 'title_code')
        return ProjectReportingConfigurationLaborTitleSerializer(titles, many=True).data

    def get_stoppage_reasons(self, obj):
        reasons = obj.stoppage_reasons.all().order_by('display_order', 'reason_code')
        return ProjectReportingConfigurationStoppageReasonSerializer(reasons, many=True).data

    def get_man_hours_rule(self, obj):
        return {
            'rule_code': obj.man_hours_rule_code or 'standard_shift_plus_overtime',
            'parameters': {
                'standard_shift_hours': str(obj.standard_shift_hours) if obj.standard_shift_hours is not None else '8',
            },
        }

    def get_activated_by(self, obj):
        if not obj.activated_by:
            return None
        return {
            'id': str(obj.activated_by_id),
            'display_name': obj.activated_by.get_full_name() or obj.activated_by.username,
        }

    def get_activated_at(self, obj):
        return obj.activated_at.isoformat().replace('+00:00', 'Z') if obj.activated_at else None


class ProjectReportingConfigurationActivateSerializer(serializers.Serializer):
    template_id = serializers.UUIDField()
    effective_from = serializers.DateField()
    confirm_backdated = serializers.BooleanField(default=False, required=False)
    reason = serializers.CharField(required=False, allow_blank=True, default='')


class ProjectReportingConfigurationPreviewSerializer(serializers.Serializer):
    template_id = serializers.UUIDField()
    effective_from = serializers.DateField()


# ---------------------------------------------------------------------------
# Labor-title catalogs (feature 033, contracts/reporting-configuration-catalog-api.md §1)
# ---------------------------------------------------------------------------


class LaborTitleCatalogTitleSerializer(serializers.ModelSerializer):
    catalog = serializers.UUIDField(read_only=True)

    class Meta:
        model = LaborTitleCatalogTitle
        fields = [
            'id',
            'catalog',
            'title_code',
            'title_label',
            'title_label_fa',
            'category',
            'display_order',
            'active',
            'legacy_alias',
            'project_specific',
        ]
        read_only_fields = ['id', 'catalog']

    def validate_category(self, value):
        if value not in ('indirect', 'direct'):
            raise serializers.ValidationError(
                "category must be 'indirect' or 'direct'.",
                code='invalid_labor_category',
            )
        return value

    def validate_display_order(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'display_order must be non-negative.',
                code='invalid_display_order',
            )
        return value

    def _catalog(self):
        return self.context.get('catalog') or (self.instance.catalog if self.instance else None)

    def validate(self, attrs):
        # Nested datasets (create-with-titles) resolve uniqueness against the
        # DB constraints at service level; row-level endpoints require the
        # catalog context here.
        if self.context.get('catalog') is None and self.instance is None:
            return attrs
        catalog = self._catalog()
        category = attrs.get('category', getattr(self.instance, 'category', None))
        display_order = attrs.get(
            'display_order', getattr(self.instance, 'display_order', None),
        )
        # (catalog, category, display_order) uniqueness derived from the DB
        # constraint, surfaced as a form error.
        qs = LaborTitleCatalogTitle.objects.filter(
            catalog=catalog, category=category, display_order=display_order,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'display_order': 'display_order must be unique within (catalog, category).'},
                code='duplicate_display_order',
            )
        # (catalog, title_code) uniqueness likewise.
        title_code = attrs.get('title_code', getattr(self.instance, 'title_code', None))
        qs = LaborTitleCatalogTitle.objects.filter(catalog=catalog, title_code=title_code)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                {'title_code': 'title_code must be unique within the catalog.'},
                code='duplicate_title_code',
            )
        return attrs


class LaborTitleCatalogSerializer(serializers.ModelSerializer):
    titles = serializers.SerializerMethodField()

    class Meta:
        model = LaborTitleCatalog
        fields = ['id', 'template_id', 'version_name', 'notes', 'titles']
        read_only_fields = ['id', 'template_id']

    def get_titles(self, obj):
        return LaborTitleCatalogTitleSerializer(
            obj.titles.all().order_by('category', 'display_order', 'title_code'),
            many=True,
        ).data


class LaborTitleCatalogCreateSerializer(serializers.Serializer):
    """Draft catalog creation body (view services ``create``; no model save here):"""

    version_name = serializers.CharField(max_length=120)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    titles = LaborTitleCatalogTitleSerializer(many=True, required=False)

