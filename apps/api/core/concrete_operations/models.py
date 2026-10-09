from django.core.validators import MinValueValidator
from django.db import models

from common.models import AuditSoftDeleteModel


class ConcreteBatch(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='concrete_batches')
    date = models.DateField()
    volume_m3 = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    cement_kg = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    sand_kg = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    aggregate_kg = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    water_l = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])
    plasticizer_l = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['-date', '-created_at']
        constraints = [models.CheckConstraint(check=models.Q(volume_m3__gt=0), name='batch_positive_volume')]


class ReadyMixDelivery(AuditSoftDeleteModel):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='ready_mix_deliveries')
    date = models.DateField()
    volume_m3 = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(0.001)])
    supplier = models.ForeignKey('resources.Supplier', on_delete=models.PROTECT, related_name='ready_mix_deliveries')
    ticket_number = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-date', '-created_at']
        constraints = [models.CheckConstraint(check=models.Q(volume_m3__gt=0), name='delivery_positive_volume')]
