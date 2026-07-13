from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel


class SubcontractorStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SUSPENDED = 'suspended', 'Suspended'
    COMPLETED = 'completed', 'Completed'
    TERMINATED = 'terminated', 'Terminated'


class Subcontractor(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='subcontractors')
    company_name = models.CharField(max_length=120)
    contract = models.ForeignKey(
        'contracts.Contract',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcontractors',
    )
    discipline = models.CharField(max_length=60, blank=True, default='')
    responsible_person = models.CharField(max_length=80, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    status = models.CharField(max_length=20, choices=SubcontractorStatus.choices, default=SubcontractorStatus.ACTIVE)

    class Meta:
        db_table = 'subcontractors'


class SubcontractorPerformanceScore(AuditSoftDeleteModel):
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.CASCADE, related_name='scores')
    score_date = models.DateField()
    progress_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    quality_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    hse_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    payment_compliance_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    cooperation_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    overall_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sub_scores')
    notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'subcontractor_performance_scores'

    SCORE_FIELDS = (
        'progress_score',
        'quality_score',
        'hse_score',
        'payment_compliance_score',
        'cooperation_score',
    )

    def compute_overall(self):
        if self.progress_score is None or self.hse_score is None:
            return None
        weights = [
            (self.progress_score, 0.3),
            (self.quality_score, 0.25),
            (self.hse_score, 0.25),
            (self.payment_compliance_score, 0.1),
            (self.cooperation_score, 0.1),
        ]
        weighted_sum = 0.0
        weight_total = 0.0
        for val, w in weights:
            if val is not None:
                weighted_sum += float(val) * w
                weight_total += w
        if weight_total == 0:
            return None
        return round(weighted_sum / weight_total, 2)

    def save(self, *args, **kwargs):
        self.overall_score = self.compute_overall()
        super().save(*args, **kwargs)


class WarningType(models.TextChoices):
    VERBAL = 'verbal', 'Verbal'
    WRITTEN = 'written', 'Written'
    FINAL = 'final', 'Final'
    CONTRACT_SUSPENSION = 'contract_suspension', 'Contract suspension'


class SubcontractorWarning(AuditSoftDeleteModel):
    subcontractor = models.ForeignKey(Subcontractor, on_delete=models.CASCADE, related_name='warnings')
    warning_date = models.DateField()
    warning_type = models.CharField(max_length=30, choices=WarningType.choices)
    reason = models.TextField()
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='sub_warnings')
    resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'subcontractor_warnings'
