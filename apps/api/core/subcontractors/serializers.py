from rest_framework import serializers

from common.serializers import JalaliDateField
from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorWarning

SCORE_FIELDS = (
    'progress_score',
    'quality_score',
    'hse_score',
    'payment_compliance_score',
    'cooperation_score',
)


def _validate_score_range(value, field_name):
    if value is not None and (float(value) < 0 or float(value) > 10):
        raise serializers.ValidationError(f'{field_name} باید بین 0 و 10 باشد')
    return value


class SubcontractorSerializer(serializers.ModelSerializer):
    latest_score = serializers.SerializerMethodField()
    latest_score_date = serializers.SerializerMethodField()
    financial_summary = serializers.SerializerMethodField()
    risk_flag = serializers.SerializerMethodField()
    risk_reasons = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()
    active_warning_types = serializers.SerializerMethodField()

    class Meta:
        model = Subcontractor
        fields = [
            'id', 'company_name', 'contract', 'discipline', 'responsible_person',
            'phone', 'status', 'latest_score', 'latest_score_date', 'financial_summary',
            'risk_flag', 'risk_reasons', 'warning_count', 'active_warning_types',
        ]
        read_only_fields = ['id']

    def _risk(self, obj):
        if not hasattr(obj, '_risk_cache'):
            from subcontractors.services.risk_service import compute_risk_flag
            obj._risk_cache = compute_risk_flag(obj)
        return obj._risk_cache

    def get_latest_score(self, obj):
        valid_scores = [s for s in obj.scores.all() if not s.is_deleted]
        if not valid_scores:
            return None
        s = max(valid_scores, key=lambda x: x.score_date)
        return float(s.overall_score) if s.overall_score is not None else None

    def get_latest_score_date(self, obj):
        valid_scores = [s for s in obj.scores.all() if not s.is_deleted]
        if not valid_scores:
            return None
        s = max(valid_scores, key=lambda x: x.score_date)
        return s.score_date.isoformat()

    def get_financial_summary(self, obj):
        from subcontractors.services.risk_service import financial_summary
        summary = financial_summary(obj)
        return {
            'outstanding': summary['outstanding'],
            'retention_held': summary['retention_held'],
        }

    def get_risk_flag(self, obj):
        return self._risk(obj)[0]

    def get_risk_reasons(self, obj):
        return self._risk(obj)[1]

    def get_warning_count(self, obj):
        return sum(1 for w in obj.warnings.all() if not w.is_deleted and not w.resolved)

    def get_active_warning_types(self, obj):
        return list(set(
            w.warning_type for w in obj.warnings.all() if not w.is_deleted and not w.resolved
        ))


class SubcontractorDetailSerializer(SubcontractorSerializer):
    contract_summary = serializers.SerializerMethodField()
    financial_status = serializers.SerializerMethodField()
    performance_history = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    recent_activities = serializers.SerializerMethodField()
    average_overall = serializers.SerializerMethodField()
    trend = serializers.SerializerMethodField()

    class Meta(SubcontractorSerializer.Meta):
        fields = SubcontractorSerializer.Meta.fields + [
            'contract_summary',
            'financial_status',
            'performance_history',
            'warnings',
            'recent_activities',
            'average_overall',
            'trend',
        ]

    def get_financial_summary(self, obj):
        from subcontractors.services.risk_service import financial_summary
        return financial_summary(obj)

    def get_contract_summary(self, obj):
        if not obj.contract_id:
            return None
        c = obj.contract
        return {
            'id': str(c.id),
            'contract_number': c.contract_number,
            'counterparty': c.counterparty,
            'contract_type': c.contract_type,
            'original_amount': float(c.original_amount or 0),
            'adjusted_amount': float(c.adjusted_amount or c.original_amount or 0),
            'status': c.status,
        }

    def get_financial_status(self, obj):
        from subcontractors.services.risk_service import financial_summary
        return financial_summary(obj)

    def get_performance_history(self, obj):
        return PerformanceScoreSerializer(
            obj.scores.filter(is_deleted=False).order_by('-score_date')[:10],
            many=True,
        ).data

    def get_warnings(self, obj):
        return WarningSerializer(
            obj.warnings.filter(is_deleted=False).order_by('-warning_date'),
            many=True,
        ).data

    def get_recent_activities(self, obj):
        from field_reports.models import DailyReportActivity

        qs = (
            DailyReportActivity.objects.filter(
                report__project_id=obj.project_id,
                is_deleted=False,
                subcontractor_name__icontains=obj.company_name,
            )
            .select_related('report')
            .order_by('-report__report_date')[:20]
        )
        return [
            {
                'id': str(row.id),
                'report_id': str(row.report_id),
                'report_date': row.report.report_date.isoformat(),
                'shift': row.shift,
                'zone': row.zone,
                'block': row.block,
                'floor': row.floor,
                'activity_description': row.activity_description,
                'headcount': row.headcount,
                'quantity': float(row.quantity) if row.quantity is not None else None,
                'unit': row.unit,
            }
            for row in qs
        ]

    def get_average_overall(self, obj):
        from subcontractors.services.risk_service import average_overall_score
        return average_overall_score(obj)

    def get_trend(self, obj):
        from subcontractors.services.risk_service import score_trend
        return score_trend(obj)


class PerformanceScoreSerializer(serializers.ModelSerializer):
    score_date = JalaliDateField()

    class Meta:
        model = SubcontractorPerformanceScore
        fields = [
            'id', 'score_date', 'progress_score', 'quality_score', 'hse_score',
            'payment_compliance_score', 'cooperation_score', 'overall_score',
            'evaluator', 'notes',
        ]
        read_only_fields = ['id', 'overall_score', 'evaluator']

    def validate(self, attrs):
        for field in SCORE_FIELDS:
            if field in attrs:
                _validate_score_range(attrs[field], field)
        return attrs


class WarningSerializer(serializers.ModelSerializer):
    warning_date = JalaliDateField()
    resolved_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = SubcontractorWarning
        fields = [
            'id', 'warning_date', 'warning_type', 'reason',
            'issued_by', 'resolved', 'resolved_date', 'resolution_notes',
        ]
        read_only_fields = ['id', 'issued_by']

    def validate(self, attrs):
        resolved = attrs.get('resolved', getattr(self.instance, 'resolved', False))
        resolved_date = attrs.get('resolved_date', getattr(self.instance, 'resolved_date', None))
        if resolved and not resolved_date:
            raise serializers.ValidationError({'resolved_date': 'تاریخ رفع اخطار الزامی است'})
        return attrs
