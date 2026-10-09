"""Risk matrix helpers: probability × severity aggregation."""

from __future__ import annotations

from decimal import Decimal

from risk.models import EventType, RiskEvent, RiskStatus, Severity

PROBABILITY_BUCKETS = [
    ('0-20', Decimal('0'), Decimal('0.20')),
    ('21-40', Decimal('0.20'), Decimal('0.40')),
    ('41-60', Decimal('0.40'), Decimal('0.60')),
    ('61-80', Decimal('0.60'), Decimal('0.80')),
    ('81-100', Decimal('0.80'), Decimal('1.00')),
]

LEVEL_TO_BUCKET = {
    1: '0-20',
    2: '21-40',
    3: '41-60',
    4: '61-80',
    5: '81-100',
}

LEVEL_TO_SEVERITY = {
    1: Severity.LOW,
    2: Severity.MEDIUM,
    3: Severity.HIGH,
    4: Severity.CRITICAL,
    5: Severity.CRITICAL,
}

SEVERITY_ORDER = [
    Severity.LOW,
    Severity.MEDIUM,
    Severity.HIGH,
    Severity.CRITICAL,
]

CLOSED_STATUSES = {RiskStatus.CLOSED, 'resolved'}


def _probability_bucket(probability) -> str | None:
    if probability is None:
        return None
    value = Decimal(str(probability))
    for index, (label, low, high) in enumerate(PROBABILITY_BUCKETS):
        if index == 0:
            if Decimal('0') <= value <= high:
                return label
        elif low < value <= high:
            return label
    return None


def build_risk_matrix(project_id) -> dict:
    """Aggregate open risk events into probability × severity cells."""
    qs = (
        RiskEvent.objects.filter(project_id=project_id, event_type=EventType.RISK)
        .exclude(status__in=CLOSED_STATUSES)
    )
    cells: dict[tuple[str, str], int] = {}
    total_open = 0
    for event in qs.only(
        'probability',
        'severity',
        'status',
        'probability_level',
        'impact_severity_level',
    ):
        bucket = None
        severity = None
        if event.probability_level and event.impact_severity_level:
            bucket = LEVEL_TO_BUCKET.get(event.probability_level)
            severity = LEVEL_TO_SEVERITY.get(event.impact_severity_level)
        elif event.severity and event.probability is not None:
            bucket = _probability_bucket(event.probability)
            severity = event.severity
        if not bucket or not severity:
            continue
        key = (bucket, severity)
        cells[key] = cells.get(key, 0) + 1
        total_open += 1

    matrix = []
    for bucket, _, _ in PROBABILITY_BUCKETS:
        row = {'probability_bucket': bucket, 'cells': []}
        for severity in SEVERITY_ORDER:
            row['cells'].append(
                {
                    'severity': severity,
                    'count': cells.get((bucket, severity), 0),
                }
            )
        matrix.append(row)

    return {'total_open': total_open, 'matrix': matrix}
