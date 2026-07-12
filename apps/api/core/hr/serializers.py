from rest_framework import serializers

from common.serializers import JalaliDateField
from hr.models import LeaveRequest, OvertimeRequest


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
