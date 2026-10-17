"""Cost control serializers."""

from decimal import Decimal

from rest_framework import serializers

from common.serializers import JalaliDateField
from cost_control.models import (
    ActualCost,
    Budget,
    BudgetChangeRequest,
    BudgetLineLevel,
    BudgetTransfer,
    BudgetVersion,
    Commitment,
    CostBreakdownNode,
    CostPool,
    Payment,
)
from resources.models import Supplier


def _format_amount(value) -> str:
    if value is None:
        return '0'
    return f'{float(value):,.0f}'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'project',
            'supplier_name',
            'supplier_code',
            'contact_person',
            'phone',
            'email',
            'address',
        ]
        read_only_fields = ['id', 'project']


class BudgetSerializer(serializers.ModelSerializer):
    budget_amount_display = serializers.SerializerMethodField()
    wbs_code = serializers.CharField(source='wbs.wbs_code', read_only=True, default=None)
    wbs_name = serializers.CharField(source='wbs.wbs_name', read_only=True, default=None)
    activity_code = serializers.CharField(source='activity.activity_code', read_only=True, default=None)
    activity_name = serializers.CharField(source='activity.activity_name', read_only=True, default=None)
    period_start = JalaliDateField(required=False, allow_null=True)
    period_end = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = Budget
        fields = [
            'id',
            'version',
            'level',
            'wbs',
            'activity',
            'cbs',
            'contract',
            'wbs_code',
            'wbs_name',
            'activity_code',
            'activity_name',
            'cost_category',
            'budget_amount',
            'budget_amount_display',
            'period_start',
            'period_end',
            'currency',
            'notes',
        ]
        read_only_fields = ['id', 'version']

    def get_budget_amount_display(self, obj):
        return _format_amount(obj.budget_amount)


class BudgetBulkItemSerializer(serializers.Serializer):
    wbs = serializers.UUIDField(required=False, allow_null=True)
    activity = serializers.UUIDField(required=False, allow_null=True)
    cbs = serializers.UUIDField(required=False, allow_null=True)
    contract = serializers.UUIDField(required=False, allow_null=True)
    level = serializers.ChoiceField(
        choices=BudgetLineLevel.choices,
        required=False,
        allow_null=True,
    )
    cost_category = serializers.ChoiceField(choices=Budget._meta.get_field('cost_category').choices)
    budget_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    period_start = serializers.DateField(required=False, allow_null=True)
    period_end = serializers.DateField(required=False, allow_null=True)

    def validate(self, attrs):
        level = attrs.get('level') or BudgetLineLevel.WBS
        if level == BudgetLineLevel.PROJECT:
            return attrs
        if level == BudgetLineLevel.CONTRACT and not attrs.get('contract'):
            raise serializers.ValidationError({'contract': 'Required for contract level.'})
        if level == BudgetLineLevel.CBS and not attrs.get('cbs'):
            raise serializers.ValidationError({'cbs': 'Required for cbs level.'})
        if level == BudgetLineLevel.ACTIVITY and not attrs.get('activity'):
            raise serializers.ValidationError({'activity': 'Required for activity level.'})
        if level in (BudgetLineLevel.WBS, BudgetLineLevel.PHASE) and not attrs.get('wbs') and not attrs.get(
            'activity'
        ):
            raise serializers.ValidationError('At least one of wbs or activity is required.')
        if not level and not attrs.get('wbs') and not attrs.get('activity') and not attrs.get('cbs') and not attrs.get(
            'contract'
        ):
            raise serializers.ValidationError('At least one of wbs, activity, cbs, or contract is required.')
        return attrs


class BudgetVersionSerializer(serializers.ModelSerializer):
    line_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = BudgetVersion
        fields = [
            'id',
            'kind',
            'status',
            'version_number',
            'name',
            'currency',
            'notes',
            'is_control',
            'submitted_at',
            'approved_at',
            'rejected_at',
            'rejection_reason',
            'line_count',
            'total_amount',
        ]
        read_only_fields = [
            'id',
            'version_number',
            'status',
            'is_control',
            'submitted_at',
            'approved_at',
            'rejected_at',
            'rejection_reason',
            'line_count',
            'total_amount',
        ]

    def get_line_count(self, obj):
        return obj.lines.filter(is_deleted=False).count()

    def get_total_amount(self, obj):
        from django.db.models import Sum

        total = obj.lines.filter(is_deleted=False).aggregate(t=Sum('budget_amount'))['t'] or 0
        return float(total)


class BudgetVersionCreateSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=['initial', 'revised', 'final_forecast'])
    name = serializers.CharField(required=False, allow_blank=True, default='')
    currency = serializers.CharField(required=False, default='IRR', max_length=3)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class BudgetChangeRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetChangeRequest
        fields = [
            'id',
            'base_version',
            'resulting_version',
            'reason',
            'amount_delta',
            'project_impact',
            'affected_lines',
            'status',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
            'decision_notes',
        ]
        read_only_fields = [
            'id',
            'base_version',
            'resulting_version',
            'status',
            'requested_by',
            'requested_at',
            'decided_by',
            'decided_at',
        ]


class BudgetChangeRequestCreateSerializer(serializers.Serializer):
    reason = serializers.CharField()
    project_impact = serializers.CharField()
    amount_delta = serializers.DecimalField(max_digits=18, decimal_places=2, required=False, default=0)
    affected_lines = serializers.ListField(child=serializers.DictField(), required=False, default=list)


class BudgetTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetTransfer
        fields = [
            'id',
            'version',
            'from_line',
            'to_line',
            'amount',
            'note',
            'created_at',
        ]
        read_only_fields = fields


class BudgetTransferCreateSerializer(serializers.Serializer):
    from_line_id = serializers.UUIDField()
    to_line_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, default='')


class ActualCostSerializer(serializers.ModelSerializer):
    cost_date = JalaliDateField()
    registered_at = JalaliDateField(required=False, allow_null=True)
    amount_display = serializers.SerializerMethodField()
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True, default=None)
    is_auto_created = serializers.SerializerMethodField()
    wbs_code = serializers.CharField(source='wbs.wbs_code', read_only=True, default=None)
    activity_code = serializers.CharField(source='activity.activity_code', read_only=True, default=None)

    class Meta:
        model = ActualCost
        fields = [
            'id',
            'activity',
            'wbs',
            'cbs',
            'commitment',
            'wbs_code',
            'activity_code',
            'cost_date',
            'registered_at',
            'status',
            'cost_category',
            'amount',
            'amount_display',
            'description',
            'invoice_number',
            'document_ref',
            'supplier',
            'supplier_name',
            'cost_type',
            'confidence_level',
            'allocation_method',
            'cost_pool',
            'daily_report',
            'is_auto_created',
            'approved_by',
        ]
        read_only_fields = ['id', 'daily_report', 'is_auto_created', 'status', 'approved_by']

    def get_amount_display(self, obj):
        return _format_amount(obj.amount)

    def get_is_auto_created(self, obj):
        return obj.daily_report_id is not None


class CostPoolSerializer(serializers.ModelSerializer):
    remaining = serializers.SerializerMethodField()
    total_amount_display = serializers.SerializerMethodField()

    class Meta:
        model = CostPool
        fields = [
            'id',
            'pool_name',
            'cost_category',
            'total_amount',
            'total_amount_display',
            'allocated_amount',
            'remaining',
            'status',
            'data_source',
            'confidence_level',
        ]
        read_only_fields = ['id', 'allocated_amount', 'status', 'remaining']

    def get_remaining(self, obj):
        return float(obj.remaining)

    def get_total_amount_display(self, obj):
        return _format_amount(obj.total_amount)


class CostPoolAllocationItemSerializer(serializers.Serializer):
    activity_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    allocation_method = serializers.CharField(required=False, allow_blank=True, default='')
    confidence_level = serializers.CharField(required=False, allow_blank=True, default='')


class CostBreakdownNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostBreakdownNode
        fields = [
            'id',
            'cbs_code',
            'cbs_name',
            'cost_type',
            'description',
            'depth',
            'is_deleted',
            'created_at',
        ]
        read_only_fields = ['id', 'depth', 'is_deleted', 'created_at']


class CommitmentSerializer(serializers.ModelSerializer):
    commitment_date = JalaliDateField()
    due_date = JalaliDateField(required=False, allow_null=True)
    remaining = serializers.SerializerMethodField()

    class Meta:
        model = Commitment
        fields = [
            'id',
            'commitment_number',
            'counterparty',
            'amount',
            'currency',
            'fx_rate',
            'commitment_date',
            'due_date',
            'wbs',
            'cbs',
            'contract',
            'requisition',
            'payment_terms',
            'status',
            'description',
            'document_ref',
            'remaining',
        ]
        read_only_fields = ['id', 'status', 'remaining']

    def get_remaining(self, obj):
        # ⚡ Bolt: Leverage prefetched payments collection in Python memory when available to prevent N+1 queries
        if hasattr(obj, '_prefetched_objects_cache') and 'payments' in obj._prefetched_objects_cache:
            posted_total = sum(p.amount for p in obj.payments.all() if not p.is_deleted and p.status == 'posted')
            return float(Decimal(obj.amount) - Decimal(posted_total))
        from cost_control.cbs_services import posted_payments_total

        return float(Decimal(obj.amount) - posted_payments_total(obj))

    def validate_requisition(self, value):
        if value is None:
            return value
        from cost_control.services.commitment_origin_service import (
            assert_requisition_approved_for_commitment,
        )

        project = self.context.get('project')
        project_id = project.id if project is not None else getattr(value, 'project_id', None)
        if project_id is not None:
            assert_requisition_approved_for_commitment(value, project_id)
        return value


class PaymentSerializer(serializers.ModelSerializer):
    paid_at = JalaliDateField()
    commitment = serializers.PrimaryKeyRelatedField(
        queryset=Commitment.objects.all(),
        required=False,
        allow_null=True,
    )
    acknowledge_duplicate_exception = serializers.BooleanField(required=False, default=False, write_only=True)
    exception_reason = serializers.CharField(required=False, allow_blank=True, default='', write_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'commitment',
            'actual_cost',
            'amount',
            'currency',
            'fx_rate',
            'paid_at',
            'document_ref',
            'status',
            'duplicate_exception_reason',
            'duplicate_exception_by',
            'acknowledge_duplicate_exception',
            'exception_reason',
        ]
        read_only_fields = [
            'id',
            'status',
            'duplicate_exception_reason',
            'duplicate_exception_by',
        ]
