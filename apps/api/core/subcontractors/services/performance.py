from subcontractors.models import Subcontractor, SubcontractorPerformanceScore, SubcontractorWarning
from subcontractors.services.risk_service import compute_risk_flag

class SubcontractorPerformanceService:
    def create_score(self, subcontractor: Subcontractor, validated_data: dict, user) -> SubcontractorPerformanceScore:
        score = SubcontractorPerformanceScore.objects.create(
            subcontractor=subcontractor,
            evaluator=user,
            created_by=user,
            updated_by=user,
            **validated_data,
        )
        self._evaluate_risk(subcontractor)
        return score

    def update_score(self, score: SubcontractorPerformanceScore, validated_data: dict, user) -> SubcontractorPerformanceScore:
        for attr, val in validated_data.items():
            setattr(score, attr, val)
        score.updated_by = user
        score.save()
        self._evaluate_risk(score.subcontractor)
        return score

    def create_warning(self, subcontractor: Subcontractor, validated_data: dict, user) -> SubcontractorWarning:
        warning = SubcontractorWarning.objects.create(
            subcontractor=subcontractor,
            issued_by=user,
            created_by=user,
            updated_by=user,
            **validated_data,
        )
        self._evaluate_risk(subcontractor)
        return warning

    def update_warning(self, warning: SubcontractorWarning, validated_data: dict, user) -> SubcontractorWarning:
        for attr, val in validated_data.items():
            setattr(warning, attr, val)

        from datetime import date
        if warning.resolved and not warning.resolved_date:
            warning.resolved_date = date.today()

        warning.updated_by = user
        warning.save()
        self._evaluate_risk(warning.subcontractor)
        return warning

    def _evaluate_risk(self, subcontractor: Subcontractor):
        flag, reasons = compute_risk_flag(subcontractor)
        if flag:
            try:
                from alerts.services.evaluation import fire_subcontractor_at_risk
                fire_subcontractor_at_risk(subcontractor, reasons)
            except Exception:
                pass
