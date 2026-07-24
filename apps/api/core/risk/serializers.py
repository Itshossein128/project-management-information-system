from rest_framework import serializers

from common.serializers import JalaliDateField
from documents.models import Correspondence
from field_reports.models import DailyReport
from risk.models import BarrierStatus, EventType, RiskEvent, Severity


class BarrierSerializer(serializers.ModelSerializer):
    log_date = JalaliDateField(source='event_date')
    resolved_date = JalaliDateField(required=False, allow_null=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    responsible_user_name = serializers.SerializerMethodField()

    class Meta:
        model = RiskEvent
        fields = [
            'id',
            'log_date',
            'description',
            'category',
            'category_label',
            'impact_on_schedule',
            'impact_on_cost',
            'status',
            'status_label',
            'resolved_date',
            'corrective_action',
            'responsible_user',
            'responsible_user_name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_responsible_user_name(self, obj):
        if not obj.responsible_user:
            return ''
        return obj.responsible_user.get_full_name() or obj.responsible_user.username

    def validate(self, attrs):
        status = attrs.get('status', getattr(self.instance, 'status', BarrierStatus.OPEN))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if status == BarrierStatus.RESOLVED and not resolved_date:
            raise serializers.ValidationError(
                {'resolved_date': 'برای وضعیت «رفع شده» تاریخ رفع الزامی است.'},
            )
        return attrs


class BarrierCreateSerializer(BarrierSerializer):
    log_date = JalaliDateField(source='event_date')

    def create(self, validated_data):
        validated_data['event_type'] = EventType.BARRIER
        return super().create(validated_data)


class RiskEventSerializer(serializers.ModelSerializer):
    event_date = JalaliDateField(required=False, allow_null=True)
    resolved_date = JalaliDateField(required=False, allow_null=True)
    target_resolution_date = JalaliDateField(required=False, allow_null=True)
    event_type_label = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_label = serializers.CharField(source='get_severity_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = RiskEvent
        fields = [
            'id',
            'activity',
            'event_date',
            'event_type',
            'event_type_label',
            'description',
            'category',
            'category_label',
            'impact_on_schedule',
            'impact_on_cost',
            'responsible_party',
            'time_impact_days',
            'cost_impact',
            'probability',
            'severity',
            'severity_label',
            'status',
            'status_label',
            'corrective_action',
            'target_resolution_date',
            'resolved_date',
            'owner',
            'responsible_user',
            'related_daily_report',
            'related_correspondence',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        status = attrs.get('status', getattr(self.instance, 'status', BarrierStatus.OPEN))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if status == BarrierStatus.RESOLVED and not resolved_date:
            raise serializers.ValidationError(
                {'resolved_date': 'برای وضعیت «رفع شده» تاریخ رفع الزامی است.'},
            )

        project_id = self.context.get('project_id')
        if project_id is None and self.instance is not None:
            project_id = self.instance.project_id

        report = attrs.get('related_daily_report')
        if report is None and 'related_daily_report' not in attrs and self.instance:
            report = self.instance.related_daily_report
        if report is not None:
            report_obj = report if isinstance(report, DailyReport) else DailyReport.objects.filter(pk=report).first()
            if report_obj is None:
                raise serializers.ValidationError({'related_daily_report': 'گزارش روزانه یافت نشد.'})
            if str(report_obj.project_id) != str(project_id):
                raise serializers.ValidationError(
                    {'related_daily_report': 'گزارش روزانه باید متعلق به همین پروژه باشد.'},
                )

        corr = attrs.get('related_correspondence')
        if corr is None and 'related_correspondence' not in attrs and self.instance:
            corr = self.instance.related_correspondence
        if corr is not None:
            corr_obj = corr if isinstance(corr, Correspondence) else Correspondence.objects.filter(pk=corr).first()
            if corr_obj is None:
                raise serializers.ValidationError({'related_correspondence': 'مکاتبه یافت نشد.'})
            if str(corr_obj.project_id) != str(project_id):
                raise serializers.ValidationError(
                    {'related_correspondence': 'مکاتبه باید متعلق به همین پروژه باشد.'},
                )

        probability = attrs.get('probability', getattr(self.instance, 'probability', None))
        if probability is not None and (float(probability) < 0 or float(probability) > 1):
            raise serializers.ValidationError({'probability': 'احتمال باید بین ۰ و ۱ باشد.'})

        return attrs
