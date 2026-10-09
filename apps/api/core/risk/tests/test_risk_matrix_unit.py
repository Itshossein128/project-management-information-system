"""Unit tests for risk matrix bucketing logic."""

from datetime import date
from decimal import Decimal

import pytest

from risk.models import EventType, RiskEvent, RiskStatus, Severity
from risk.services.matrix_service import PROBABILITY_BUCKETS, _probability_bucket, build_risk_matrix


@pytest.mark.parametrize(
    'probability,expected',
    [
        (Decimal('0.20'), '0-20'),
        (Decimal('0.35'), '21-40'),
        (Decimal('0.50'), '41-60'),
        (Decimal('0.75'), '61-80'),
        (Decimal('1.00'), '81-100'),
        (Decimal('0.90'), '81-100'),
    ],
)
def test_probability_bucket(probability, expected):
    assert _probability_bucket(probability) == expected


@pytest.mark.django_db
def test_build_risk_matrix_counts_and_excludes(project, user):
    """Matrix includes open risks only (not barriers/claims/issues/closed)."""
    RiskEvent.objects.create(
        project=project,
        event_type=EventType.RISK,
        description='Open risk',
        probability=Decimal('0.50'),
        severity=Severity.MEDIUM,
        status=RiskStatus.OPEN,
        event_date=date.today(),
        created_by=user,
        updated_by=user,
    )
    RiskEvent.objects.create(
        project=project,
        event_type=EventType.RISK,
        description='Critical open risk',
        probability=Decimal('0.90'),
        severity=Severity.CRITICAL,
        status=RiskStatus.UNDER_REVIEW,
        event_date=date.today(),
        created_by=user,
        updated_by=user,
    )
    RiskEvent.objects.create(
        project=project,
        event_type=EventType.RISK,
        description='Level-based risk',
        probability_level=4,
        impact_severity_level=3,
        status=RiskStatus.MITIGATED,
        event_date=date.today(),
        created_by=user,
        updated_by=user,
    )
    RiskEvent.objects.create(
        project=project,
        event_type=EventType.BARRIER,
        description='Barrier ignored',
        probability=Decimal('0.90'),
        severity=Severity.CRITICAL,
        status=RiskStatus.OPEN,
        event_date=date.today(),
        created_by=user,
        updated_by=user,
    )
    RiskEvent.objects.create(
        project=project,
        event_type=EventType.RISK,
        description='Closed risk',
        probability=Decimal('0.50'),
        severity=Severity.MEDIUM,
        status=RiskStatus.CLOSED,
        event_date=date.today(),
        resolved_date=date.today(),
        created_by=user,
        updated_by=user,
    )

    result = build_risk_matrix(project.id)
    assert result['total_open'] == 3
    assert len(result['matrix']) == len(PROBABILITY_BUCKETS)
    medium_cell = next(
        c
        for row in result['matrix']
        if row['probability_bucket'] == '41-60'
        for c in row['cells']
        if c['severity'] == Severity.MEDIUM
    )
    assert medium_cell['count'] == 1
