from django.conf import settings
from django.db import models

from common.models import AuditSoftDeleteModel, TimeStampedModel, UUIDModel


METHOD_IDS = frozenset({'saw', 'topsis', 'ahp', 'dematel', 'ism'})
RANKING_METHODS = frozenset({'saw', 'topsis'})
CRITERIA_METHODS = frozenset({'ahp', 'dematel', 'ism'})


class DecisionCase(AuditSoftDeleteModel):
    """Project-scoped editable decision dossier (live inputs)."""

    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='decision_cases',
    )
    title = models.CharField(max_length=200)
    selected_methods = models.JSONField(default=list, blank=True)
    criteria = models.JSONField(default=list, blank=True)
    alternatives = models.JSONField(default=list, blank=True)
    weights = models.JSONField(default=list, blank=True)
    types = models.JSONField(default=list, blank=True)
    performance_matrix = models.JSONField(default=list, blank=True)
    ahp_matrix = models.JSONField(default=list, blank=True)
    dematel_matrix = models.JSONField(default=list, blank=True)
    ism_matrix = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'decision_cases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at'], name='decision_case_proj_created'),
        ]

    def __str__(self):
        return f'{self.title} ({self.project_id})'


class DecisionRun(UUIDModel, TimeStampedModel):
    """Immutable execution record for one method on one case."""

    case = models.ForeignKey(
        DecisionCase,
        on_delete=models.CASCADE,
        related_name='runs',
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='decision_runs',
    )
    method = models.CharField(max_length=32)
    input_snapshot = models.JSONField(default=dict)
    result = models.JSONField(default=dict)
    extracted_at = models.DateTimeField()
    extracted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='decision_runs',
    )

    class Meta:
        db_table = 'decision_runs'
        ordering = ['-extracted_at']
        indexes = [
            models.Index(fields=['case', '-extracted_at'], name='decision_run_case_extracted'),
            models.Index(fields=['project', '-extracted_at'], name='decision_run_proj_extracted'),
        ]

    def __str__(self):
        return f'{self.method} @ {self.extracted_at}'
