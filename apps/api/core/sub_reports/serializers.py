from rest_framework import serializers

from common.serializers import JalaliDateField
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMaterial,
    DisciplineSubReportNote,
)


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
