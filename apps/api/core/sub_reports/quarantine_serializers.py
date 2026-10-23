from rest_framework import serializers

from sub_reports.models import UnitReportMigrationQuarantine


class UnitReportMigrationQuarantineSerializer(serializers.ModelSerializer):
    source_system = serializers.CharField(source='trace.source_system', read_only=True)
    source_model = serializers.CharField(source='trace.source_model', read_only=True)
    source_id = serializers.CharField(source='trace.source_id', read_only=True)
    disposition = serializers.CharField(source='trace.disposition', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)

    class Meta:
        model = UnitReportMigrationQuarantine
        fields = [
            'id',
            'trace_id',
            'source_system',
            'source_model',
            'source_id',
            'disposition',
            'reason_code',
            'raw_category',
            'raw_payload',
            'detected_at',
            'resolved_by',
            'resolved_by_name',
            'resolved_at',
            'resolution_notes',
        ]
        read_only_fields = [
            'id',
            'trace_id',
            'source_system',
            'source_model',
            'source_id',
            'disposition',
            'reason_code',
            'raw_category',
            'raw_payload',
            'detected_at',
            'resolved_by',
            'resolved_by_name',
            'resolved_at',
        ]
