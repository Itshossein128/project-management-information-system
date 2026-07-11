"""Contract and IPC serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from contracts.models import ChangeOrder, Contract, ContractItem, IPC, IPCDeduction, IPCItem


def _format_amount(value) -> str:
    if value is None:
        return '0'
    return f'{float(value):,.0f}'


class ContractItemSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source='unit.name', read_only=True, default='')
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = ContractItem
        fields = [
            'id', 'activity', 'boq_code', 'description', 'unit', 'unit_name',
            'unit_price', 'quantity', 'total_amount',
        ]
        read_only_fields = ['id']

    def get_total_amount(self, obj):
        return float(obj.total_amount)


class ChangeOrderSerializer(serializers.ModelSerializer):
    approved_date = JalaliDateField(required=False, allow_null=True)
    amount_change_display = serializers.SerializerMethodField()

    class Meta:
        model = ChangeOrder
        fields = [
            'id', 'change_number', 'description', 'amount_change',
            'amount_change_display', 'approved_date', 'status', 'file_url',
        ]
        read_only_fields = ['id', 'change_number']

    def get_amount_change_display(self, obj):
        return _format_amount(obj.amount_change)


class ContractListSerializer(serializers.ModelSerializer):
    effective_amount = serializers.SerializerMethodField()
    advance_amount = serializers.SerializerMethodField()
    total_ipc_count = serializers.SerializerMethodField()
    paid_ipc_count = serializers.SerializerMethodField()
    total_billed = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    guarantee_expiry_alert = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'contract_type', 'counterparty',
            'original_amount', 'adjusted_amount', 'effective_amount', 'advance_amount',
            'status', 'total_ipc_count', 'paid_ipc_count', 'total_billed', 'total_paid',
            'guarantee_expiry_alert',
        ]

    def get_effective_amount(self, obj):
        return float(obj.effective_amount)

    def get_advance_amount(self, obj):
        return obj.advance_amount

    def _ipc_stats(self, obj):
        return getattr(obj, '_ipc_stats', None)

    def get_total_ipc_count(self, obj):
        stats = self._ipc_stats(obj)
        return stats['total'] if stats else obj.ipcs.filter(is_deleted=False).count()

    def get_paid_ipc_count(self, obj):
        stats = self._ipc_stats(obj)
        return stats['paid'] if stats else obj.ipcs.filter(is_deleted=False, status='paid').count()

    def get_total_billed(self, obj):
        stats = self._ipc_stats(obj)
        return stats['billed'] if stats else 0

    def get_total_paid(self, obj):
        stats = self._ipc_stats(obj)
        return stats['paid_amount'] if stats else 0

    def get_guarantee_expiry_alert(self, obj):
        from datetime import date, timedelta

        today = date.today()
        threshold = today + timedelta(days=30)
        for exp in (obj.performance_guarantee_expiry, obj.advance_guarantee_expiry):
            if exp and today <= exp <= threshold:
                return True
        return False


class ContractDetailSerializer(serializers.ModelSerializer):
    start_date = JalaliDateField(required=False, allow_null=True)
    finish_date = JalaliDateField(required=False, allow_null=True)
    performance_guarantee_expiry = JalaliDateField(required=False, allow_null=True)
    advance_guarantee_expiry = JalaliDateField(required=False, allow_null=True)
    items = ContractItemSerializer(many=True, read_only=True)
    change_orders = ChangeOrderSerializer(many=True, read_only=True)
    effective_amount = serializers.SerializerMethodField()
    advance_amount = serializers.SerializerMethodField()

    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'contract_type', 'counterparty',
            'start_date', 'finish_date', 'original_amount', 'adjusted_amount',
            'effective_amount', 'advance_amount', 'advance_payment_pct',
            'retention_pct', 'insurance_pct', 'tax_pct',
            'performance_guarantee_amount', 'performance_guarantee_expiry',
            'advance_guarantee_amount', 'advance_guarantee_expiry',
            'status', 'file_url', 'notes', 'items', 'change_orders',
        ]
        read_only_fields = ['id']

    def get_effective_amount(self, obj):
        return float(obj.effective_amount)

    def get_advance_amount(self, obj):
        return obj.advance_amount


class ContractWriteSerializer(serializers.ModelSerializer):
    start_date = JalaliDateField(required=False, allow_null=True)
    finish_date = JalaliDateField(required=False, allow_null=True)
    performance_guarantee_expiry = JalaliDateField(required=False, allow_null=True)
    advance_guarantee_expiry = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = Contract
        fields = [
            'contract_number', 'contract_type', 'counterparty',
            'start_date', 'finish_date', 'original_amount', 'adjusted_amount',
            'advance_payment_pct', 'retention_pct', 'insurance_pct', 'tax_pct',
            'performance_guarantee_amount', 'performance_guarantee_expiry',
            'advance_guarantee_amount', 'advance_guarantee_expiry',
            'status', 'file_url', 'notes',
        ]


class IPCItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPCItem
        fields = [
            'id', 'contract_item', 'description', 'unit', 'unit_price',
            'qty_previous', 'qty_current', 'qty_cumulative',
            'amount_current', 'amount_cumulative',
        ]
        read_only_fields = ['id']


class IPCDeductionSerializer(serializers.ModelSerializer):
    amount_display = serializers.SerializerMethodField()

    class Meta:
        model = IPCDeduction
        fields = ['id', 'deduction_type', 'amount', 'amount_display', 'description']
        read_only_fields = ['id']

    def get_amount_display(self, obj):
        return _format_amount(obj.amount)


class IPCListSerializer(serializers.ModelSerializer):
    period_start = JalaliDateField(read_only=True)
    period_end = JalaliDateField(read_only=True)
    gross_amount_display = serializers.SerializerMethodField()
    net_amount_display = serializers.SerializerMethodField()
    days_overdue = serializers.SerializerMethodField()
    contract_number = serializers.CharField(source='contract.contract_number', read_only=True)

    class Meta:
        model = IPC
        fields = [
            'id', 'ipc_number', 'contract', 'contract_number',
            'period_start', 'period_end', 'gross_amount', 'gross_amount_display',
            'net_amount', 'net_amount_display', 'status', 'approval_date',
            'planned_payment_date', 'actual_payment_date', 'days_overdue',
        ]

    def get_gross_amount_display(self, obj):
        return _format_amount(obj.gross_amount)

    def get_net_amount_display(self, obj):
        return _format_amount(obj.net_amount)

    def get_days_overdue(self, obj):
        from datetime import date

        if (
            obj.status == 'approved'
            and obj.planned_payment_date
            and obj.planned_payment_date < date.today()
            and not obj.actual_payment_date
        ):
            return (date.today() - obj.planned_payment_date).days
        return None


class IPCDetailSerializer(serializers.ModelSerializer):
    period_start = JalaliDateField(required=False, allow_null=True)
    period_end = JalaliDateField(required=False, allow_null=True)
    prepared_date = JalaliDateField(required=False, allow_null=True)
    items = IPCItemSerializer(many=True, read_only=True)
    deductions = IPCDeductionSerializer(many=True, read_only=True)
    deductions_total = serializers.SerializerMethodField()
    net_amount_computed = serializers.SerializerMethodField()
    contract_number = serializers.CharField(source='contract.contract_number', read_only=True)

    class Meta:
        model = IPC
        fields = [
            'id', 'ipc_number', 'contract', 'contract_number',
            'period_start', 'period_end', 'prepared_date',
            'submitted_date', 'approval_date', 'planned_payment_date', 'actual_payment_date',
            'gross_amount', 'net_amount', 'status', 'rejection_reason', 'notes',
            'items', 'deductions', 'deductions_total', 'net_amount_computed',
        ]
        read_only_fields = ['id', 'ipc_number', 'gross_amount', 'net_amount']

    def get_deductions_total(self, obj):
        total = sum(float(d.amount) for d in obj.deductions.filter(is_deleted=False))
        return total

    def get_net_amount_computed(self, obj):
        deductions = self.get_deductions_total(obj)
        return float(obj.gross_amount or 0) - deductions


class IPCCreateSerializer(serializers.Serializer):
    contract_id = serializers.UUIDField()
    period_start = JalaliDateField(required=False, allow_null=True)
    period_end = JalaliDateField(required=False, allow_null=True)
    prepared_date = JalaliDateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
