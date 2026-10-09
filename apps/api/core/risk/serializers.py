from rest_framework import serializers

from common.serializers import JalaliDateField
from contracts.models import Contract
from cost_control.models import CostBreakdownNode
from documents.models import Correspondence
from field_reports.models import DailyReport
from projects.models import Activity
from risk.models import (
    BarrierStatus,
    CorrectiveAction,
    EventType,
    HseEvent,
    Inspection,
    Nonconformity,
    RiskAction,
    RiskActionStatus,
    RiskEvent,
    RiskStatus,
    SafetyTraining,
    WorkPermit,
)
from risk.services.score_service import (
    compute_composite_score,
    default_status_for_incomplete_score,
    normalize_status,
)


def _closed_like(status: str) -> bool:
    return status in (RiskStatus.CLOSED, BarrierStatus.RESOLVED)


_BARRIER_STATUS_CHOICES = list(RiskStatus.choices) + [
    (BarrierStatus.IN_PROGRESS, 'در حال پیگیری'),
    (BarrierStatus.RESOLVED, 'رفع شده'),
]


class BarrierSerializer(serializers.ModelSerializer):
    log_date = JalaliDateField(source='event_date')
    resolved_date = JalaliDateField(required=False, allow_null=True)
    # Accept legacy barrier statuses; normalize to FR codes in validate()
    status = serializers.ChoiceField(choices=_BARRIER_STATUS_CHOICES, required=False)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    status_label = serializers.SerializerMethodField()
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

    def get_status_label(self, obj):
        if obj.status == RiskStatus.CLOSED:
            return 'رفع شده'
        if obj.status == RiskStatus.UNDER_REVIEW:
            return 'در حال پیگیری'
        return obj.get_status_display()

    def get_responsible_user_name(self, obj):
        if not obj.responsible_user:
            return ''
        return obj.responsible_user.get_full_name() or obj.responsible_user.username

    def validate(self, attrs):
        if 'status' in attrs:
            attrs['status'] = normalize_status(attrs['status']) or attrs['status']
        status = attrs.get('status', getattr(self.instance, 'status', RiskStatus.OPEN))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if _closed_like(status) and not resolved_date:
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
    due_date = JalaliDateField(required=False, allow_null=True)
    event_type_label = serializers.CharField(source='get_event_type_display', read_only=True)
    severity_label = serializers.CharField(source='get_severity_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    category_label = serializers.CharField(source='get_category_display', read_only=True)
    acknowledge_open_actions = serializers.BooleanField(required=False, write_only=True, default=False)
    open_actions_count = serializers.SerializerMethodField()
    action_text = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = RiskEvent
        fields = [
            'id',
            'activity',
            'event_date',
            'event_type',
            'event_type_label',
            'description',
            'cause',
            'consequence',
            'response',
            'category',
            'category_label',
            'impact_on_schedule',
            'impact_on_cost',
            'impact_on_quality',
            'impact_on_safety',
            'impact_on_contract',
            'impact_on_liquidity',
            'responsible_party',
            'time_impact_days',
            'cost_impact',
            'probability',
            'probability_level',
            'severity',
            'severity_label',
            'impact_severity_level',
            'composite_score',
            'status',
            'status_label',
            'corrective_action',
            'action_text',
            'target_resolution_date',
            'due_date',
            'resolved_date',
            'owner',
            'responsible_user',
            'cost_item',
            'contract',
            'related_decision_ref',
            'related_decision_note',
            'related_daily_report',
            'related_correspondence',
            'acknowledge_open_actions',
            'open_actions_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'composite_score', 'created_at', 'updated_at', 'open_actions_count']

    def get_open_actions_count(self, obj):
        return obj.actions.filter(status=RiskActionStatus.OPEN, is_deleted=False).count()

    def validate_probability_level(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('سطح احتمال باید بین ۱ و ۵ باشد.')
        return value

    def validate_impact_severity_level(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError('سطح شدت اثر باید بین ۱ و ۵ باشد.')
        return value

    def validate(self, attrs):
        if 'status' in attrs:
            attrs['status'] = normalize_status(attrs['status']) or attrs['status']

        status = attrs.get('status', getattr(self.instance, 'status', RiskStatus.OPEN))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if _closed_like(status) and not resolved_date and status == BarrierStatus.RESOLVED:
            raise serializers.ValidationError(
                {'resolved_date': 'برای وضعیت «رفع شده» تاریخ رفع الزامی است.'},
            )

        project_id = self.context.get('project_id')
        if project_id is None and self.instance is not None:
            project_id = self.instance.project_id

        activity = attrs.get('activity')
        if activity is not None:
            act = activity if isinstance(activity, Activity) else Activity.objects.filter(pk=activity).first()
            if act is None or str(act.project_id) != str(project_id):
                raise serializers.ValidationError({'activity': 'فعالیت باید متعلق به همین پروژه باشد.'})

        cost_item = attrs.get('cost_item')
        if cost_item is not None:
            node = (
                cost_item
                if isinstance(cost_item, CostBreakdownNode)
                else CostBreakdownNode.objects.filter(pk=cost_item).first()
            )
            if node is None or str(node.project_id) != str(project_id):
                raise serializers.ValidationError({'cost_item': 'قلم هزینه باید متعلق به همین پروژه باشد.'})

        contract = attrs.get('contract')
        if contract is not None:
            c = contract if isinstance(contract, Contract) else Contract.objects.filter(pk=contract).first()
            if c is None or str(c.project_id) != str(project_id):
                raise serializers.ValidationError({'contract': 'قرارداد باید متعلق به همین پروژه باشد.'})

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

    def create(self, validated_data):
        validated_data.pop('acknowledge_open_actions', None)
        action_text = validated_data.pop('action_text', None)
        if action_text:
            validated_data['corrective_action'] = action_text
        p_level = validated_data.get('probability_level')
        i_level = validated_data.get('impact_severity_level')
        validated_data['composite_score'] = compute_composite_score(p_level, i_level)
        if 'status' not in validated_data or not validated_data.get('status'):
            default = default_status_for_incomplete_score(p_level, i_level, explicit_status=None)
            if default:
                validated_data['status'] = default
        due = validated_data.get('due_date')
        if due and not validated_data.get('target_resolution_date'):
            validated_data['target_resolution_date'] = due
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('acknowledge_open_actions', None)
        action_text = validated_data.pop('action_text', None)
        if action_text is not None:
            validated_data['corrective_action'] = action_text
        p_level = validated_data.get(
            'probability_level',
            instance.probability_level,
        )
        i_level = validated_data.get(
            'impact_severity_level',
            instance.impact_severity_level,
        )
        if 'probability_level' in validated_data or 'impact_severity_level' in validated_data:
            validated_data['composite_score'] = compute_composite_score(p_level, i_level)
        due = validated_data.get('due_date')
        if due and 'target_resolution_date' not in validated_data:
            validated_data['target_resolution_date'] = due
        return super().update(instance, validated_data)


class RiskActionSerializer(serializers.ModelSerializer):
    due_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = RiskAction
        fields = [
            'id',
            'risk_event',
            'description',
            'due_date',
            'owner',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_risk_event(self, value):
        project_id = self.context.get('project_id')
        if value is not None and str(value.project_id) != str(project_id):
            raise serializers.ValidationError('رویداد ریسک باید متعلق به همین پروژه باشد.')
        return value


class InspectionSerializer(serializers.ModelSerializer):
    inspection_date = JalaliDateField()

    class Meta:
        model = Inspection
        fields = [
            'id',
            'wbs',
            'responsible_user',
            'inspection_date',
            'stage',
            'result',
            'description',
            'activity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        project_id = self.context.get('project_id')
        wbs = attrs.get('wbs', getattr(self.instance, 'wbs', None))
        responsible = attrs.get('responsible_user', getattr(self.instance, 'responsible_user', None))
        inspection_date = attrs.get('inspection_date', getattr(self.instance, 'inspection_date', None))
        errors = {}
        if wbs is None:
            errors['wbs'] = 'WBS الزامی است.'
        elif str(wbs.project_id) != str(project_id):
            errors['wbs'] = 'WBS باید متعلق به همین پروژه باشد.'
        if responsible is None:
            errors['responsible_user'] = 'مسئول الزامی است.'
        if inspection_date is None:
            errors['inspection_date'] = 'تاریخ الزامی است.'
        activity = attrs.get('activity')
        if activity is not None and str(activity.project_id) != str(project_id):
            errors['activity'] = 'فعالیت باید متعلق به همین پروژه باشد.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class NonconformitySerializer(serializers.ModelSerializer):
    raised_date = JalaliDateField()

    class Meta:
        model = Nonconformity
        fields = [
            'id',
            'inspection',
            'wbs',
            'description',
            'status',
            'raised_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        project_id = self.context.get('project_id')
        inspection = attrs.get('inspection')
        if inspection is not None:
            if str(inspection.project_id) != str(project_id):
                raise serializers.ValidationError({'inspection': 'بازرسی باید متعلق به همین پروژه باشد.'})
            if 'wbs' not in attrs or attrs.get('wbs') is None:
                attrs['wbs'] = inspection.wbs
        wbs = attrs.get('wbs')
        if wbs is not None and str(wbs.project_id) != str(project_id):
            raise serializers.ValidationError({'wbs': 'WBS باید متعلق به همین پروژه باشد.'})
        return attrs


class CorrectiveActionSerializer(serializers.ModelSerializer):
    due_date = JalaliDateField(required=False, allow_null=True)
    completed_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = CorrectiveAction
        fields = [
            'id',
            'nonconformity',
            'description',
            'responsible_user',
            'due_date',
            'status',
            'completed_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_nonconformity(self, value):
        project_id = self.context.get('project_id')
        if str(value.project_id) != str(project_id):
            raise serializers.ValidationError('عدم انطباق باید متعلق به همین پروژه باشد.')
        return value


class HseEventSerializer(serializers.ModelSerializer):
    event_date = JalaliDateField()

    class Meta:
        model = HseEvent
        fields = [
            'id',
            'kind',
            'event_date',
            'description',
            'wbs',
            'severity',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_wbs(self, value):
        if value is None:
            return value
        project_id = self.context.get('project_id')
        if str(value.project_id) != str(project_id):
            raise serializers.ValidationError('WBS باید متعلق به همین پروژه باشد.')
        return value


class WorkPermitSerializer(serializers.ModelSerializer):
    permit_date = JalaliDateField()

    class Meta:
        model = WorkPermit
        fields = [
            'id',
            'permit_date',
            'permit_type',
            'responsible_user',
            'description',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SafetyTrainingSerializer(serializers.ModelSerializer):
    training_date = JalaliDateField()

    class Meta:
        model = SafetyTraining
        fields = [
            'id',
            'training_date',
            'topic',
            'trainer_or_responsible',
            'responsible_user',
            'attendees_count',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
