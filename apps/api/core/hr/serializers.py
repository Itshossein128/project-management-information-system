from decimal import Decimal

from rest_framework import serializers

from authentication.models import User
from common.serializers import JalaliDateField
from hr.models import (
    ApprovedLaborRate,
    CapacityException,
    LeaveRequest,
    OvertimeRequest,
    ResourceAllocation,
)
from permissions.project import member_has_codename


class OvertimeRequestSerializer(serializers.ModelSerializer):
    overtime_date = JalaliDateField()
    request_date = JalaliDateField(read_only=True)
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)

    class Meta:
        model = OvertimeRequest
        fields = [
            'id',
            'requester',
            'requester_name',
            'department',
            'request_date',
            'overtime_date',
            'start_time',
            'end_time',
            'requested_hours',
            'approved_hours',
            'reason',
            'status',
            'supervisor_notes',
        ]
        read_only_fields = ['id', 'request_date', 'status', 'approved_hours']

    def validate_reason(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError('علت باید حداقل ۱۰ کاراکتر باشد.')
        return value


class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_date = JalaliDateField()
    request_date = JalaliDateField(read_only=True)
    start_datetime = serializers.DateTimeField(required=False, allow_null=True)
    end_datetime = serializers.DateTimeField(required=False, allow_null=True)
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    warning = serializers.SerializerMethodField()

    class Meta:
        model = LeaveRequest
        fields = [
            'id',
            'requester',
            'requester_name',
            'department',
            'request_type',
            'request_date',
            'leave_date',
            'start_datetime',
            'end_datetime',
            'replacement_user',
            'mission_subject',
            'status',
            'warning',
        ]
        read_only_fields = ['id', 'request_date', 'status']

    def get_warning(self, obj):
        if not obj.replacement_user_id:
            return 'جایگزین مشخص نشده است'
        return None

    def validate(self, attrs):
        req_type = attrs.get('request_type', getattr(self.instance, 'request_type', None))
        if req_type == 'mission' and not attrs.get('mission_subject', getattr(self.instance, 'mission_subject', '')):
            raise serializers.ValidationError({'mission_subject': 'موضوع مأموریت الزامی است.'})
        if req_type == 'hourly':
            if not attrs.get('start_datetime') or not attrs.get('end_datetime'):
                raise serializers.ValidationError('برای مرخصی ساعتی، زمان شروع و پایان الزامی است.')
        return attrs


class PersonDossierSerializer(serializers.ModelSerializer):
    org_unit_name = serializers.CharField(source='org_unit.name', read_only=True, allow_null=True)
    supervisor_name = serializers.CharField(source='supervisor.full_name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id',
            'full_name',
            'email',
            'mobile',
            'status',
            'is_active',
            'organization',
            'skills',
            'qualifications',
            'org_unit_id',
            'org_unit_name',
            'supervisor_id',
            'supervisor_name',
            'default_capacity_percent',
        ]
        read_only_fields = [
            'id',
            'full_name',
            'email',
            'mobile',
            'is_active',
            'organization',
            'org_unit_id',
            'supervisor_id',
            'skills',
            'qualifications',
            'status',
            'default_capacity_percent',
        ]


class ResourceAllocationSerializer(serializers.ModelSerializer):
    person_id = serializers.UUIDField(read_only=True)
    wbs_id = serializers.UUIDField(allow_null=True, required=False)
    activity_id = serializers.UUIDField(allow_null=True, required=False)
    supervisor_id = serializers.UUIDField(allow_null=True, required=False)
    capacity_exception_id = serializers.UUIDField(allow_null=True, read_only=True)

    class Meta:
        model = ResourceAllocation
        fields = [
            'id',
            'person_id',
            'wbs_id',
            'activity_id',
            'start_date',
            'end_date',
            'role',
            'capacity_percent',
            'capacity_hours',
            'work_location',
            'supervisor_id',
            'status',
            'has_capacity_exception',
            'capacity_exception_id',
        ]
        read_only_fields = ['id', 'has_capacity_exception', 'capacity_exception_id']


class ResourceAllocationWriteSerializer(serializers.Serializer):
    person_id = serializers.UUIDField()
    wbs_id = serializers.UUIDField(required=False, allow_null=True)
    activity_id = serializers.UUIDField(required=False, allow_null=True)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    role = serializers.CharField(max_length=120)
    capacity_percent = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    capacity_hours = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    work_location = serializers.CharField(required=False, allow_blank=True, default='')
    supervisor_id = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.CharField(required=False)
    capacity_exception_id = serializers.UUIDField(required=False, allow_null=True)


class CapacityExceptionSerializer(serializers.ModelSerializer):
    person_id = serializers.UUIDField(read_only=True)
    allocation_id = serializers.UUIDField(allow_null=True, required=False)

    class Meta:
        model = CapacityException
        fields = [
            'id',
            'person_id',
            'allocation_id',
            'start_date',
            'end_date',
            'reason',
            'status',
            'requested_capacity_percent',
            'overlapping_snapshot',
            'submitted_at',
            'decided_by',
            'decided_at',
            'decision_notes',
        ]
        read_only_fields = fields


class CapacityExceptionWriteSerializer(serializers.Serializer):
    person_id = serializers.UUIDField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    reason = serializers.CharField(required=False, allow_blank=True, default='')
    requested_capacity_percent = serializers.DecimalField(max_digits=8, decimal_places=2)
    allocation_id = serializers.UUIDField(required=False, allow_null=True)
    submit = serializers.BooleanField(required=False, default=False)


class ApprovedLaborRateSerializer(serializers.ModelSerializer):
    person_id = serializers.UUIDField(allow_null=True, required=False)

    class Meta:
        model = ApprovedLaborRate
        fields = [
            'id',
            'person_id',
            'amount',
            'currency',
            'effective_from',
            'effective_to',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        project_id = self.context.get('project_pk') or instance.project_id
        if request is not None and not member_has_codename(request.user, project_id, 'view_wage'):
            data.pop('amount', None)
        return data


class ApprovedLaborRateWriteSerializer(serializers.Serializer):
    person_id = serializers.UUIDField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField(max_length=3, required=False, default='IRR')
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)


class LaborCostEstimateRequestSerializer(serializers.Serializer):
    person_id = serializers.UUIDField()
    approved_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    as_of = serializers.DateField(required=False)


class LaborCostEstimateResponseSerializer(serializers.Serializer):
    amount = serializers.CharField(allow_null=True)
    currency = serializers.CharField(allow_null=True)
    rate_amount = serializers.CharField(allow_null=True, required=False)
    hours = serializers.CharField()
    warning = serializers.CharField(allow_null=True)
