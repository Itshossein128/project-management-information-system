from rest_framework import serializers

from common.serializers import JalaliDateField
from sub_reports.models import DisciplineSubReport, DisciplineSubReportActivity


class SubReportActivitySerializer(serializers.ModelSerializer):
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


class DisciplineSubReportSerializer(serializers.ModelSerializer):
    report_date = JalaliDateField()
    activities = SubReportActivitySerializer(many=True, required=False)
    activity_count = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReport
        fields = [
            'id',
            'report_date',
            'discipline',
            'weather_condition',
            'form_code',
            'revision_number',
            'status',
            'linked_daily_report',
            'activities',
            'activity_count',
            'rejection_reason',
        ]
        read_only_fields = ['id', 'status']

    def get_activity_count(self, obj):
        # ⚡ Bolt: Use python iteration over prefetched collection to avoid N+1 queries from .filter()
        return sum(1 for activity in obj.activities.all() if not activity.is_deleted)

    def create(self, validated_data):
        activities = validated_data.pop('activities', [])
        report = DisciplineSubReport.objects.create(**validated_data)
        for row in activities:
            DisciplineSubReportActivity.objects.create(sub_report=report, **row)
        return report

    def update(self, instance, validated_data):
        activities = validated_data.pop('activities', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if activities is not None:
            instance.activities.filter(is_deleted=False).update(is_deleted=True)
            for row in activities:
                DisciplineSubReportActivity.objects.create(sub_report=instance, **row)
        return instance
