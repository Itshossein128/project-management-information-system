from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework import serializers

from common.serializers import JalaliDateField
from field_reports.models import Equipment
from projects.models import Activity, Stakeholder
from resources.models import Material
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    DisciplineSubReportConcrete,
    DisciplineSubReportGeneralActivity,
    DisciplineSubReportLabor,
    DisciplineSubReportMachinery,
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

    def validate_execution_percentage(self, value):
        if value is not None and (value < Decimal('0.00') or value > Decimal('100.00')):
            raise serializers.ValidationError(
                _('درصد پیشرفت باید بین ۰ تا ۱۰۰ باشد / Execution percentage must be between 0.00 and 100.00'),
                code='percent_must_be_between_0_and_100',
            )
        return value


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
        required=False,
        allow_null=True,
    )
    contractor_name = serializers.CharField(source='contractor_ref.name', read_only=True)
    foreman_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    worker_count = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    activity_description = serializers.CharField(required=False, allow_blank=True, default='')
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    execution_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
    )
    achieved_milestones = serializers.ListField(required=False, allow_empty=True, default=list)
    shift_hours = serializers.DecimalField(
        max_digits=4, decimal_places=2, required=False, default=Decimal('8.00'),
    )
    is_hydrostatic_tested = serializers.BooleanField(required=False, default=False)
    test_pressure_bar = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, allow_null=True,
    )
    test_duration_minutes = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    test_outcome = serializers.ChoiceField(
        choices=('PASSED', 'FAILED'), required=False, allow_blank=True, default='',
    )
    tested_segment = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    qc_inspection = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DisciplineSubReportActivity
        fields = [
            'id',
            'sync_revision',
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
            'execution_percentage',
            'achieved_milestones',
            'shift_hours',
            'is_hydrostatic_tested',
            'test_pressure_bar',
            'test_duration_minutes',
            'test_outcome',
            'tested_segment',
            'qc_inspection',
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

    def validate_execution_percentage(self, value):
        if value is not None and (value < Decimal('0.00') or value > Decimal('100.00')):
            raise serializers.ValidationError(
                _('درصد پیشرفت باید بین ۰ تا ۱۰۰ باشد / Execution percentage must be between 0.00 and 100.00'),
                code='percent_must_be_between_0_and_100',
            )
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        # Hydrostatic test check
        is_tested = attrs.get('is_hydrostatic_tested')
        if is_tested is None and self.instance:
            is_tested = self.instance.is_hydrostatic_tested
        if is_tested:
            pressure = attrs.get('test_pressure_bar')
            if pressure is None and self.instance:
                pressure = self.instance.test_pressure_bar
            if pressure is None or pressure <= Decimal('0.00'):
                raise serializers.ValidationError(
                    {
                        'test_pressure_bar': serializers.ErrorDetail(
                            _('فشار آزمون باید عددی مثبت باشد / Test pressure must be a positive number'),
                            code='invalid_test_pressure_value',
                        )
                    }
                )
        if not (attrs.get('activity_description') or '').strip():
            act = attrs.get('activity_ref') or getattr(self.instance, 'activity_ref', None)
            if act is not None and getattr(act, 'activity_name', None):
                attrs['activity_description'] = act.activity_name

        # A sub-report activity is a physical progress entry. Validate the
        # approved measurement basis and cumulative quantity before the row is
        # persisted, including draft/in-flight rows from the same project.
        activity = attrs.get('activity_ref') or getattr(self.instance, 'activity_ref', None)
        quantity = attrs.get('quantity')
        if quantity is None and self.instance is not None:
            quantity = self.instance.quantity
        if activity is not None:
            # Reject foreign references before consulting their measurement
            # status or quantities, which belong to another project's data.
            report = self.context.get('report') or getattr(self.instance, 'sub_report', None)
            if report is not None and str(activity.project_id) != str(report.project_id):
                raise serializers.ValidationError({
                    'activity_ref': serializers.ErrorDetail(
                        'فعالیت به پروژه گزارش تعلق ندارد.', code='activity_not_in_project_scope',
                    ),
                })
            from django.db.models import Sum
            from schedule.services.measurement_service import (
                effective_total_quantity,
                get_current_approved_version,
            )

            version = get_current_approved_version(activity)
            if version is None:
                raise serializers.ValidationError(
                    serializers.ErrorDetail(
                        'روش اندازه‌گیری این فعالیت هنوز تأیید نشده است.',
                        code='measurement_not_approved',
                    )
                )
            if quantity is not None and quantity > 0:
                total = effective_total_quantity(activity, version)
                if total is not None and total > 0:
                    from sub_reports.models import DisciplineSubReportActivity
                    report = self.context.get('report') or getattr(self.instance, 'sub_report', None)
                    report_date = getattr(report, 'report_date', None)
                    prior = DisciplineSubReportActivity.objects.filter(
                        sub_report__project_id=activity.project_id,
                        activity_ref=activity,
                        is_deleted=False,
                    ).filter(
                        Q(sub_report__status='approved')
                        | Q(sub_report__report_date=report_date),
                    )
                    if self.instance is not None:
                        prior = prior.exclude(pk=self.instance.pk)
                    existing = prior.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
                    if existing + quantity > total:
                        raise serializers.ValidationError(
                            serializers.ErrorDetail(
                                'مجموع پیشرفت نمی‌تواند از ۱۰۰٪ بیشتر شود؛ لطفاً مقادیر اصلاح شوند',
                                code='progress_exceeds_100',
                            )
                        )
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


class UnitReportLaborSectionSerializer(serializers.ModelSerializer):
    """Canonical unit-report §2 labor rows (feature 033, task T021).

    Resolves job titles against the effective project reporting configuration
    snapshot for the report date, enforces non-negative integer headcounts
    (`headcount_must_be_non_negative`), category consistency with the catalog
    title (`invalid_labor_category`), and optional project-scoped contractor.
    Man-hours are not stored on the unit row; aggregation computes them per the
    effective rule.
    """

    labor_category = serializers.CharField(required=True, allow_blank=True)
    job_title = serializers.CharField(max_length=120, required=False, allow_blank=True, default='')
    custom_title = serializers.CharField(
        max_length=120, required=False, allow_blank=True, default='', write_only=True,
    )
    present_count = serializers.IntegerField(required=False, default=0)
    leave_count = serializers.IntegerField(required=False, default=0)
    overtime_hours = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=False, default=0,
    )
    contractor_ref = serializers.PrimaryKeyRelatedField(
        queryset=Stakeholder.objects.all(),
        required=False,
        allow_null=True,
    )
    contractor_name = serializers.CharField(source='contractor_ref.name', read_only=True)
    title_code = serializers.SerializerMethodField()
    display_order = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReportLabor
        fields = [
            'id',
            'sync_revision',
            'labor_category',
            'job_title',
            'custom_title',
            'present_count',
            'leave_count',
            'overtime_hours',
            'contractor_ref',
            'contractor_name',
            'title_code',
            'display_order',
        ]
        read_only_fields = ['id', 'contractor_name', 'title_code', 'display_order']

    def _effective_config(self, obj):
        cache = self.context.setdefault('_config_cache', {})
        report = self.context.get('report') or getattr(obj, 'sub_report', None)
        if report is None:
            return None
        key = (str(report.project_id), str(report.report_date))
        if key not in cache:
            from field_reports.services.daily_report_aggregation import (
                resolve_project_reporting_configuration,
            )

            cache[key] = resolve_project_reporting_configuration(
                report.project_id, report.report_date,
            )
        return cache[key]

    def _resolved_title(self, obj):
        config = self._effective_config(obj)
        if config is None:
            return None
        from project_templates.services import resolve_labor_title

        return resolve_labor_title(config, getattr(obj, 'job_title', '') or '')

    def get_title_code(self, obj) -> str:
        resolved = self._resolved_title(obj)
        return resolved.title_code if resolved else ''

    def get_display_order(self, obj) -> int:
        resolved = self._resolved_title(obj)
        return resolved.display_order if resolved else 0

    def validate_present_count(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                _('تعداد نفرات حاضر نمی‌تواند منفی باشد'),
                code='headcount_must_be_non_negative',
            )
        return 0 if value is None else value

    def validate_leave_count(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                _('تعداد نفرات مرخصی/غیبت نمی‌تواند منفی باشد'),
                code='headcount_must_be_non_negative',
            )
        return 0 if value is None else value

    def validate_overtime_hours(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                _('ساعت اضافه‌کاری نمی‌تواند منفی باشد'),
                code='headcount_must_be_non_negative',
            )
        return 0 if value is None else value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('contractor_ref') is not None:
            data['contractor_ref'] = str(data['contractor_ref'])
        return data


class UnitReportMachinerySectionSerializer(serializers.ModelSerializer):
    """Canonical unit-report §3 machinery rows (feature 033, task T028).

    Enforces non-negative status counts (`status_count_must_be_non_negative`),
    day-limit hours (`hours_exceed_day_limit`), and stoppage reason vocabulary
    (`stoppage_reason_required_when_stoppage_gt_zero`, `stoppage_reason_not_in_vocabulary`).
    """

    row_number = serializers.IntegerField(required=False, allow_null=True, min_value=1)
    equipment_type = serializers.CharField(max_length=120, required=True, allow_blank=False)
    equipment_ref = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        required=False,
        allow_null=True,
    )
    equipment_code = serializers.CharField(source='equipment_ref.equipment_code', read_only=True)
    equipment_name = serializers.CharField(source='equipment_ref.equipment_name', read_only=True)
    status_total = serializers.IntegerField(required=False, default=0)
    status_active = serializers.IntegerField(required=False, default=0)
    status_ready = serializers.IntegerField(required=False, default=0)
    status_inactive = serializers.IntegerField(required=False, default=0)
    status_under_repair = serializers.IntegerField(required=False, default=0)
    operating_hours = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
    )
    stoppage_hours = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
    )
    repair_hours = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, allow_null=True,
    )
    stoppage_reason_code = serializers.CharField(
        max_length=60, required=False, allow_blank=True, default='',
    )
    stoppage_reason_label = serializers.SerializerMethodField()
    stoppage_reason_label_fa = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReportMachinery
        fields = [
            'id',
            'sync_revision',
            'row_number',
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
            'stoppage_reason_label',
            'stoppage_reason_label_fa',
        ]
        read_only_fields = [
            'id',
            'equipment_code',
            'equipment_name',
            'stoppage_reason_label',
            'stoppage_reason_label_fa',
        ]

    def _vocabulary_map(self, obj):
        cache = self.context.setdefault('_stoppage_vocab_cache', {})
        report = self.context.get('report') or getattr(obj, 'sub_report', None)
        key = (
            (str(report.project_id), str(report.report_date))
            if report is not None
            else ('default', 'default')
        )
        if key not in cache:
            from sub_reports.services.section_validation import resolve_stoppage_vocabulary

            vocab = resolve_stoppage_vocabulary(report, context=self.context)
            cache[key] = {v['reason_code']: v for v in vocab}
        return cache[key]

    def get_stoppage_reason_label(self, obj):
        code = (getattr(obj, 'stoppage_reason_code', None) or '').strip()
        if not code:
            return None
        entry = self._vocabulary_map(obj).get(code)
        return entry['reason_label'] if entry else code

    def get_stoppage_reason_label_fa(self, obj):
        code = (getattr(obj, 'stoppage_reason_code', None) or '').strip()
        if not code:
            return None
        entry = self._vocabulary_map(obj).get(code)
        return entry['reason_label_fa'] if entry else code

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('equipment_ref') is not None:
            data['equipment_ref'] = str(data['equipment_ref'])
        return data


class UnitReportMaterialSectionSerializer(serializers.ModelSerializer):
    """Canonical unit-report §4 material rows (feature 033, task T035).

    Enforces transaction_type (`transaction_type_required`), positive quantity
    (`quantity_must_be_positive`), document reference on receipts
    (`receipt_requires_document_reference`), consumption location on consumption
    (`consumption_location_required_for_consumption`), and project-scoped
    material_ref (`reference_not_in_project_scope`). Receipt resolution is
    computed read-only from project warehouse documents (never client-stored).
    """

    transaction_type = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    material_description = serializers.CharField(max_length=255, required=True, allow_blank=False)
    material_ref = serializers.PrimaryKeyRelatedField(
        queryset=Material.objects.all(),
        required=False,
        allow_null=True,
    )
    material_code = serializers.CharField(source='material_ref.material_code', read_only=True)
    material_name = serializers.CharField(source='material_ref.material_name', read_only=True)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=4, required=True)
    unit = serializers.CharField(max_length=40, required=True, allow_blank=False)
    consumption_location = serializers.CharField(
        max_length=160, required=False, allow_blank=True, default='',
    )
    supplier = serializers.CharField(
        max_length=160, required=False, allow_blank=True, default='',
    )
    warehouse_document_reference = serializers.CharField(
        max_length=120, required=False, allow_blank=True, default='',
    )
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    receipt_evidence = serializers.SerializerMethodField()
    receipt_resolved = serializers.SerializerMethodField()

    class Meta:
        model = DisciplineSubReportMaterial
        fields = [
            'id',
            'sync_revision',
            'transaction_type',
            'material_description',
            'material_ref',
            'material_code',
            'material_name',
            'quantity',
            'unit',
            'consumption_location',
            'supplier',
            'warehouse_document_reference',
            'notes',
            'receipt_evidence',
            'receipt_resolved',
        ]
        read_only_fields = [
            'id',
            'material_code',
            'material_name',
            'receipt_evidence',
            'receipt_resolved',
        ]

    def _is_receipt_resolved(self, obj) -> bool:
        # ⚡ Bolt: Cache warehouse resolution per object on serializer instance to prevent duplicate DB queries
        if not hasattr(self, '_resolved_receipt_cache'):
            self._resolved_receipt_cache = {}
        cache_key = getattr(obj, 'id', None) or id(obj)
        if cache_key in self._resolved_receipt_cache:
            return self._resolved_receipt_cache[cache_key]

        tx_type = getattr(obj, 'transaction_type', None)
        if tx_type != 'receipt':
            self._resolved_receipt_cache[cache_key] = False
            return False
        doc_ref = (getattr(obj, 'warehouse_document_reference', '') or '').strip()
        if not doc_ref:
            self._resolved_receipt_cache[cache_key] = False
            return False
        report = self.context.get('report') or getattr(obj, 'sub_report', None)
        project_id = getattr(report, 'project_id', None) or self.context.get('project_id')
        if not project_id:
            self._resolved_receipt_cache[cache_key] = False
            return False
        from sub_reports.services.section_validation import resolve_warehouse_document

        doc = resolve_warehouse_document(
            project_id, doc_ref, getattr(obj, 'material_ref_id', None)
        )
        resolved = doc is not None
        self._resolved_receipt_cache[cache_key] = resolved
        return resolved

    def get_receipt_evidence(self, obj) -> str | None:
        tx_type = getattr(obj, 'transaction_type', None)
        if tx_type != 'receipt':
            return None
        return 'resolved' if self._is_receipt_resolved(obj) else 'unresolved_reference'

    def get_receipt_resolved(self, obj) -> bool:
        return self._is_receipt_resolved(obj)

    def validate_transaction_type(self, value):
        val = (value or '').strip()
        if val not in ('receipt', 'consumption'):
            raise serializers.ValidationError(
                _('انتخاب نوع تراکنش مصالح الزامی است'),
                code='transaction_type_required',
            )
        return val

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                _('مقدار مصالح باید بزرگ‌تر از صفر باشد'),
                code='quantity_must_be_positive',
            )
        return value

    def validate(self, attrs):
        tx_type = attrs.get(
            'transaction_type',
            getattr(self.instance, 'transaction_type', None) if self.instance else None,
        )
        tx_type = (tx_type or '').strip()
        if tx_type not in ('receipt', 'consumption'):
            raise serializers.ValidationError({
                'transaction_type': serializers.ErrorDetail(
                    _('انتخاب نوع تراکنش مصالح الزامی است'),
                    code='transaction_type_required',
                )
            })
        attrs['transaction_type'] = tx_type

        if tx_type == 'receipt':
            doc_ref = (
                attrs.get(
                    'warehouse_document_reference',
                    getattr(self.instance, 'warehouse_document_reference', '')
                    if self.instance
                    else '',
                )
                or ''
            ).strip()
            if not doc_ref:
                raise serializers.ValidationError({
                    'warehouse_document_reference': serializers.ErrorDetail(
                        _('برای رسید انبار، شماره برگه/سند انبار الزامی است'),
                        code='receipt_requires_document_reference',
                    )
                })
            attrs['warehouse_document_reference'] = doc_ref
        elif tx_type == 'consumption':
            loc = (
                attrs.get(
                    'consumption_location',
                    getattr(self.instance, 'consumption_location', '')
                    if self.instance
                    else '',
                )
                or ''
            ).strip()
            if not loc:
                raise serializers.ValidationError({
                    'consumption_location': serializers.ErrorDetail(
                        _('برای مصرف مصالح، محل مصرف الزامی است'),
                        code='consumption_location_required_for_consumption',
                    )
                })
            attrs['consumption_location'] = loc

        mat_ref = attrs.get(
            'material_ref',
            getattr(self.instance, 'material_ref', None) if self.instance else None,
        )
        report = self.context.get('report') or getattr(self.instance, 'sub_report', None)
        project_id = getattr(report, 'project_id', None) or self.context.get('project_id')
        if mat_ref is not None:
            if getattr(mat_ref, 'is_deleted', False) or (
                project_id and str(mat_ref.project_id) != str(project_id)
            ):
                raise serializers.ValidationError({
                    'material_ref': serializers.ErrorDetail(
                        _('شناسه ارجاع‌شده متعلق به این پروژه نیست'),
                        code='reference_not_in_project_scope',
                    )
                })

        return attrs

    def create(self, validated_data):
        if 'sub_report' not in validated_data and self.context.get('report') is not None:
            validated_data['sub_report'] = self.context['report']
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get('material_ref') is not None:
            data['material_ref'] = str(data['material_ref'])
        return data


class SubReportMaterialSerializer(UnitReportMaterialSectionSerializer):
    """Alias/compat serializer enforcing the §4 materials contract."""
    pass


class UnitReportConcreteSectionSerializer(serializers.ModelSerializer):
    """§2.5 concrete pour contract (feature 033, T041)."""

    class Meta:
        model = DisciplineSubReportConcrete
        fields = [
            'id', 'sync_revision', 'concrete_description', 'volume_m3', 'zone', 'block', 'floor', 'notes',
            'structural_element', 'parcel', 'batching_plant', 'truck_delivery_note_number',
            'lab_sample_code', 'sampling_state', 'test_sheet_count', 'qc_inspection',
        ]
        read_only_fields = ['id', 'qc_inspection']

    def validate_volume_m3(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError(
                _('حجم بتن باید بزرگ‌تر از صفر باشد'),
                code='volume_must_be_positive',
            )
        return value


class SubReportConcreteSerializer(UnitReportConcreteSectionSerializer):
    """Nested compat serializer. QC linkage stays read-only."""


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
