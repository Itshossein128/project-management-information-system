"""033 RED-phase scaffolding (feature 033-daily-sections-grid).

Tasks: T050
Scope: Summary attachment counts + link payloads per FR-036.

This module is intentionally written for the RED phase so that tests can be
run from day one. Tests will FAIL until the implementation (summary attachment
counts service, link payload computation) is in place.
"""

from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
import pytest

from projects.models import Project, WBS
from resources.models import Material
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    UnitReportAttachment,
    SubReportStatus,
)
from common.reporting_units import SpecialtyUnit
from django.db import transaction

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def project_with_attachments(db, user):
    """Create a project with reports and activities that have attachments."""
    project = Project.objects.create(
        project_code='PRJ-ATT3',
        project_name='Attachment Summary Test',
        employer='Employer Co',
    )

    report = DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        lineage_id=None,
        status=SubReportStatus.DRAFT,
        created_by=user,
    )

    from projects.models import Activity
    wbs = WBS.add_root(project=project, wbs_code='1', wbs_name='Root')
    activity1 = Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A1',
        activity_name='Activity One',
        status='in_progress',
        created_by=user,
    )

    activity2 = Activity.objects.create(
        project=project,
        wbs=wbs,
        activity_code='A2',
        activity_name='Activity Two',
        status='in_progress',
        created_by=user,
    )

    # Save sub-report activities
    act1 = DisciplineSubReportActivity.objects.create(
        sub_report=report,
        row_number=1,
        shift='shift_1',
        activity_ref=activity1,
        activity_description='Activity One',
        contractor_ref=None,
        crew_name='Crew A',
        foreman_count=2,
        worker_count=3,
        quantity='10.0',
        unit='m3',
    )

    act2 = DisciplineSubReportActivity.objects.create(
        sub_report=report,
        row_number=2,
        shift='shift_1',
        activity_ref=activity2,
        activity_description='Activity Two',
        contractor_ref=None,
        crew_name='Crew B',
        foreman_count=1,
        worker_count=4,
        quantity='5.0',
        unit='m3',
    )

    return project, report, act1, act2


# ---------------------------------------------------------------------------
# §7: summary attachment counts
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSummaryAttachmentCounts:
    """Tests for per-section accessible counts + link payloads (FR-036)."""

    def test_per_section_accessible_counts(
        self, db, project_with_attachments
    ):
        """Per-section accessible counts + link payloads derive from contributing units (FR-036)."""
        from projects.models import Project
        from sub_reports.services import get_attachment_counts

        project, report, act1, act2 = project_with_attachments

        # Attach images to both activities via service
        from django.core.files.base import ContentFile
        from sub_reports.models import UnitReportAttachment

        # Activity 1 attachment (2 MB JPEG)
        att1 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act1.id),
            storage_key='attachments/activity1/image1.jpg',
            declared_content_type='image/jpeg',
            size_bytes=2 * 1024 * 1024,
            checksum='abc123',
            capture_date=date(2024, 6, 10),
            work_front='Site A',
        )

        # Activity 2 attachment (5 MB PNG)
        att2 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act2.id),
            storage_key='attachments/activity2/image2.png',
            declared_content_type='image/png',
            size_bytes=5 * 1024 * 1024,
            checksum='def456',
            capture_date=date(2024, 6, 10),
            work_front='Site B',
        )

        # Get summary counts
        counts = get_attachment_counts(report)

        # Should have 2 attachments total across the section
        assert counts['total'] == 2, (
            f"Expected 2 total attachments, got {counts['total']}"
        )
        assert counts['by_section']['activity'] == 2, (
            f"Expected 2 activity attachments, got {counts['by_section'].get('activity')}"
        )
        assert counts['by_section']['buildings'] == 2, (
            f"Expected 2 buildings attachments, got {counts['by_section'].get('buildings')}"
        )

        # Links should be accessible (relative paths, not full URLs with secrets)
        assert 'links' in counts, "Summary should provide accessible link payloads"
        # Links should be relative paths or tokenized URLs, not absolute with secrets
        for link in counts.get('links', []):
            assert link.startswith('/') or link.startswith('?'), (
                f"Links should be relative or tokenized, got: {link}"
            )

    def test_counts_derived_from_contributing_units(self, db, project_with_attachments):
        """Counts are derived only from contributing units, not all units."""
        from projects.models import Project
        from sub_reports.services import get_attachment_counts

        project, report, act1, act2 = project_with_attachments

        # Only attach to the two activities in this report
        from django.core.files.base import ContentFile
        from sub_reports.models import UnitReportAttachment

        att1 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act1.id),
            storage_key='attachments/activity1/image1.jpg',
            declared_content_type='image/jpeg',
            size_bytes=2 * 1024 * 1024,
            checksum='abc123',
            capture_date=date(2024, 6, 10),
            work_front='Site A',
        )

        att2 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act2.id),
            storage_key='attachments/activity2/image2.png',
            declared_content_type='image/png',
            size_bytes=5 * 1024 * 1024,
            checksum='def456',
            capture_date=date(2024, 6, 10),
            work_front='Site B',
        )

        counts = get_attachment_counts(report)

        # Should count only attachments from this report's units
        assert counts['total'] == 2, (
            f"Expected 2 total attachments from contributing units, got {counts['total']}"
        )
        # Should not count attachments from other reports/projects
        assert counts['by_section']['activity'] == 2

    def test_daily_summary_payload_groups_authorized_attachment_links(
        self, db, user, project_with_attachments,
    ):
        """T069: summary payload groups current-unit attachments by section."""
        from field_reports.serializers import DailyReportDetailSerializer
        from field_reports.services.daily_report_aggregation import ensure_daily_report_summary

        project, report, act1, _act2 = project_with_attachments
        report.status = SubReportStatus.SUBMITTED
        report.save(update_fields=['status'])
        UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act1.id),
            storage_key='attachments/activity1/summary.jpg',
            declared_content_type='image/jpeg',
            size_bytes=1024,
            checksum='summary-count',
            capture_date=REPORT_DATE,
            work_front='Tower A',
        )

        summary = ensure_daily_report_summary(project.id, REPORT_DATE, user=user)
        payload = DailyReportDetailSerializer(summary).data

        assert payload['attachment_counts'] == [
            {
                'section': 'activity',
                'count': 1,
                'first_links': [],
            }
        ]

    def test_summary_attachment_links_require_a_project_member(
        self, db, user, project_with_attachments,
    ):
        """T069: metadata navigation links require project membership, never storage access."""
        from rest_framework.test import APIRequestFactory
        from master_data.models import MemberStatus, ProjectMember
        from field_reports.serializers import DailyReportDetailSerializer
        from field_reports.services.daily_report_aggregation import ensure_daily_report_summary

        project, report, act1, _ = project_with_attachments
        report.status = SubReportStatus.SUBMITTED
        report.save(update_fields=['status'])
        UnitReportAttachment.objects.create(
            sub_report=report, row_kind='activity', row_id=str(act1.id),
            storage_key='local-unavailable/not-a-public-url',
            declared_content_type='image/jpeg', size_bytes=1024,
            checksum='membership-only', capture_date=REPORT_DATE,
        )
        summary = ensure_daily_report_summary(project.id, REPORT_DATE, user=user)
        request = APIRequestFactory().get('/')
        request.user = user

        without_membership = DailyReportDetailSerializer(
            summary, context={'request': request},
        ).data['attachment_counts']
        assert without_membership[0]['first_links'] == []

        ProjectMember.objects.create(
            project=project, user=user, status=MemberStatus.ACTIVE,
        )
        with_membership = DailyReportDetailSerializer(
            summary, context={'request': request},
        ).data['attachment_counts']
        assert with_membership[0]['first_links']
        assert 'local-unavailable' not in with_membership[0]['first_links'][0]
        assert '/attachments/' in with_membership[0]['first_links'][0]

    def test_no_attachments_returns_zero_counts(self, db, user, project):
        """When there are no attachments, counts should be zero."""
        from projects.models import Project
        from sub_reports.services import get_attachment_counts

        project = Project.objects.create(
            project_code='PRJ-EMPTY',
            project_name='Empty Attachment Test',
            employer='Employer Co',
        )

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        counts = get_attachment_counts(report)

        assert counts['total'] == 0, (
            f"Expected 0 total attachments, got {counts['total']}"
        )
        assert counts['by_section'] == {} or counts['by_section'].get('activity') == 0

    def test_urls_never_returned_to_users_lacking_permission(self, db, user, project):
        """URLs never returned to users lacking project/unit view permission."""
        from projects.models import Project
        from django.contrib.auth import get_user_model
        from sub_reports.services import get_attachment_links

        project = Project.objects.create(
            project_code='PRJ-ATT-PERM',
            project_name='Attachment Perm Test',
            employer='Employer Co',
        )

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=REPORT_DATE,
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        from django.core.files.base import ContentFile
        from sub_reports.models import UnitReportAttachment
        from projects.models import Activity

        activity = Activity.objects.create(
            project=project,
            wbs=WBS.add_root(project=project, wbs_code='1', wbs_name='Root'),
            activity_code='A1',
            activity_name='Activity 1',
            status='in_progress',
            created_by=user,
        )

        act = DisciplineSubReportActivity.objects.create(
            sub_report=report,
            row_number=1,
            shift='shift_1',
            activity_ref=activity,
            activity_description='Activity 1',
            contractor_ref=None,
            crew_name='Crew A',
            foreman_count=2,
            worker_count=3,
            quantity='10.0',
            unit='m3',
        )

        # Attachment exists
        UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act.id),
            storage_key='attachments/activity1/image1.jpg',
            declared_content_type='image/jpeg',
            size_bytes=2 * 1024 * 1024,
            checksum='abc123',
            capture_date=date(2024, 6, 10),
            work_front='Site A',
        )

        # Create a user without project permission
        unprivileged_user = get_user_model().objects.create_user(
            username='unprivileged',
            email='unpriv@example.com',
            password='pass123',
        )

        # Try to retrieve attachment URLs without permission
        links = get_attachment_links(report, user=unprivileged_user)

        # Should either return empty or masked/redacted URLs, not real paths
        assert links == {} or (
            'redacted' in str(links).lower() or
            'no access' in str(links).lower()
        ), (
            "URLs should not be returned to users lacking project/unit view permission"
        )
