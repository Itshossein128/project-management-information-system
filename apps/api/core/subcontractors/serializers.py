from rest_framework import serializers

from common.serializers import JalaliDateField
from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorWarning


class SubcontractorSerializer(serializers.ModelSerializer):
    latest_score = serializers.SerializerMethodField()
    financial_summary = serializers.SerializerMethodField()
    risk_flag = serializers.SerializerMethodField()
    risk_reasons = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()

    class Meta:
        model = Subcontractor
        fields = [
            'id', 'company_name', 'contract', 'discipline', 'responsible_person',
            'phone', 'status', 'latest_score', 'financial_summary',
            'risk_flag', 'risk_reasons', 'warning_count',
        ]
        read_only_fields = ['id']

    def _risk(self, obj):
        if not hasattr(obj, '_risk_cache'):
            from subcontractors.services.risk_service import compute_risk_flag
            obj._risk_cache = compute_risk_flag(obj)
        return obj._risk_cache

    def get_latest_score(self, obj):
        s = obj.scores.filter(is_deleted=False).order_by('-score_date').first()
        return float(s.overall_score) if s and s.overall_score is not None else None

    def get_financial_summary(self, obj):
        from subcontractors.services.risk_service import financial_summary
        return financial_summary(obj)

    def get_risk_flag(self, obj):
        return self._risk(obj)[0]

    def get_risk_reasons(self, obj):
        return self._risk(obj)[1]

    def get_warning_count(self, obj):
        return obj.warnings.filter(is_deleted=False, resolved=False).count()


class SubcontractorDetailSerializer(SubcontractorSerializer):
    scores = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()

    class Meta(SubcontractorSerializer.Meta):
        fields = SubcontractorSerializer.Meta.fields + ['scores', 'warnings']

    def get_scores(self, obj):
        return PerformanceScoreSerializer(
            obj.scores.filter(is_deleted=False).order_by('-score_date')[:20],
            many=True,
        ).data

    def get_warnings(self, obj):
        return WarningSerializer(
            obj.warnings.filter(is_deleted=False).order_by('-warning_date'),
            many=True,
        ).data


class PerformanceScoreSerializer(serializers.ModelSerializer):
    score_date = JalaliDateField()

    class Meta:
        model = SubcontractorPerformanceScore
        fields = [
            'id', 'score_date', 'progress_score', 'quality_score', 'hse_score',
            'payment_compliance_score', 'cooperation_score', 'overall_score',
            'evaluator', 'notes',
        ]
        read_only_fields = ['id', 'overall_score']


class WarningSerializer(serializers.ModelSerializer):
    warning_date = JalaliDateField()
    resolved_date = JalaliDateField(required=False, allow_null=True)

    class Meta:
        model = SubcontractorWarning
        fields = [
            'id', 'warning_date', 'warning_type', 'reason',
            'issued_by', 'resolved', 'resolved_date',
        ]
        read_only_fields = ['id', 'issued_by']
