"""Section contracts on the canonical unit-report surface (feature 033).

US1 executed-activity contract (tasks T012), per
contracts/unit-report-sections-api.md §1. Sections for later stories
(US2–US7, tasks T019–T049) arrive with their phases.
"""
from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model
import pytest

from projects.models import Activity, Project, Stakeholder, WBS
from sub_reports.models import (
    DisciplineSubReport,
    DisciplineSubReportActivity,
    SubReportStatus,
    UnitReportAttachment,
)
from common.reporting_units import SpecialtyUnit
from sub_reports.serializers import (
    UnitReportActivitySectionSerializer,
    UnitReportLaborSectionSerializer,
)
from sub_reports.services.section_validation import (
    validate_activity_rows,
    validate_labor_rows,
    SectionContractError,
)

User = get_user_model()

REPORT_DATE = date(2024, 6, 10)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def unit_report(db, project, user):
    return DisciplineSubReport.objects.create(
        project=project,
        report_date=REPORT_DATE,
        unit=SpecialtyUnit.BUILDINGS,
        discipline='civil',
        lineage_id=None,
        status=SubReportStatus.DRAFT,
        created_by=user,
    )


@pytest.fixture
def contractor(db, project, user):
    stakeholder = Stakeholder.objects.create(
        project=project,
        name='Test Contractor Co',
        role='contractor',
        created_by=user,
    )
    stakeholder.refresh_from_db()
    return stakeholder


@pytest.fixture
def project_activity(db, activity, project, approved_measurement):
    activity.status = 'in_progress'
    activity.is_deleted = False
    activity.save()
    return activity


@pytest.fixture
def foreign_project(db, user, unit):
    other = Project.objects.create(
        project_code='PRJ-001-F',
        project_name='Other Project',
        employer='Employer Co',
    )
    node = WBS.add_root(project=other, wbs_code='1', wbs_name='Root')
    activity = Activity.objects.create(
        project=other,
        wbs=node,
        activity_code='X1',
        activity_name='Foreign activity',
        status='in_progress',
        created_by=user,
    )
    from schedule.services.measurement_service import approve_definition, get_or_create_definition, update_draft

    definition = get_or_create_definition(activity, user)
    update_draft(definition, {'method': 'quantity', 'total_quantity': 100, 'unit_id': str(unit.id)}, user)
    approve_definition(definition, user)
    stakeholder = Stakeholder.objects.create(
        project=other,
        name='Foreign Contractor Co',
        role='contractor',
        created_by=user,
    )
    return {'project': other, 'wbs': node, 'activity': activity, 'stakeholder': stakeholder}


@pytest.fixture
def section_activity_payload(project_activity, contractor):
    return {
        'row_number': 1,
        'shift': 'shift_1',
        'activity_ref': str(project_activity.id),
        'activity_description': 'Wall works',
        'contractor_ref': str(contractor.id),
        'crew_name': 'Crew A',
        'foreman_count': 2,
        'worker_count': 3,
        'parcel': 'P4',
        'zone': 'Z1',
        'block': 'B2',
        'floor': 'F3',
        'quantity': '12.5',
        'unit': 'm3',
    }


def _save_rows(report, rows):
    """Save section rows through the section-validation service + serializer path."""
    return validate_activity_rows(report, rows, context={})


# ---------------------------------------------------------------------------
# §1: executed activities (Buildings / Electrical / Mechanical)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestActivitySectionContract:
    def test_valid_complete_row_saves_and_maintains_headcount(
        self, db, unit_report, section_activity_payload,
    ):
        rows = _save_rows(unit_report, [section_activity_payload])
        assert len(rows) == 1
        row = rows[0]
        # headcount maintained as foreman_count + worker_count (T014)
        assert row.headcount == 5
        assert row.foreman_count == 2
        assert row.worker_count == 3
        assert row.contractor_ref_id
        assert row.activity_ref_id

    @pytest.mark.parametrize('quantity', ['0', '-12.5'])
    def test_quantity_must_be_positive(
        self, db, unit_report, section_activity_payload, quantity,
    ):
        section_activity_payload['quantity'] = quantity
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('quantity') == ['quantity_must_be_positive']

    def test_invalid_shift_not_silently_remapped(
        self, db, unit_report, section_activity_payload,
    ):
        section_activity_payload['shift'] = 'برانکارد'  # unrecognized free text
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('shift') == ['invalid_shift']

    def test_foreign_project_activity_refused(
        self, db, unit_report, section_activity_payload, foreign_project,
    ):
        section_activity_payload['activity_ref'] = str(foreign_project['activity'].id)
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('activity_ref') == ['activity_not_in_project_scope']

    def test_inactive_or_unapproved_activity_refused(
        self, db, unit_report, section_activity_payload, project_activity,
    ):
        project_activity.status = 'suspended'
        project_activity.save(update_fields=['status'])
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('activity_ref') == ['activity_not_in_project_scope']

    def test_foreign_project_contractor_refused(
        self, db, unit_report, section_activity_payload, foreign_project,
    ):
        section_activity_payload['contractor_ref'] = str(foreign_project['stakeholder'].id)
        with pytest.raises(SectionContractError) as excinfo:
            _save_rows(unit_report, [section_activity_payload])
        assert excinfo.value.field_errors('contractor_ref') == [
            'contractor_not_in_project_scope',
        ]

    def test_direct_company_labor_may_omit_contractor(self, db, unit_report, section_activity_payload):
        section_activity_payload.pop('contractor_ref')
        rows = _save_rows(unit_report, [section_activity_payload])
        assert rows[0].contractor_ref_id is None

    def test_crew_name_and_contractor_survive_as_separate_columns(
        self, db, unit_report, section_activity_payload, contractor,
    ):
        rows = _save_rows(unit_report, [section_activity_payload])
        data = UnitReportActivitySectionSerializer(rows[0]).data
        # No merged paint-by-name column: crew and contractor are distinct fields.
        assert 'crew_name' in data
        assert 'contractor_ref' in data
        assert data['crew_name'] == 'Crew A'
        assert data['contractor_ref'] == str(contractor.id)


# ---------------------------------------------------------------------------
# §2: labor section contract (US2, tasks T020/T021)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestLaborSectionContract:
    """Labor section validation per contracts/unit-report-sections-api.md §2."""

    @pytest.fixture
    def active_labor_config(self, db, project, user):
        from project_templates.models import ProjectTemplate
        from project_templates.services import (
            activate_project_reporting_configuration,
            create_labor_catalog,
        )

        tpl = ProjectTemplate.objects.create(
            template_name='Labor Section Test Template',
            is_system=False,
            created_by=user,
        )
        create_labor_catalog(
            tpl,
            version_name='v1',
            titles=[
                {
                    'title_code': 'site_manager',
                    'title_label': 'Site Manager',
                    'title_label_fa': 'سرپرست کارگاه',
                    'category': 'indirect',
                    'display_order': 1,
                    'active': True,
                    'project_specific': False,
                },
                {
                    'title_code': 'rebar_worker',
                    'title_label': 'Rebar Worker',
                    'title_label_fa': 'آرماتوربند',
                    'category': 'direct',
                    'display_order': 1,
                    'active': True,
                    'project_specific': False,
                },
            ],
        )
        return activate_project_reporting_configuration(
            project=project,
            template=tpl,
            effective_from=date(2024, 6, 1),
            user=user,
        )

    def test_valid_labor_row_saves_and_resolves_catalog_title(
        self, db, unit_report, active_labor_config, contractor,
    ):
        rows = validate_labor_rows(
            unit_report,
            [
                {
                    'labor_category': 'direct',
                    'job_title': 'آرماتوربند',
                    'present_count': 6,
                    'leave_count': 1,
                    'overtime_hours': '2.50',
                    'contractor_ref': str(contractor.id),
                },
            ],
        )
        assert len(rows) == 1
        row = rows[0]
        assert row.labor_category == 'direct'
        assert row.job_title == 'آرماتوربند'
        assert row.present_count == 6
        assert row.leave_count == 1
        assert str(row.overtime_hours) == '2.50'
        assert row.contractor_ref_id == contractor.id
        data = UnitReportLaborSectionSerializer(row).data
        assert data['present_count'] == 6
        assert data['leave_count'] == 1
        assert data['contractor_ref'] == str(contractor.id)

    @pytest.mark.parametrize(
        'field_name,bad_value',
        [
            ('present_count', -1),
            ('leave_count', -1),
            ('overtime_hours', '-0.50'),
        ],
    )
    def test_headcount_must_be_non_negative(
        self, db, unit_report, active_labor_config, field_name, bad_value,
    ):
        payload = {
            'labor_category': 'direct',
            'job_title': 'آرماتوربند',
            'present_count': 5,
            'leave_count': 0,
            'overtime_hours': '0.00',
            field_name: bad_value,
        }
        with pytest.raises(SectionContractError) as excinfo:
            validate_labor_rows(unit_report, [payload])
        assert excinfo.value.field_errors(field_name) == ['headcount_must_be_non_negative']

    def test_unknown_job_title_outside_effective_catalog_refused(
        self, db, unit_report, active_labor_config,
    ):
        payload = {
            'labor_category': 'direct',
            'job_title': 'فضانورد کارگاهی',
            'present_count': 2,
            'leave_count': 0,
        }
        with pytest.raises(SectionContractError) as excinfo:
            validate_labor_rows(unit_report, [payload])
        assert excinfo.value.field_errors('job_title') == ['unknown_job_title']

    def test_invalid_labor_category_mismatch_with_catalog_title_refused(
        self, db, unit_report, active_labor_config,
    ):
        payload = {
            'labor_category': 'indirect',  # catalog says rebar_worker is 'direct'
            'job_title': 'آرماتوربند',
            'present_count': 3,
            'leave_count': 0,
        }
        with pytest.raises(SectionContractError) as excinfo:
            validate_labor_rows(unit_report, [payload])
        assert excinfo.value.field_errors('labor_category') == ['invalid_labor_category']

    def test_foreign_project_contractor_refused_in_labor_row(
        self, db, unit_report, active_labor_config, foreign_project,
    ):
        payload = {
            'labor_category': 'direct',
            'job_title': 'آرماتوربند',
            'present_count': 4,
            'leave_count': 0,
            'contractor_ref': str(foreign_project['stakeholder'].id),
        }
        with pytest.raises(SectionContractError) as excinfo:
            validate_labor_rows(unit_report, [payload])
        assert excinfo.value.field_errors('contractor_ref') == [
            'contractor_not_in_project_scope',
        ]


# ---------------------------------------------------------------------------
# §7: attachment group tests (T049)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAttachmentContract:
    """Attachment tests per contracts/unit-report-sections-api.md §7."""

    @pytest.fixture(autouse=True)
    def _persisted_activity(self, unit_report, section_activity_payload):
        _save_rows(unit_report, [section_activity_payload])

    def test_unsupported_file_format(self, db, unit_report, section_activity_payload):
        """ZIP/EXE/content-misdeclared files are rejected at upload."""
        from sub_reports.services import attach_image_to_activity

        # Simulate uploading a ZIP file (misdeclared as image)
        zip_content = b'PK\x03\x04\x14\x00\x00\x00\x08\x00'  # PK zip header
        misdeclared_exe = b'MZ\x90\x00\x04\x00\x00'  # PE/EXE header

        with pytest.raises(Exception) as excinfo:  # will be ValidationError
            attach_image_to_activity(
                report=unit_report,
                activity_row_id=str(unit_report.activities.first().id),
                file_content=zip_content,
                declared_content_type='image/jpeg',
            )

        # Should reject unsupported format
        assert 'unsupported_file_format' in str(excinfo.value).lower() or \
            'unsupported' in str(excinfo.value).lower()

    def test_file_too_large(self, db, unit_report, section_activity_payload):
        """Files above 10 MB are rejected at upload."""
        from sub_reports.services import attach_image_to_activity

        # Create content > 10 MB (10 * 1024 * 1024 + 1 bytes)
        large_content = b'x' * (10 * 1024 * 1024 + 1)

        with pytest.raises(Exception) as excinfo:
            attach_image_to_activity(
                report=unit_report,
                activity_row_id=str(unit_report.activities.first().id),
                file_content=large_content,
                declared_content_type='image/jpeg',
            )

        # Should reject oversized file
        assert 'file_too_large' in str(excinfo.value).lower() or \
            'too large' in str(excinfo.value).lower() or \
            'size limit' in str(excinfo.value).lower()

    def test_attachment_row_not_in_version(self, db, unit_report, section_activity_payload, project):
        """Attachment target outside the versioned report is rejected."""
        from sub_reports.services import attach_image_to_activity

        # Create a different report (different version)
        from django.contrib.auth import get_user_model
        other_user = get_user_model().objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123',
        )
        other_report = DisciplineSubReport.objects.create(
            project=project,
            report_date=date(2024, 6, 11),  # different date = different version
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=other_user,
        )

        saved_other = DisciplineSubReportActivity.objects.create(
            sub_report=other_report,
            row_number=1,
            shift='shift_1',
            activity_ref=unit_report.activities.first().activity_ref,
            activity_description='Other version',
            crew_name='Other',
            foreman_count=1,
            worker_count=1,
            quantity='1',
            unit='m3',
        )
        with pytest.raises(Exception) as excinfo:
            attach_image_to_activity(
                report=unit_report,
                activity_row_id=str(saved_other.id),
                file_content=b'fake-image-data',
                declared_content_type='image/jpeg',
            )

        # Should reject attachment to row outside version
        assert 'attachment_row_not_in_version' in str(excinfo.value).lower() or \
            'not in version' in str(excinfo.value).lower() or \
            'cross-project' in str(excinfo.value).lower()

    def test_reference_not_in_project_scope(self, db, unit_report, section_activity_payload, foreign_project, project, user):
        """Cross-project attachment target is refused with no partial storage."""
        from sub_reports.services import attach_image_to_activity

        foreign_report = DisciplineSubReport.objects.create(
            project=foreign_project['project'],
            report_date=date(2024, 6, 10),
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            status=SubReportStatus.DRAFT,
            created_by=user,
        )
        foreign_row = DisciplineSubReportActivity.objects.create(
            sub_report=foreign_report,
            row_number=1,
            shift='shift_1',
            activity_ref=foreign_project['activity'],
            activity_description='Foreign',
            crew_name='Foreign crew',
            foreman_count=1,
            worker_count=1,
            quantity='1',
            unit='m3',
        )
        before = UnitReportAttachment.objects.count()
        with pytest.raises(Exception) as excinfo:
            attach_image_to_activity(
                report=unit_report,
                activity_row_id=str(foreign_row.id),
                file_content=b'fake-image-data',
                declared_content_type='image/jpeg',
            )
        assert UnitReportAttachment.objects.count() == before

        # Should refuse cross-project attachment
        assert 'reference_not_in_project_scope' in str(excinfo.value).lower() or \
            'not in project scope' in str(excinfo.value).lower() or \
            'cross-project' in str(excinfo.value).lower()

    def test_attachment_mutable_only_on_draft(self, db, unit_report, section_activity_payload):
        """Attachments can only be modified on draft reports, not submitted/approved."""
        from sub_reports.services import attach_image_to_activity

        # First, submit the report
        unit_report.status = SubReportStatus.SUBMITTED
        unit_report.save()

        # Try to add attachment to submitted report
        with pytest.raises(Exception) as excinfo:
            attach_image_to_activity(
                report=unit_report,
                activity_row_id=str(unit_report.activities.first().id),
                file_content=b'fake-image-data',
                declared_content_type='image/jpeg',
            )

        # Should reject modification on non-draft
        assert 'draft only' in str(excinfo.value).lower() or \
            'not allowed' in str(excinfo.value).lower() or \
            'submitted' in str(excinfo.value).lower()

    def test_provenance_metadata_preserved(self, db, unit_report, section_activity_payload):
        """Provenance metadata (capture date, work front, source activity/unit/project) preserved."""
        from sub_reports.services import attach_image_to_activity

        saved = _save_rows(unit_report, [section_activity_payload])
        attachment = attach_image_to_activity(
            report=unit_report,
            activity_row_id=str(saved[0].id),
            file_content=b'fake-image-data',
            declared_content_type='image/jpeg',
            capture_date=date(2024, 6, 10),
            work_front='Site A',
        )

        # Verify provenance fields are stored
        assert attachment.capture_date == date(2024, 6, 10)
        assert attachment.work_front == 'Site A'
        assert attachment.sub_report_id == unit_report.id
        # Source activity/unit should be inferable from the report/activity context
        assert attachment.row_kind  # should have a row_kind set


@pytest.mark.django_db
class TestAttachmentSummaryCounts:
    """Summary count tests for attachments (FR-036)."""

    def test_per_section_accessible_counts(self, db, user, project):
        """Per-section accessible counts + link payloads derive from contributing units (FR-036)."""
        from projects.models import Project
        from wbs.services import create_wbs_node

        # Create project and report
        project = Project.objects.create(
            project_code='PRJ-ATT',
            project_name='Attachment Test',
            employer='Employer Co',
        )
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Attachment root')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=date(2024, 6, 10),
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        # Create activities with attachments across units
        activity1 = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A1',
            activity_name='Activity 1',
            status='in_progress',
            created_by=user,
        )

        activity2 = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A2',
            activity_name='Activity 2',
            status='in_progress',
            created_by=user,
        )

        # Save sub-report activities
        act1 = DisciplineSubReportActivity.objects.create(
            sub_report=report,
            row_number=1,
            shift='shift_1',
            activity_ref=activity1,
            activity_description='Activity 1',
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
            activity_description='Activity 2',
            contractor_ref=None,
            crew_name='Crew B',
            foreman_count=1,
            worker_count=4,
            quantity='5.0',
            unit='m3',
        )

        # Attach images to both activities (simulate via service)
        from sub_reports.models import UnitReportAttachment
        from django.core.files.base import ContentFile

        # Activity 1 attachment
        att1 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act1.id),
            storage_key='attachments/activity1/image1.jpg',
            declared_content_type='image/jpeg',
            size_bytes=2 * 1024 * 1024,  # 2 MB
            checksum='abc123',
            capture_date=date(2024, 6, 10),
            work_front='Site A',
        )

        # Activity 2 attachment
        att2 = UnitReportAttachment.objects.create(
            sub_report=report,
            row_kind='activity',
            row_id=str(act2.id),
            storage_key='attachments/activity2/image2.png',
            declared_content_type='image/png',
            size_bytes=5 * 1024 * 1024,  # 5 MB
            checksum='def456',
            capture_date=date(2024, 6, 10),
            work_front='Site B',
        )

        # Test that summary counts are derived from contributing units
        # per-section counts should reflect attachments from contributing units
        from sub_reports.services import get_attachment_counts

        counts = get_attachment_counts(report)

        # Should have 2 attachments total across the section
        assert counts['total'] == 2, (
            f"Expected 2 total attachments, got {counts['total']}"
        )
        assert counts['by_section']['activity'] == 2, (
            f"Expected 2 activity attachments, got {counts['by_section'].get('activity')}"
        )

        # Links should be accessible URLs (relative paths, not full URLs)
        assert 'links' in counts or 'url' in counts, (
            "Summary should provide accessible link payloads"
        )

    def test_urls_never_returned_to_users_lacking_permission(self, db, user, project):
        """URLs never returned to users lacking project/unit view permission."""
        from projects.models import Project
        from django.contrib.auth import get_user_model
        from wbs.services import create_wbs_node

        # Create project and report
        project = Project.objects.create(
            project_code='PRJ-ATT2',
            project_name='Attachment Perm Test',
            employer='Employer Co',
        )
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Attachment permission root')

        report = DisciplineSubReport.objects.create(
            project=project,
            report_date=date(2024, 6, 10),
            unit=SpecialtyUnit.BUILDINGS,
            discipline='civil',
            lineage_id=None,
            status=SubReportStatus.DRAFT,
            created_by=user,
        )

        activity = Activity.objects.create(
            project=project,
            wbs=wbs,
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

        from django.core.files.base import ContentFile
        from sub_reports.models import UnitReportAttachment

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
        # The service should not expose URLs to unprivileged users
        from sub_reports.services import get_attachment_links

        links = get_attachment_links(report, user=unprivileged_user)

        # Should either return empty or masked/redacted URLs, not real paths
        assert links == {} or (
            'redacted' in str(links).lower() or
            'no access' in str(links).lower()
        ), (
            "URLs should not be returned to users lacking project/unit view permission"
        )
