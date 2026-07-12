"""Cost control serializers."""

from rest_framework import serializers

from common.serializers import JalaliDateField
from cost_control.models import ActualCost, Budget, CostPool
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

    class Meta:
        model = Budget
        fields = [
            'id',
            'wbs',
            'activity',
            'wbs_code',
            'wbs_name',
            'activity_code',
            'activity_name',
            'cost_category',
            'budget_amount',
            'budget_amount_display',
            'notes',
        ]
        read_only_fields = ['id']

    def get_budget_amount_display(self, obj):
        return _format_amount(obj.budget_amount)


class BudgetBulkItemSerializer(serializers.Serializer):
    wbs = serializers.UUIDField(required=False, allow_null=True)
    activity = serializers.UUIDField(required=False, allow_null=True)
    cost_category = serializers.ChoiceField(choices=Budget._meta.get_field('cost_category').choices)
    budget_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        if not attrs.get('wbs') and not attrs.get('activity'):
            raise serializers.ValidationError('At least one of wbs or activity is required.')
        return attrs


class ActualCostSerializer(serializers.ModelSerializer):
    cost_date = JalaliDateField()
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
            'wbs_code',
            'activity_code',
            'cost_date',
            'cost_category',
            'amount',
            'amount_display',
            'description',
            'invoice_number',
            'supplier',
            'supplier_name',
            'cost_type',
            'confidence_level',
            'allocation_method',
            'cost_pool',
            'daily_report',
            'is_auto_created',
        ]
        read_only_fields = ['id', 'daily_report', 'is_auto_created']

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
