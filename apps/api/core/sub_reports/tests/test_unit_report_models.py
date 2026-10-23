"""T012 — unit-report model/version constraints (feature 032, data-model §4)."""

import uuid

import pytest
from django.db import IntegrityError, transaction

from sub_reports.models import (
    DisciplineSubReport,
    SubReportStatus,
    UnitReportEventType,
    UnitReportStatusEvent,
)


def _report(project, user, **kwargs):
    defaults = {
        'project': project,
        'report_date': kwargs.pop('report_date', '2026-10-20'),
        'unit': 'buildings',
        'legacy_discipline': 'civil',
        'created_by': user,
    }
    defaults.update(kwargs)
    return DisciplineSubReport.objects.create(**defaults)


@pytest.mark.django_db
class TestUnitReportVersionConstraints:
    def test_lineage_version_number_is_unique(self, project, user):
        first = _report(project, user, lineage_id=uuid.uuid4(), version_number=1)
        with pytest.raises(IntegrityError), transaction.atomic():
            _report(
                project, user,
                lineage_id=first.lineage_id,
                version_number=1,
                unit='buildings',
            )

    def test_two_current_versions_for_same_key_rejected(self, project, user):
        """Unique current report on (project, report_date, unit) where is_current=true."""
        lineage = uuid.uuid4()
        _report(project, user, lineage_id=lineage, version_number=1, is_current=True)
        with pytest.raises(IntegrityError), transaction.atomic():
            _report(
                project, user,
                lineage_id=uuid.uuid4(),
                version_number=1,
                unit='buildings',
                is_current=True,
            )

    def test_historical_versions_allowed_for_same_key(self, project, user):
        lineage = uuid.uuid4()
        _report(project, user, lineage_id=lineage, version_number=1, is_current=False)
        _report(project, user, lineage_id=lineage, version_number=2, is_current=True)
        assert DisciplineSubReport.all_objects.filter(
            project=project, unit='buildings', is_deleted=False,
        ).count() == 2

    def test_supersedes_must_share_lineage_with_lower_version(self, project, user):
        lineage = uuid.uuid4()
        v1 = _report(project, user, lineage_id=lineage, version_number=1, is_current=False)
        v2 = _report(project, user, lineage_id=lineage, version_number=2, is_current=True, supersedes=v1)
        assert v2.supersedes_id == v1.id

    def test_legacy_discipline_evidence_preserved(self, project, user):
        r = _report(project, user, discipline='civil', legacy_discipline='civil', unit='buildings')
        r.refresh_from_db()
        assert r.legacy_discipline == 'civil'
        assert r.unit == 'buildings'


@pytest.mark.django_db
class TestUnitReportStatusEvent:
    def test_event_is_appended(self, project, user):
        report = _report(project, user)
        UnitReportStatusEvent.objects.create(
            report_version=report,
            from_status='',
            to_status=SubReportStatus.DRAFT,
            actor=user,
            occurred_at=report.created_at,
            event_type=UnitReportEventType.CREATED,
        )
        assert report.status_events.count() == 1

    def test_rejection_event_carries_reason(self, project, user):
        report = _report(project, user, status=SubReportStatus.REJECTED)
        event = UnitReportStatusEvent.objects.create(
            report_version=report,
            from_status=SubReportStatus.SUBMITTED,
            to_status=SubReportStatus.REJECTED,
            actor=user,
            occurred_at=report.updated_at,
            reason='اطلاعات ناقص است',
            event_type=UnitReportEventType.REJECTED,
        )
        assert event.reason
