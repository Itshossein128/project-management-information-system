from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from common.jalali import persian_day_of_week
from common.serializers import JalaliDateField
from field_reports.models import (
    DailyReport,
    DailyReportActivity,
    DailyReportConcreteLog,
    DailyReportCorrectionRequest,
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
            'wind_speed',
            'soil_condition',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'day_of_week', 'created_at', 'updated_at']

    def validate(self, attrs):
        temp_min = attrs.get('temp_min', getattr(self.instance, 'temp_min', None))
        temp_max = attrs.get('temp_max', getattr(self.instance, 'temp_max', None))
        if temp_min is not None and temp_max is not None and temp_max < temp_min:
            raise serializers.ValidationError(
                {'temp_max': [ErrorDetail('حداکثر دما باید بزرگتر یا مساوی حداقل دما باشد.', code='temp_max_must_be_gte_temp_min')]},
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


def _build_provenance_list(obj, derived_kind, context):
    if not getattr(obj, 'is_derived', False):
        return []
    from field_reports.models import DailyReportDerivedSource

    sources = list(
        DailyReportDerivedSource.objects.filter(
            daily_report_id=getattr(obj, 'report_id', None),
            derived_kind=derived_kind,
            derived_row_id=str(obj.id),
        ).order_by('ordinal', 'id')
    )

    request = context.get('request') if context else None
    user = getattr(request, 'user', None) if request else None
    can_view = False
    if user and user.is_authenticated:
        if user.is_superuser or user.groups.filter(name='admin').exists():
            can_view = True
        else:
            from permissions.project import member_has_codename
            proj_id = getattr(obj, 'project_id', None)
            if not proj_id and getattr(obj, 'report', None):
                proj_id = getattr(obj.report, 'project_id', None)
            if not proj_id and getattr(request, 'project_id', None):
                proj_id = request.project_id
            if proj_id:
                can_view = member_has_codename(user, proj_id, 'view_reports')

    return [
        {
            'unit': s.source_unit,
            'report_id': str(s.source_report_id_snapshot),
            'report_version': s.source_report_version,
            'source_row_kind': s.source_row_kind,
            'source_row_id': s.source_row_id,
            'contribution_value': str(s.contribution_value) if s.contribution_value is not None else None,
            'can_view_source': can_view,
        }
        for s in sources
    ]


class DailyReportActivitySerializer(serializers.ModelSerializer):
    activity_code = serializers.CharField(source='activity_ref.activity_code', read_only=True)
    quantity = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        required=False,
        allow_null=True,
    )
    provenance = serializers.SerializerMethodField()
    # Contract daily-summary-sections-api.md §1.1: contractor label and crew
    # name are separate columns (never merged); `location` maps the zone and
    # keeps unknown (null) distinct from empty ('').
    contractor = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

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
            'contractor_ref',
            'contractor',
            'crew_name',
            'headcount',
            'foreman_count',
            'worker_count',
            'parcel',
            'zone',
            'block',
            'floor',
            'location',
            'location_detail',
            'quantity',
            'quantity_measured',
            'unit',
            'execution_percentage',
            'responsible_user',
            'responsible_name',
            'notes',
            'photo_file',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = ['id', 'source_sub_report', 'source_discipline', 'is_derived', 'provenance']

    def get_contractor(self, obj):
        ref = getattr(obj, 'contractor_ref', None)
        return ref.name if ref else None

    def get_location(self, obj):
        return obj.zone

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'activity', self.context)

    def validate_quantity(self, value):
        from common.unset import coerce_optional_decimal

        if value == '':
            return None
        return coerce_optional_decimal(value) if value is not None else None

    def validate(self, attrs):
        measured = attrs.get(
            'quantity_measured',
            getattr(self.instance, 'quantity_measured', True),
        )
        if 'quantity' in attrs:
            quantity = attrs['quantity']
        elif self.instance is not None:
            quantity = self.instance.quantity
        else:
            quantity = None
        touching_qty = ('quantity' in attrs) or ('quantity_measured' in attrs) or (not self.partial)
        if not measured:
            attrs['quantity'] = None
        elif touching_qty and quantity is None:
            raise serializers.ValidationError({
                'quantity': 'در حالت اندازه‌گیری‌شده مقدار الزامی است',
                'code': 'quantity_unset_invalid',
            })

        from django.core.exceptions import ValidationError as DjangoValidationError
        from projects.contractor_utils import resolve_active_contractor

        report = getattr(self.instance, 'report', None)
        if report is None:
            report = self.context.get('report')
        project_id = getattr(report, 'project_id', None) or self.context.get('project_id')

        contractor = attrs.get('contractor_ref', serializers.empty)
        if contractor is not serializers.empty and contractor is not None and project_id:
            try:
                stakeholder = resolve_active_contractor(
                    project_id=project_id, contractor_id=getattr(contractor, 'pk', contractor)
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    getattr(exc, 'message_dict', {'contractor_ref': list(exc.messages)})
                ) from exc
            attrs['contractor_ref'] = stakeholder
            attrs['subcontractor_name'] = stakeholder.name
            return attrs

        name = ''
        if 'subcontractor_name' in attrs:
            name = str(attrs.get('subcontractor_name') or '').strip()
        elif self.instance is not None:
            name = str(getattr(self.instance, 'subcontractor_name', '') or '').strip()

        clearing_ref = contractor is None
        existing_ref = getattr(self.instance, 'contractor_ref_id', None) if self.instance else None
        if name and (clearing_ref or (contractor is serializers.empty and not existing_ref)):
            if project_id:
                try:
                    stakeholder = resolve_active_contractor(project_id=project_id, name=name)
                except DjangoValidationError as exc:
                    raise serializers.ValidationError(
                        {
                            'contractor_ref': _(
                                'Select a valid active contractor. Register the contractor on '
                                'stakeholders (ذینفعان) first.'
                            )
                        }
                    ) from exc
                attrs['contractor_ref'] = stakeholder
                attrs['subcontractor_name'] = stakeholder.name
            else:
                raise serializers.ValidationError(
                    {
                        'contractor_ref': _(
                            'Select a valid active contractor. Register the contractor on '
                            'stakeholders (ذینفعان) first.'
                        )
                    }
                )
        return attrs


class DailyReportLaborSerializer(serializers.ModelSerializer):
    total_count = serializers.IntegerField(read_only=True)
    provenance = serializers.SerializerMethodField()

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
            'work_hours',
            'overtime_hours',
            'daily_rate',
            'absence_count',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = ['id', 'total_count', 'source_sub_report', 'source_discipline', 'is_derived', 'provenance']
        extra_kwargs = {'absence_count': {'required': False, 'allow_null': True}}

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'labor', self.context)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        project_id = getattr(instance, 'project_id', None)
        if project_id is None and getattr(instance, 'report_id', None):
            project_id = getattr(instance.report, 'project_id', None)
        if request is not None and request.user.is_authenticated and project_id is not None:
            from permissions.project import member_has_codename

            if not member_has_codename(request.user, project_id, 'view_wage'):
                data.pop('daily_rate', None)
        return data


class BaseEquipmentEntrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'id',
            'equipment',
            'equipment_name',
            'equipment_ref',
            'shift',
            'status',
            'ownership_type',
            'work_start',
            'work_end',
            'repair_hours',
            'idle_hours',
            'idle_reason',
            'productive_hours',
            'hourly_rate',
            'fuel_cost',
            'activity_ref',
            'notes',
        ]
        read_only_fields = ['id']


class DailyReportEquipmentSerializer(BaseEquipmentEntrySerializer):
    class Meta(BaseEquipmentEntrySerializer.Meta):
        model = DailyReportEquipment


class DailyReportMaterialSerializer(serializers.ModelSerializer):
    quantity = serializers.DecimalField(max_digits=18, decimal_places=4)
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportMaterial
        fields = [
            'id',
            'material_ref',
            'material_description',
            'quantity',
            'unit_cost',
            'unit',
            'transaction_type',
            'consumption_location',
            'activity_ref',
            'notes',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = ['id', 'source_sub_report', 'source_discipline', 'is_derived', 'provenance']

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'material', self.context)

    def validate_quantity(self, value):
        if value is None or value == '':
            raise serializers.ValidationError(
                'مقدار مصالح نمی‌تواند خالی باشد',
                code='quantity_unset_invalid',
            )
        return value


class DailyReportConcreteLogSerializer(serializers.ModelSerializer):
    provenance = serializers.SerializerMethodField()

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
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = ['id', 'source_sub_report', 'source_discipline', 'is_derived', 'provenance']

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'concrete', self.context)


class BaseLaborCampEntrySerializer(serializers.ModelSerializer):
    class Meta:
        fields = [
            'id',
            'connex_number',
            'subcontractor_name',
            'contractor_ref',
            'total_residents',
            'present_count',
            'on_leave_count',
            'capacity',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'subcontractor_name': {'required': False, 'allow_blank': True},
            'contractor_ref': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        from django.core.exceptions import ValidationError as DjangoValidationError
        from projects.contractor_utils import resolve_active_contractor

        report = getattr(self.instance, 'report', None)
        if report is None:
            report = self.context.get('report')
        project_id = (
            getattr(report, 'project_id', None)
            or getattr(self.instance, 'project_id', None)
            or self.context.get('project_id')
        )

        contractor = attrs.get('contractor_ref', serializers.empty)
        if contractor is not serializers.empty and contractor is not None and project_id:
            try:
                stakeholder = resolve_active_contractor(
                    project_id=project_id,
                    contractor_id=getattr(contractor, 'pk', contractor),
                )
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    getattr(
                        exc,
                        'message_dict',
                        {'contractor_ref': list(exc.messages)},
                    )
                ) from exc
            attrs['contractor_ref'] = stakeholder
            attrs['subcontractor_name'] = stakeholder.name
            return attrs

        name = ''
        if 'subcontractor_name' in attrs:
            name = str(attrs.get('subcontractor_name') or '').strip()
        elif self.instance is not None:
            name = str(getattr(self.instance, 'subcontractor_name', '') or '').strip()

        clearing_ref = contractor is None
        existing_ref = getattr(self.instance, 'contractor_ref_id', None) if self.instance else None
        needs_resolve = clearing_ref or (
            contractor is serializers.empty and not existing_ref
        )

        if needs_resolve:
            if name and project_id:
                try:
                    stakeholder = resolve_active_contractor(
                        project_id=project_id, name=name
                    )
                except DjangoValidationError as exc:
                    raise serializers.ValidationError(
                        {
                            'contractor_ref': _(
                                'Select a valid active contractor. Register the contractor on '
                                'stakeholders (ذینفعان) first.'
                            )
                        }
                    ) from exc
                attrs['contractor_ref'] = stakeholder
                attrs['subcontractor_name'] = stakeholder.name
                return attrs
            if self.instance is None:
                raise serializers.ValidationError(
                    {'contractor_ref': _('This field is required.')}
                )
            if name:
                raise serializers.ValidationError(
                    {
                        'contractor_ref': _(
                            'Select a valid active contractor. Register the contractor on '
                            'stakeholders (ذینفعان) first.'
                        )
                    }
                )

        if name:
            attrs['subcontractor_name'] = name
        return attrs


class DailyReportLaborCampSerializer(BaseLaborCampEntrySerializer):
    class Meta(BaseLaborCampEntrySerializer.Meta):
        model = DailyReportLaborCamp


class DailyReportIncidentSerializer(serializers.ModelSerializer):
    due_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = DailyReportIncident
        fields = [
            'id',
            'incident_type',
            'description',
            'corrective_action',
            'follow_up_owner_user',
            'follow_up_owner_name',
            'due_date',
        ]
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
            'work_front',
            'location_notes',
            'weather_condition',
            'temp_max',
            'temp_min',
            'site_status',
            'inactivity_reason',
            'weather_impact_notes',
            'general_notes',
            'management_opinion',
            'weather_override',
            'site_status_override',
            'local_id',
            'synced_from_offline',
        ]

    def validate(self, attrs):
        temp_min = attrs.get('temp_min', getattr(self.instance, 'temp_min', None))
        temp_max = attrs.get('temp_max', getattr(self.instance, 'temp_max', None))
        if temp_min is not None and temp_max is not None and temp_max < temp_min:
            raise serializers.ValidationError(
                {'temp_max': [ErrorDetail('حداکثر دما باید بزرگتر یا مساوی حداقل دما باشد.', code='temp_max_must_be_gte_temp_min')]},
            )
        site_status = attrs.get('site_status', getattr(self.instance, 'site_status', None))
        inactivity_reason = attrs.get('inactivity_reason', getattr(self.instance, 'inactivity_reason', ''))
        if site_status == 'inactive' and not inactivity_reason:
            raise serializers.ValidationError(
                {'inactivity_reason': [ErrorDetail('در صورت تعطیلی کارگاه، انتخاب علت الزامی است.', code='inactivity_reason_required')]},
            )
        if site_status == 'active':
            attrs['inactivity_reason'] = ''
        return attrs


class DailyReportDetailSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source='id', read_only=True)
    report_date = JalaliDateField()
    day_of_week = serializers.SerializerMethodField()
    weather_condition_label = serializers.SerializerMethodField()
    site_status_label = serializers.CharField(source='get_site_status_display', read_only=True)
    inactivity_reason_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    is_locked = serializers.BooleanField(read_only=True)
    status_label_key = serializers.SerializerMethodField()
    prepared_by_name = serializers.SerializerMethodField()
    submitted_by_name = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()
    supersedes = serializers.UUIDField(source='supersedes_id', read_only=True, allow_null=True)

    activities = serializers.SerializerMethodField()
    labor = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    concrete_logs = serializers.SerializerMethodField()
    labor_camp = serializers.SerializerMethodField()
    incidents = serializers.SerializerMethodField()
    aggregation = serializers.SerializerMethodField()

    class Meta:
        model = DailyReport
        fields = [
            'report_id',
            'report_date',
            'day_of_week',
            'shift',
            'work_front',
            'location_notes',
            'weather_condition',
            'weather_condition_label',
            'temp_max',
            'temp_min',
            'site_status',
            'site_status_label',
            'inactivity_reason',
            'inactivity_reason_label',
            'weather_impact_notes',
            'general_notes',
            'management_opinion',
            'weather_override',
            'site_status_override',
            'is_auto_summary',
            'aggregated_at',
            'aggregation',
            'status',
            'status_label',
            'is_locked',
            'status_label_key',
            'lineage_id',
            'version_number',
            'supersedes',
            'is_current',
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

    def get_aggregation(self, obj):
        from field_reports.services.daily_report_aggregation import build_aggregation_meta

        return build_aggregation_meta(obj.project_id, obj.report_date, report=obj)

    def get_status_label(self, obj):
        if obj.status == 'approved':
            return 'قفل‌شده'
        return obj.get_status_display()

    def get_status_label_key(self, obj):
        if obj.status == 'approved':
            return 'dailyReport.status.locked'
        return f'dailyReport.status.{obj.status}'

    def get_day_of_week(self, obj):
        return persian_day_of_week(obj.report_date) if obj.report_date else ''

    def get_weather_condition_label(self, obj):
        if not obj.weather_condition:
            return None
        try:
            return WeatherCondition(obj.weather_condition).label
        except (ValueError, KeyError):
            return obj.weather_condition

    def get_inactivity_reason_label(self, obj):
        if not getattr(obj, 'inactivity_reason', None):
            return None
        try:
            from field_reports.models import InactivityReason
            return InactivityReason(obj.inactivity_reason).label
        except (ValueError, KeyError):
            return obj.inactivity_reason

    def get_prepared_by_name(self, obj):
        return _user_name(obj.prepared_by)

    def get_submitted_by_name(self, obj):
        return _user_name(obj.submitted_by)

    def get_reviewed_by_name(self, obj):
        return _user_name(obj.reviewed_by)

    def get_approved_by_name(self, obj):
        return _user_name(obj.approved_by)

    def _active(self, manager):
        return [item for item in manager.all() if not item.is_deleted]

    def get_activities(self, obj):
        return DailyReportActivitySerializer(self._active(obj.activities), many=True, context=self.context).data

    def get_labor(self, obj):
        return DailyReportLaborSerializer(self._active(obj.labor_entries), many=True, context=self.context).data

    def get_equipment(self, obj):
        return DailyReportEquipmentSerializer(self._active(obj.equipment_entries), many=True, context=self.context).data

    def get_materials(self, obj):
        return DailyReportMaterialSerializer(self._active(obj.material_entries), many=True, context=self.context).data

    def get_concrete_logs(self, obj):
        return DailyReportConcreteLogSerializer(self._active(obj.concrete_logs), many=True, context=self.context).data

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
    inactivity_reason_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    is_locked = serializers.BooleanField(read_only=True)
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
            'work_front',
            'site_status',
            'site_status_label',
            'inactivity_reason',
            'inactivity_reason_label',
            'weather_condition',
            'weather_condition_label',
            'status',
            'status_label',
            'is_locked',
            'is_current',
            'version_number',
            'prepared_by_name',
            'approved_by_name',
            'activity_count',
            'labor_total',
            'equipment_count',
            'has_incidents',
        ]

    def get_status_label(self, obj):
        if obj.status == 'approved':
            return 'قفل‌شده'
        return obj.get_status_display()

    def get_day_of_week(self, obj):
        return persian_day_of_week(obj.report_date) if obj.report_date else ''

    def get_weather_condition_label(self, obj):
        if not obj.weather_condition:
            return None
        try:
            return WeatherCondition(obj.weather_condition).label
        except (ValueError, KeyError):
            return obj.weather_condition

    def get_inactivity_reason_label(self, obj):
        if not getattr(obj, 'inactivity_reason', None):
            return None
        try:
            from field_reports.models import InactivityReason
            return InactivityReason(obj.inactivity_reason).label
        except (ValueError, KeyError):
            return obj.inactivity_reason

    def get_prepared_by_name(self, obj):
        return _user_name(obj.prepared_by)

    def get_approved_by_name(self, obj):
        return _user_name(obj.approved_by)

    def get_activity_count(self, obj):
        return sum(1 for activity in obj.activities.all() if not activity.is_deleted)

    def get_labor_total(self, obj):
        return sum(
            row.total_count for row in obj.labor_entries.all() if not row.is_deleted
        )

    def get_equipment_count(self, obj):
        return sum(1 for equipment in obj.equipment_entries.all() if not equipment.is_deleted)

    def get_has_incidents(self, obj):
        return any(not incident.is_deleted for incident in obj.incidents.all())


class DailyReportCorrectionRequestSerializer(serializers.ModelSerializer):
    source_report_id = serializers.UUIDField(read_only=True)
    result_report_id = serializers.UUIDField(read_only=True, allow_null=True)

    class Meta:
        model = DailyReportCorrectionRequest
        fields = [
            'id',
            'source_report_id',
            'result_report_id',
            'reason',
            'status',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'decision_notes',
            'created_at',
        ]
        read_only_fields = fields


class DailyReportVersionSerializer(serializers.ModelSerializer):
    report_id = serializers.UUIDField(source='id', read_only=True)
    report_date = JalaliDateField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = DailyReport
        fields = [
            'report_id',
            'report_date',
            'shift',
            'version_number',
            'is_current',
            'status',
            'is_locked',
            'approved_at',
            'created_at',
        ]
