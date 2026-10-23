from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.serializers import JalaliDateField
from projects.models import Activity, Stakeholder
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
)
from sub_reports.section_rules import resolve_shift


class SubReportActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for DisciplineSubReportActivity.
    Handles serialization of individual activities, ensuring `id` is read-only.
    """
    class Meta:
        model = DisciplineSubReportActivity
        fields = [
            'id',
            'row_number',
            'shift',
            'crew_name',
            'foreman_count',
            'worker_count',
            'zone',
            'block',
            'floor',
            'activity_description',
            'unit',
            'quantity',
            'execution_percentage',
            'activity_ref',
        ]
        read_only_fields = ['id']


class UnitReportActivitySectionSerializer(serializers.ModelSerializer):
    """Canonical unit-report §1 activity rows (feature 033, task T014).

    Enforces the §1 contract at the serializer layer: the recognized shift
    vocabulary with synonyms (no silent fallback), project-scoped activity and
    contractor references (fielded stable codes), and a strictly positive
    quantity when provided. `headcount` is derived and read-only; the model
    maintains it as foreman_count + worker_count in save().
    """

    row_number = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    # Not a ChoiceField: synonyms must resolve through validate_shift (no
    # silent fallback — anything unrecognized is refused, FR-003).
    shift = serializers.CharField(required=True, allow_blank=True)
    crew_name = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    headcount = serializers.IntegerField(read_only=True)
    quantity = serializers.DecimalField(
        max_digits=18, decimal_places=4, required=False, allow_null=True,
    )
    activity_ref = serializers.PrimaryKeyRelatedField(
        queryset=Activity.objects.all(),
        required=True,
        allow_null=False,
    )
    activity_code = serializers.CharField(source='activity_ref.activity_code', read_only=True)
    activity_name = serializers.CharField(source='activity_ref.activity_name', read_only=True)
    contractor_ref = serializers.PrimaryKeyRelatedField(
        queryset=Stakeholder.objects.all(),
        required=True,
        allow_null=False,
    )
    contractor_name = serializers.CharField(source='contractor_ref.name', read_only=True)
    foreman_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    worker_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    activity_description = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = DisciplineSubReportActivity
        fields = [
            'id',
            'row_number',
            'shift',
            'crew_name',
            'foreman_count',
            'worker_count',
            'headcount',
            'activity_ref',
            'activity_code',
            'activity_name',
            'activity_description',
            'contractor_ref',
            'contractor_name',
            'parcel',
            'zone',
            'block',
            'floor',
            'quantity',
            'unit',
            'notes',
        ]

    def validate_shift(self, raw):
        resolved = resolve_shift(raw)
        if resolved is None:
            raise serializers.ValidationError(
                _('شناسه شیفت نامعتبر است؛ یکی از شیفت‌های ۱ تا ۳ را انتخاب کنید'),
                code='invalid_shift',
            )
        return resolved

    def validate_quantity(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                _('مقدار باید بزرگ‌تر از صفر باشد'),
                code='quantity_must_be_positive',
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not (attrs.get('activity_description') or '').strip():
            act = attrs.get('activity_ref') or getattr(self.instance, 'activity_ref', None)
            if act is not None and getattr(act, 'activity_name', None):
                attrs['activity_description'] = act.activity_name
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field in ('activity_ref', 'contractor_ref'):
            if data.get(field) is not None:
                data[field] = str(data[field])
        return data


class SubReportLaborSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineSubReportLabor
        fields = ['id', 'labor_category', 'job_title', 'present_count', 'leave_count']
        read_only_fields = ['id']


class SubReportMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineSubReportMaterial
        fields = ['id', 'material_description', 'quantity', 'unit', 'notes']
        read_only_fields = ['id']


class SubReportConcreteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineSubReportConcrete
        fields = [
            'id', 'concrete_description', 'volume_m3', 'zone', 'block', 'floor', 'notes',
        ]
        read_only_fields = ['id']


class SubReportGeneralActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineSubReportGeneralActivity
        fields = [
            'id', 'activity_description', 'location', 'quantity', 'unit', 'notes',
        ]
        read_only_fields = ['id']


class SubReportNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineSubReportNote
        fields = ['id', 'note_type', 'text', 'row_number']
        read_only_fields = ['id']


class DisciplineSubReportSerializer(serializers.ModelSerializer):
    """
    Serializer for DisciplineSubReport.
    Handles creation and modification of a sub-report and its nested activities.
    """
    report_date = JalaliDateField()
    activities = SubReportActivitySerializer(many=True, required=False)
    labor_entries = SubReportLaborSerializer(many=True, required=False)
    material_entries = SubReportMaterialSerializer(many=True, required=False)
    concrete_entries = SubReportConcreteSerializer(many=True, required=False)
    general_activities = SubReportGeneralActivitySerializer(many=True, required=False)
    notes = SubReportNoteSerializer(many=True, required=False)
    activity_count = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReport
        fields = [
            'id',
            'report_date',
            'discipline',
            'weather_condition',
            'site_status',
            'form_code',
            'revision_number',
            'status',
            'linked_daily_report',
            'activities',
            'labor_entries',
            'material_entries',
            'concrete_entries',
            'general_activities',
            'notes',
            'activity_count',
            'rejection_reason',
        ]
        read_only_fields = ['id', 'status']

    def get_activity_count(self, obj):
        # ⚡ Bolt: Use python iteration over prefetched collection to avoid N+1 queries from .filter()
        return sum(1 for activity in obj.activities.all() if not activity.is_deleted)

    def _create_nested(self, report, nested: dict):
        for row in nested.get('activities') or []:
            DisciplineSubReportActivity.objects.create(sub_report=report, **row)
        for row in nested.get('labor_entries') or []:
            DisciplineSubReportLabor.objects.create(sub_report=report, **row)
        for row in nested.get('material_entries') or []:
            DisciplineSubReportMaterial.objects.create(sub_report=report, **row)
        for row in nested.get('concrete_entries') or []:
            DisciplineSubReportConcrete.objects.create(sub_report=report, **row)
        for row in nested.get('general_activities') or []:
            DisciplineSubReportGeneralActivity.objects.create(sub_report=report, **row)
        for row in nested.get('notes') or []:
            DisciplineSubReportNote.objects.create(sub_report=report, **row)

    def create(self, validated_data):
        """
        Creates a DisciplineSubReport along with its associated DisciplineSubReportActivities.
        """
        nested_keys = (
            'activities', 'labor_entries', 'material_entries',
            'concrete_entries', 'general_activities', 'notes',
        )
        nested = {k: validated_data.pop(k, []) for k in nested_keys}
        report = DisciplineSubReport.objects.create(**validated_data)
        self._create_nested(report, nested)
        return report

    def update(self, instance, validated_data):
        """
        Updates a DisciplineSubReport instance. If new activities are provided,
        existing un-deleted activities are soft-deleted, and the new ones are created.
        """
        nested_keys = (
            'activities', 'labor_entries', 'material_entries',
            'concrete_entries', 'general_activities', 'notes',
        )
        nested = {k: validated_data.pop(k, None) for k in nested_keys}
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        managers = {
            'activities': (instance.activities, DisciplineSubReportActivity),
            'labor_entries': (instance.labor_entries, DisciplineSubReportLabor),
            'material_entries': (instance.material_entries, DisciplineSubReportMaterial),
            'concrete_entries': (instance.concrete_entries, DisciplineSubReportConcrete),
            'general_activities': (instance.general_activities, DisciplineSubReportGeneralActivity),
            'notes': (instance.notes, DisciplineSubReportNote),
        }
        for key, rows in nested.items():
            if rows is None:
                continue
            manager, model = managers[key]
            manager.filter(is_deleted=False).update(is_deleted=True)
            for row in rows:
                model.objects.create(sub_report=instance, **row)
        return instance
