from decimal import Decimal

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
    DailyReportGeneralActivity,
    DailyReportIncident,
    DailyReportLabor,
    DailyReportLaborCamp,
    DailyReportMachineryRow,
    DailyReportMaterial,
    DailyReportVisit,
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


def _build_provenance_list(obj, derived_kind, context, *, allow_source_report=False):
    if not getattr(obj, 'is_derived', False) and not (
        allow_source_report and getattr(obj, 'source_report_id', None)
    ):
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
        if not measured:
            attrs['quantity'] = None

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
    present_count = serializers.IntegerField(source='total_count', read_only=True)
    leave_count = serializers.SerializerMethodField()
    man_hours = serializers.SerializerMethodField()
    title_code = serializers.SerializerMethodField()
    display_order = serializers.SerializerMethodField()
    source_count = serializers.SerializerMethodField()
    has_multiple_sources = serializers.SerializerMethodField()
    per_unit_breakdown = serializers.SerializerMethodField()
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportLabor
        fields = [
            'id',
            'labor_category',
            'job_title',
            'custom_title',
            'contractor_ref',
            'contractor_name',
            'title_code',
            'display_order',
            'present_count',
            'leave_count',
            'shift_1_count',
            'shift_2_count',
            'shift_3_count',
            'total_count',
            'work_hours',
            'overtime_hours',
            'man_hours',
            'daily_rate',
            'absence_count',
            'source_set_complete',
            'source_count',
            'has_multiple_sources',
            'per_unit_breakdown',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = [
            'id',
            'title_code',
            'display_order',
            'present_count',
            'leave_count',
            'total_count',
            'man_hours',
            'source_set_complete',
            'source_count',
            'has_multiple_sources',
            'per_unit_breakdown',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        extra_kwargs = {'absence_count': {'required': False, 'allow_null': True}}

    def _effective_config(self, obj):
        cache = self.context.setdefault('_labor_config_cache', {})
        project_id = getattr(obj, 'project_id', None) or (
            getattr(obj.report, 'project_id', None) if getattr(obj, 'report_id', None) else None
        )
        report_date = getattr(obj, 'report_date', None) or (
            getattr(obj.report, 'report_date', None) if getattr(obj, 'report_id', None) else None
        )
        if not project_id or not report_date:
            return None
        key = (str(project_id), str(report_date))
        if key not in cache:
            report = getattr(obj, 'report', None)
            if report is not None and getattr(report, 'reporting_configuration_id', None):
                cache[key] = report.reporting_configuration
            else:
                from field_reports.services.daily_report_aggregation import (
                    resolve_project_reporting_configuration,
                )

                cache[key] = resolve_project_reporting_configuration(project_id, report_date)
        return cache[key]

    def _resolved_title(self, obj):
        config = self._effective_config(obj)
        if config is None:
            return None
        from project_templates.services import resolve_labor_title

        return resolve_labor_title(config, getattr(obj, 'job_title', '') or '')

    def get_leave_count(self, obj) -> int:
        return int(obj.absence_count or 0)

    def get_title_code(self, obj) -> str:
        resolved = self._resolved_title(obj)
        return resolved.title_code if resolved else ''

    def get_display_order(self, obj) -> int:
        resolved = self._resolved_title(obj)
        return resolved.display_order if resolved else 0

    def get_man_hours(self, obj) -> str:
        from decimal import Decimal
        from field_reports.services.man_hours import compute_man_hours

        if obj.work_hours is not None:
            return f"{Decimal(str(obj.work_hours)):.2f}"
        config = self._effective_config(obj)
        rule_code = config.man_hours_rule_code if config else None
        shift_hours = config.standard_shift_hours if config else Decimal('8')
        val = compute_man_hours(
            rule_code,
            present_count=obj.total_count,
            overtime_person_hours=obj.overtime_hours,
            standard_shift_hours=shift_hours,
        )
        return f"{val:.2f}"

    def _sources(self, obj):
        from field_reports.models import DailyReportDerivedSource

        cache = self.context.setdefault('_labor_sources_cache', {})
        key = str(obj.id)
        if key not in cache:
            if not getattr(obj, 'report_id', None):
                cache[key] = []
            else:
                cache[key] = list(
                    DailyReportDerivedSource.objects.filter(
                        daily_report_id=obj.report_id,
                        derived_kind='labor',
                        derived_row_id=str(obj.id),
                    )
                    .select_related('source_report')
                    .order_by('ordinal', 'id')
                )
        return cache[key]

    def get_source_count(self, obj) -> int:
        return len(self._sources(obj))

    def get_has_multiple_sources(self, obj) -> bool:
        return len(self._sources(obj)) > 1

    def get_per_unit_breakdown(self, obj) -> list[dict]:
        from decimal import Decimal
        from field_reports.services.man_hours import compute_man_hours
        from sub_reports.models import DisciplineSubReportLabor

        sources = self._sources(obj)
        if not sources:
            return []
        config = self._effective_config(obj)
        rule_code = config.man_hours_rule_code if config else None
        shift_hours = config.standard_shift_hours if config else Decimal('8')
        row_ids = [s.source_row_id for s in sources if s.source_row_id]
        source_rows_map = {
            str(r.id): r
            for r in DisciplineSubReportLabor.objects.filter(id__in=row_ids).select_related('contractor_ref')
        }
        breakdown = []
        for src in sources:
            s_row = source_rows_map.get(str(src.source_row_id))
            present = s_row.present_count if s_row is not None else int(src.contribution_value or 0)
            leave = s_row.leave_count if s_row is not None else 0
            overtime = Decimal(str(s_row.overtime_hours if s_row is not None else 0))
            mh = compute_man_hours(
                rule_code,
                present_count=present,
                overtime_person_hours=overtime,
                standard_shift_hours=shift_hours,
            )
            breakdown.append({
                'source_unit': src.source_unit,
                'source_report_id': str(src.source_report_id_snapshot),
                'source_report_version': src.source_report_version,
                'source_row_id': src.source_row_id,
                'present_count': present,
                'leave_count': leave,
                'overtime_hours': f"{overtime:.2f}",
                'man_hours': f"{mh:.2f}",
                'contractor_ref': str(s_row.contractor_ref_id) if (s_row and s_row.contractor_ref_id) else None,
                'contractor_name': s_row.contractor_ref.name if (s_row and s_row.contractor_ref) else None,
            })
        return breakdown

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


class DailyReportMachineryRowSerializer(serializers.ModelSerializer):
    equipment_code = serializers.SerializerMethodField()
    equipment_name = serializers.SerializerMethodField()
    stoppage_reason = serializers.SerializerMethodField()
    stoppage_reason_label = serializers.SerializerMethodField()
    stoppage_reason_label_fa = serializers.SerializerMethodField()
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportMachineryRow
        fields = [
            'id',
            'equipment_type',
            'equipment_ref',
            'equipment_code',
            'equipment_name',
            'status_total',
            'status_active',
            'status_ready',
            'status_inactive',
            'status_under_repair',
            'operating_hours',
            'stoppage_hours',
            'repair_hours',
            'stoppage_reason_code',
            'stoppage_reason',
            'stoppage_reason_label',
            'stoppage_reason_label_fa',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = fields

    def get_equipment_code(self, obj) -> str | None:
        ref = getattr(obj, 'equipment_ref', None)
        return getattr(ref, 'equipment_code', None) if ref is not None else None

    def get_equipment_name(self, obj) -> str | None:
        ref = getattr(obj, 'equipment_ref', None)
        return getattr(ref, 'equipment_name', None) if ref is not None else None

    def _effective_config(self, obj):
        cache = self.context.setdefault('_machinery_config_cache', {})
        report = getattr(obj, 'report', None)
        if report is None:
            return None
        key = str(report.id)
        if key not in cache:
            if getattr(report, 'reporting_configuration_id', None):
                cache[key] = report.reporting_configuration
            else:
                from field_reports.services.daily_report_aggregation import (
                    resolve_project_reporting_configuration,
                )

                cache[key] = resolve_project_reporting_configuration(
                    report.project_id, report.report_date,
                )
        return cache[key]

    def _resolve_reason(self, obj):
        code = (getattr(obj, 'stoppage_reason_code', None) or '').strip()
        if not code:
            return None
        config = self._effective_config(obj)
        from project_templates.services import resolve_stoppage_reason

        entry = resolve_stoppage_reason(config, code) if config is not None else None
        if entry is not None:
            return {
                'code': entry.reason_code,
                'label': entry.reason_label or entry.reason_code,
                'label_fa': entry.reason_label_fa or entry.reason_label or entry.reason_code,
            }
        return {
            'code': code,
            'label': code,
            'label_fa': code,
        }

    def get_stoppage_reason(self, obj) -> dict | None:
        return self._resolve_reason(obj)

    def get_stoppage_reason_label(self, obj) -> str:
        resolved = self._resolve_reason(obj)
        return resolved['label'] if resolved else ''

    def get_stoppage_reason_label_fa(self, obj) -> str:
        resolved = self._resolve_reason(obj)
        return resolved['label_fa'] if resolved else ''

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'machinery', self.context)



class DailyReportMaterialSerializer(serializers.ModelSerializer):
    quantity = serializers.DecimalField(max_digits=18, decimal_places=4)
    material_code = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()
    receipt_evidence = serializers.SerializerMethodField()
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportMaterial
        fields = [
            'id',
            'material_ref',
            'material_code',
            'material_name',
            'material_description',
            'quantity',
            'unit_cost',
            'unit',
            'transaction_type',
            'consumption_location',
            'supplier',
            'warehouse_document_reference',
            'receipt_resolved',
            'receipt_evidence',
            'reconciliation_status',
            'reconciliation_document_id',
            'reconciliation_checked_at',
            'activity_ref',
            'notes',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = [
            'id',
            'material_code',
            'material_name',
            'receipt_resolved',
            'receipt_evidence',
            'reconciliation_status',
            'reconciliation_document_id',
            'reconciliation_checked_at',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]

    def get_material_code(self, obj) -> str | None:
        ref = getattr(obj, 'material_ref', None)
        return getattr(ref, 'material_code', None) if ref is not None else None

    def get_material_name(self, obj) -> str | None:
        ref = getattr(obj, 'material_ref', None)
        return getattr(ref, 'material_name', None) if ref is not None else None

    def get_receipt_evidence(self, obj) -> str | None:
        if getattr(obj, 'transaction_type', None) != 'receipt':
            return None
        return 'resolved' if getattr(obj, 'receipt_resolved', None) is True else 'unresolved_reference'

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
            'structural_element',
            'parcel',
            'batching_plant',
            'truck_delivery_note_number',
            'lab_sample_code',
            'sampling_state',
            'test_sheet_count',
            'qc_inspection',
            'qc_link',
            'source_sub_report',
            'source_discipline',
            'is_derived',
            'provenance',
        ]
        read_only_fields = [
            'id', 'source_sub_report', 'source_discipline', 'is_derived', 'provenance', 'qc_link',
        ]

    qc_link = serializers.SerializerMethodField()

    def get_qc_link(self, obj):
        if not obj.qc_inspection_id:
            return None
        return {
            'id': str(obj.qc_inspection_id),
            'href': f'/api/v1/projects/{obj.report.project_id}/inspections/{obj.qc_inspection_id}/',
        }

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


class DailyReportGeneralActivitySerializer(serializers.ModelSerializer):
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportGeneralActivity
        fields = [
            'id', 'row_number', 'activity_description', 'location', 'quantity',
            'unit', 'notes', 'source_sub_report', 'source_discipline',
            'is_derived', 'provenance',
        ]
        read_only_fields = fields

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'general_activity', self.context)


class DailyReportVisitSerializer(serializers.ModelSerializer):
    provenance = serializers.SerializerMethodField()

    class Meta:
        model = DailyReportVisit
        fields = [
            'id', 'row_number', 'text', 'source_sub_report', 'source_discipline',
            'is_derived', 'provenance',
        ]
        read_only_fields = fields

    def get_provenance(self, obj):
        return _build_provenance_list(obj, 'visit', self.context)


class DailyReportIncidentSerializer(serializers.ModelSerializer):
    due_date = JalaliDateField(required=False, allow_null=True)
    provenance = serializers.SerializerMethodField()

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
            'severity',
            'notification_id',
            'row_number',
            'source_report',
            'source_row_id',
            'provenance',
        ]
        read_only_fields = [
            'id', 'notification_id', 'row_number', 'source_report', 'source_row_id',
            'provenance',
        ]

    def get_provenance(self, obj):
        # Incident rows predate the generic ``is_derived`` flag; their source
        # report is the authoritative marker for summary-derived form.
        kind = 'hse_incident' if obj.incident_type == 'safety' else 'issue'
        return _build_provenance_list(
            obj, kind, self.context, allow_source_report=True,
        )


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
    labor_summary = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    machinery_rows = serializers.SerializerMethodField()
    machinery = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()
    materials_summary = serializers.SerializerMethodField()
    concrete_logs = serializers.SerializerMethodField()
    labor_camp = serializers.SerializerMethodField()
    incidents = serializers.SerializerMethodField()
    general_activities = serializers.SerializerMethodField()
    visits = serializers.SerializerMethodField()
    issues = serializers.SerializerMethodField()
    hse_incidents = serializers.SerializerMethodField()
    attachment_counts = serializers.SerializerMethodField()
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
            'labor_summary',
            'equipment',
            'machinery_rows',
            'machinery',
            'materials',
            'materials_summary',
            'concrete_logs',
            'labor_camp',
            'incidents',
            'general_activities',
            'visits',
            'issues',
            'hse_incidents',
            'attachment_counts',
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

    def get_labor_summary(self, obj):
        from decimal import Decimal

        rows = DailyReportLaborSerializer(
            self._active(obj.labor_entries), many=True, context=self.context,
        ).data
        sorted_rows = sorted(
            rows,
            key=lambda r: (
                0 if r.get('labor_category') == 'indirect' else 1,
                r.get('display_order') or 0,
                r.get('job_title') or '',
            ),
        )
        indirect_summary = [r for r in sorted_rows if r.get('labor_category') == 'indirect']
        direct_summary = [r for r in sorted_rows if r.get('labor_category') == 'direct']
        overall_summary = indirect_summary + direct_summary

        indirect_total_count = sum(int(r.get('present_count') or 0) for r in indirect_summary)
        direct_total_count = sum(int(r.get('present_count') or 0) for r in direct_summary)
        overall_total_count = indirect_total_count + direct_total_count

        indirect_leave_count = sum(int(r.get('leave_count') or 0) for r in indirect_summary)
        direct_leave_count = sum(int(r.get('leave_count') or 0) for r in direct_summary)
        overall_leave_count = indirect_leave_count + direct_leave_count

        indirect_overtime = sum(
            (Decimal(str(r.get('overtime_hours') or 0)) for r in indirect_summary),
            Decimal('0.00'),
        )
        direct_overtime = sum(
            (Decimal(str(r.get('overtime_hours') or 0)) for r in direct_summary),
            Decimal('0.00'),
        )
        overall_overtime = indirect_overtime + direct_overtime

        indirect_mh = sum(
            (Decimal(str(r.get('man_hours') or 0)) for r in indirect_summary),
            Decimal('0.00'),
        )
        direct_mh = sum(
            (Decimal(str(r.get('man_hours') or 0)) for r in direct_summary),
            Decimal('0.00'),
        )
        overall_mh = indirect_mh + direct_mh

        all_provenance = [
            p for r in overall_summary for p in (r.get('provenance') or [])
        ]

        return {
            'indirect_summary': indirect_summary,
            'direct_summary': direct_summary,
            'overall_summary': overall_summary,
            'totals': {
                'indirect_total_count': indirect_total_count,
                'direct_total_count': direct_total_count,
                'overall_total_count': overall_total_count,
                'indirect_leave_count': indirect_leave_count,
                'direct_leave_count': direct_leave_count,
                'overall_leave_count': overall_leave_count,
                'indirect_overtime_hours': f"{indirect_overtime:.2f}",
                'direct_overtime_hours': f"{direct_overtime:.2f}",
                'overall_overtime_hours': f"{overall_overtime:.2f}",
                'indirect_man_hours': f"{indirect_mh:.2f}",
                'direct_man_hours': f"{direct_mh:.2f}",
                'overall_man_hours': f"{overall_mh:.2f}",
                'source_count': len(all_provenance),
                'has_multiple_sources': len(all_provenance) > 1,
                'provenance': all_provenance,
                'indirect': {
                    'present_count': indirect_total_count,
                    'leave_count': indirect_leave_count,
                    'overtime_hours': f"{indirect_overtime:.2f}",
                    'man_hours': f"{indirect_mh:.2f}",
                },
                'direct': {
                    'present_count': direct_total_count,
                    'leave_count': direct_leave_count,
                    'overtime_hours': f"{direct_overtime:.2f}",
                    'man_hours': f"{direct_mh:.2f}",
                },
                'overall': {
                    'present_count': overall_total_count,
                    'leave_count': overall_leave_count,
                    'overtime_hours': f"{overall_overtime:.2f}",
                    'man_hours': f"{overall_mh:.2f}",
                },
            },
        }

    def get_equipment(self, obj):
        return DailyReportEquipmentSerializer(self._active(obj.equipment_entries), many=True, context=self.context).data

    def get_machinery_rows(self, obj):
        return DailyReportMachineryRowSerializer(
            self._active(obj.machinery_rows), many=True, context=self.context,
        ).data

    def get_machinery(self, obj):
        rows = self.get_machinery_rows(obj)
        config = getattr(obj, 'reporting_configuration', None)
        if config is None and getattr(obj, 'project_id', None) and getattr(obj, 'report_date', None):
            from field_reports.services.daily_report_aggregation import (
                resolve_project_reporting_configuration,
            )

            config = resolve_project_reporting_configuration(obj.project_id, obj.report_date)
        marker = ''
        if config is not None:
            marker = f"{config.id}:{getattr(config, 'snapshot_revision_marker', '') or config.effective_from}"

        # Type-level presentation rows per contract daily-summary-sections-api.md §1.3
        type_summaries_map = {}
        for r in rows:
            eq_type = r.get('equipment_type') or ''
            if eq_type not in type_summaries_map:
                type_summaries_map[eq_type] = {
                    'equipment_type': eq_type,
                    'status_total': 0,
                    'status_active': 0,
                    'status_ready': 0,
                    'status_inactive': 0,
                    'status_under_repair': 0,
                    'operating_hours': Decimal('0.00'),
                    'stoppage_hours': Decimal('0.00'),
                    'repair_hours': Decimal('0.00'),
                }
            ts = type_summaries_map[eq_type]
            ts['status_total'] += r.get('status_total') or 0
            ts['status_active'] += r.get('status_active') or 0
            ts['status_ready'] += r.get('status_ready') or 0
            ts['status_inactive'] += r.get('status_inactive') or 0
            ts['status_under_repair'] += r.get('status_under_repair') or 0
            if r.get('operating_hours'):
                ts['operating_hours'] += Decimal(str(r['operating_hours']))
            if r.get('stoppage_hours'):
                ts['stoppage_hours'] += Decimal(str(r['stoppage_hours']))
            if r.get('repair_hours'):
                ts['repair_hours'] += Decimal(str(r['repair_hours']))

        type_summaries = [
            {
                'equipment_type': eq_type,
                'status_total': ts['status_total'],
                'status_active': ts['status_active'],
                'status_ready': ts['status_ready'],
                'status_inactive': ts['status_inactive'],
                'status_under_repair': ts['status_under_repair'],
                'operating_hours': f"{ts['operating_hours']:.2f}",
                'stoppage_hours': f"{ts['stoppage_hours']:.2f}",
                'repair_hours': f"{ts['repair_hours']:.2f}",
            }
            for eq_type, ts in sorted(type_summaries_map.items())
        ]

        return {
            'rows': rows,
            'type_summaries': type_summaries,
            'vocabulary_revision_marker': marker,
        }

    def get_materials(self, obj):
        return DailyReportMaterialSerializer(self._active(obj.material_entries), many=True, context=self.context).data

    def get_materials_summary(self, obj):
        rows = DailyReportMaterialSerializer(
            self._active(obj.material_entries), many=True, context=self.context,
        ).data
        main_table = [
            r for r in rows
            if r.get('transaction_type') == 'receipt' and r.get('receipt_resolved') is True
        ]
        details = [
            r for r in rows
            if not (r.get('transaction_type') == 'receipt' and r.get('receipt_resolved') is True)
        ]

        from collections import defaultdict
        from decimal import Decimal

        groups = defaultdict(lambda: {
            'material_ref_id': None,
            'material_description': '',
            'unit': '',
            'total_received': Decimal('0'),
            'total_consumed': Decimal('0'),
        })

        for r in rows:
            mat_ref = r.get('material_ref')
            mat_desc = (r.get('material_description') or '').strip()
            unit = (r.get('unit') or '').strip()
            key = (str(mat_ref) if mat_ref else '', mat_desc.lower(), unit.lower())

            item = groups[key]
            if not item['material_description']:
                item['material_description'] = mat_desc
            if not item['unit']:
                item['unit'] = unit
            item['material_ref_id'] = mat_ref

            qty = Decimal(str(r.get('quantity') or 0))
            tx_type = r.get('transaction_type')
            if tx_type == 'receipt':
                item['total_received'] += qty
            elif tx_type in ('issue', 'consumption'):
                item['total_consumed'] += qty

        grouped_summary = []
        for item in groups.values():
            net = item['total_received'] - item['total_consumed']
            grouped_summary.append({
                'material_ref_id': item['material_ref_id'],
                'material_description': item['material_description'],
                'unit': item['unit'],
                'total_received': float(item['total_received']),
                'total_consumed': float(item['total_consumed']),
                'net_quantity': float(net),
            })

        return {
            'main_table': main_table,
            'details': details,
            'grouped_summary': grouped_summary,
        }

    def get_concrete_logs(self, obj):
        return DailyReportConcreteLogSerializer(self._active(obj.concrete_logs), many=True, context=self.context).data

    def get_labor_camp(self, obj):
        return DailyReportLaborCampSerializer(self._active(obj.labor_camp_entries), many=True).data

    def get_incidents(self, obj):
        return DailyReportIncidentSerializer(self._active(obj.incidents), many=True, context=self.context).data

    def get_general_activities(self, obj):
        return DailyReportGeneralActivitySerializer(
            self._active(obj.general_activities), many=True, context=self.context,
        ).data

    def get_visits(self, obj):
        return DailyReportVisitSerializer(self._active(obj.visits), many=True, context=self.context).data

    def get_issues(self, obj):
        rows = [
            row for row in self._active(obj.incidents)
            if row.incident_type in {'issue', 'barrier'}
        ]
        return DailyReportIncidentSerializer(rows, many=True, context=self.context).data

    def get_hse_incidents(self, obj):
        rows = [row for row in self._active(obj.incidents) if row.incident_type == 'safety']
        return DailyReportIncidentSerializer(rows, many=True, context=self.context).data

    def get_attachment_counts(self, obj):
        """Expose counts for eligible source versions, never storage URLs.

        Attachment bytes are MinIO-backed and may not be available locally. The
        only links emitted here point at the permission-checked source attachment
        collection, so clients can navigate to metadata without treating a
        storage key as a public file URL.
        """
        from sub_reports.models import UnitReportAttachment
        from field_reports.services.daily_report_aggregation import contributing_sub_reports

        source_ids = contributing_sub_reports(obj.project_id, obj.report_date).values('id')
        rows = UnitReportAttachment.objects.filter(
            sub_report_id__in=source_ids, is_deleted=False,
        ).select_related('sub_report').order_by('row_kind', 'id')

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        allowed = False
        if user is not None and getattr(user, 'is_authenticated', False):
            if getattr(user, 'is_superuser', False):
                allowed = True
            else:
                from master_data.models import ProjectMember
                allowed = ProjectMember.objects.filter(project_id=obj.project_id, user_id=user.id).exists()

        grouped = {}
        for row in rows:
            section = row.row_kind or 'activity'
            payload = grouped.setdefault(section, {'section': section, 'count': 0, 'first_links': []})
            payload['count'] += 1
            if allowed and len(payload['first_links']) < 3:
                payload['first_links'].append(
                    f'/api/v1/projects/{obj.project_id}/units/{row.sub_report.unit}/'
                    f'daily-reports/{row.sub_report_id}/attachments/#attachment-{row.id}'
                )
        return list(grouped.values())


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
    modifier_name = serializers.SerializerMethodField()
    correction_reason = serializers.SerializerMethodField()

    def get_modifier_name(self, obj):
        return _user_name(obj.updated_by or obj.created_by)

    def get_correction_reason(self, obj):
        request = next(
            (
                item for item in obj.correction_requests_as_result.all()
                if not item.is_deleted
            ),
            None,
        )
        return request.reason if request else None

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
            'modifier_name',
            'correction_reason',
            'approved_at',
            'created_at',
        ]
