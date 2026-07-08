from rest_framework import serializers

from common.jalali import persian_day_of_week
from common.serializers import JalaliDateField
from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportEquipment,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportLaborCamp,
    DailyReportMaterial,
    LaborJobTitle,
    SiteStatus,
    WeatherCondition,
    WeatherLog,
)


# ---------------------------------------------------------------------------
# Weather logs (existing)
# ---------------------------------------------------------------------------


class WeatherLogSerializer(serializers.ModelSerializer):
    log_date = JalaliDateField()
    day_of_week = serializers.CharField(read_only=True)
    weather_condition_label = serializers.CharField(
        source='get_weather_condition_display',
        read_only=True,
    )
    site_status_label = serializers.CharField(
        source='get_site_status_display',
        read_only=True,
    )

    class Meta:
        model = WeatherLog
        fields = [
            'id',
            'log_date',
            'day_of_week',
            'temp_max',
            'temp_min',
            'weather_condition',
            'weather_condition_label',
            'site_status',
            'site_status_label',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'day_of_week', 'created_at', 'updated_at']

    def validate(self, attrs):
        temp_min = attrs.get('temp_min', getattr(self.instance, 'temp_min', None))
        temp_max = attrs.get('temp_max', getattr(self.instance, 'temp_max', None))
        if temp_min is not None and temp_max is not None and temp_min > temp_max:
            raise serializers.ValidationError(
                {'temp_min': 'حداقل دما نمی‌تواند بیشتر از حداکثر دما باشد.'},
            )
        log_date = attrs.get('log_date', getattr(self.instance, 'log_date', None))
        if log_date:
            attrs['day_of_week'] = persian_day_of_week(log_date)
        return attrs


class WeatherLogCreateSerializer(WeatherLogSerializer):
    class Meta(WeatherLogSerializer.Meta):
        pass


# ---------------------------------------------------------------------------
# Labor reference titles
# ---------------------------------------------------------------------------


class LaborJobTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LaborJobTitle
        fields = ['id', 'category', 'title', 'display_order']


# ---------------------------------------------------------------------------
# Daily report child rows
# ---------------------------------------------------------------------------


class DailyReportActivitySerializer(serializers.ModelSerializer):
    activity_code = serializers.CharField(source='activity_ref.activity_code', read_only=True)

    class Meta:
        model = DailyReportActivity
        fields = [
            'id',
            'activity_ref',
            'activity_code',
            'activity_description',
            'shift',
            'subcontractor_name',
            'subcontractor_ref',
            'headcount',
            'zone',
            'block',
            'floor',
            'location_detail',
            'quantity',
            'quantity_measured',
            'unit',
            'execution_percentage',
            'notes',
        ]
        read_only_fields = ['id']


class DailyReportLaborSerializer(serializers.ModelSerializer):
    total_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = DailyReportLabor
        fields = [
            'id',
            'labor_category',
            'job_title',
            'custom_title',
            'shift_1_count',
            'shift_2_count',
            'shift_3_count',
            'total_count',
        ]
        read_only_fields = ['id', 'total_count']


class DailyReportEquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReportEquipment
        fields = [
            'id',
            'equipment_name',
            'equipment_ref',
            'shift',
            'status',
            'ownership_type',
            'work_start',
            'work_end',
            'repair_hours',
            'productive_hours',
            'activity_ref',
            'notes',
        ]
        read_only_fields = ['id']


class DailyReportMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReportMaterial
        fields = [
            'id',
            'material_ref',
            'material_description',
            'quantity',
            'unit',
            'transaction_type',
            'activity_ref',
            'notes',
        ]
        read_only_fields = ['id']


class DailyReportConcreteLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReportConcreteLog
        fields = [
            'id',
            'concrete_description',
            'volume_m3',
            'activity_ref',
            'zone',
            'block',
            'floor',
            'notes',
        ]
        read_only_fields = ['id']


class DailyReportLaborCampSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReportLaborCamp
        fields = [
            'id',
            'connex_number',
            'subcontractor_name',
            'total_residents',
            'present_count',
            'on_leave_count',
            'capacity',
        ]
        read_only_fields = ['id']


class DailyReportIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReportIncident
        fields = ['id', 'incident_type', 'description', 'corrective_action']
        read_only_fields = ['id']


# ---------------------------------------------------------------------------
# Daily report header / detail
# ---------------------------------------------------------------------------


def _user_name(user):
    if not user:
        return None
    full = getattr(user, 'get_full_name', lambda: '')() or ''
    return full or getattr(user, 'username', None)


class DailyReportHeaderSerializer(serializers.ModelSerializer):
    """Create / update of header fields only."""

    report_id = serializers.UUIDField(source='id', read_only=True)
    report_date = JalaliDateField()

    class Meta:
        model = DailyReport
        fields = [
            'report_id',
            'report_date',
            'shift',
            'weather_condition',
            'temp_max',
            'temp_min',
            'site_status',
            'general_notes',
            'local_id',
            'synced_from_offline',
        ]

    def validate(self, attrs):
        temp_min = attrs.get('temp_min', getattr(self.instance, 'temp_min', None))
        temp_max = attrs.get('temp_max', getattr(self.instance, 'temp_max', None))
        if temp_min is not None and temp_max is not None and temp_min > temp_max:
            raise serializers.ValidationError(
                {'temp_min': 'حداقل دما نمی‌تواند بیشتر از حداکثر دما باشد.'},
            )
        return attrs


class DailyReportDetailSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source='id', read_only=True)
    report_date = JalaliDateField()
    day_of_week = serializers.SerializerMethodField()
    weather_condition_label = serializers.SerializerMethodField()
    site_status_label = serializers.CharField(source='get_site_status_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    prepared_by_name = serializers.SerializerMethodField()
    submitted_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    activities = serializers.SerializerMethodField()
    labor = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    concrete_logs = serializers.SerializerMethodField()
    labor_camp = serializers.SerializerMethodField()
    incidents = serializers.SerializerMethodField()

    class Meta:
        model = DailyReport
        fields = [
            'report_id',
            'report_date',
            'day_of_week',
            'shift',
            'weather_condition',
            'weather_condition_label',
            'temp_max',
            'temp_min',
            'site_status',
            'site_status_label',
            'general_notes',
            'status',
            'status_label',
            'prepared_by',
            'prepared_by_name',
            'submitted_by',
            'submitted_by_name',
            'reviewed_by',
            'reviewed_by_name',
            'approved_by',
            'approved_by_name',
            'submitted_at',
            'reviewed_at',
            'approved_at',
            'rejection_reason',
            'synced_from_offline',
            'local_id',
            'created_at',
            'updated_at',
            'activities',
            'labor',
            'equipment',
            'materials',
            'concrete_logs',
            'labor_camp',
            'incidents',
        ]

    def get_day_of_week(self, obj):
        return persian_day_of_week(obj.report_date) if obj.report_date else ''

    def get_weather_condition_label(self, obj):
        if not obj.weather_condition:
            return None
        return WeatherCondition(obj.weather_condition).label

    def get_prepared_by_name(self, obj):
        return _user_name(obj.prepared_by)

    def get_submitted_by_name(self, obj):
        return _user_name(obj.submitted_by)

    def get_reviewed_by_name(self, obj):
        return _user_name(obj.reviewed_by)

    def get_approved_by_name(self, obj):
        return _user_name(obj.approved_by)

    def _active(self, manager):
        return manager.filter(is_deleted=False)

    def get_activities(self, obj):
        return DailyReportActivitySerializer(self._active(obj.activities), many=True).data

    def get_labor(self, obj):
        return DailyReportLaborSerializer(self._active(obj.labor_entries), many=True).data

    def get_equipment(self, obj):
        return DailyReportEquipmentSerializer(self._active(obj.equipment_entries), many=True).data

    def get_materials(self, obj):
        return DailyReportMaterialSerializer(self._active(obj.material_entries), many=True).data

    def get_concrete_logs(self, obj):
        return DailyReportConcreteLogSerializer(self._active(obj.concrete_logs), many=True).data

    def get_labor_camp(self, obj):
        return DailyReportLaborCampSerializer(self._active(obj.labor_camp_entries), many=True).data

    def get_incidents(self, obj):
        return DailyReportIncidentSerializer(self._active(obj.incidents), many=True).data


class DailyReportListSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source='id', read_only=True)
    report_date = JalaliDateField(read_only=True)
    day_of_week = serializers.SerializerMethodField()
    weather_condition_label = serializers.SerializerMethodField()
    site_status_label = serializers.CharField(source='get_site_status_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    prepared_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    activity_count = serializers.SerializerMethodField()
    labor_total = serializers.SerializerMethodField()
    equipment_count = serializers.SerializerMethodField()
    has_incidents = serializers.SerializerMethodField()

    class Meta:
        model = DailyReport
        fields = [
            'report_id',
            'report_date',
            'day_of_week',
            'site_status',
            'site_status_label',
            'weather_condition',
            'weather_condition_label',
            'status',
            'status_label',
            'prepared_by_name',
            'approved_by_name',
            'activity_count',
            'labor_total',
            'equipment_count',
            'has_incidents',
        ]

    def get_day_of_week(self, obj):
        return persian_day_of_week(obj.report_date) if obj.report_date else ''

    def get_weather_condition_label(self, obj):
        if not obj.weather_condition:
            return None
        return WeatherCondition(obj.weather_condition).label

    def get_prepared_by_name(self, obj):
        return _user_name(obj.prepared_by)

    def get_approved_by_name(self, obj):
        return _user_name(obj.approved_by)

    def get_activity_count(self, obj):
        return obj.activities.filter(is_deleted=False).count()

    def get_labor_total(self, obj):
        return sum(
            row.total_count for row in obj.labor_entries.filter(is_deleted=False)
        )

    def get_equipment_count(self, obj):
        return obj.equipment_entries.filter(is_deleted=False).count()

    def get_has_incidents(self, obj):
        return obj.incidents.filter(is_deleted=False).exists()
