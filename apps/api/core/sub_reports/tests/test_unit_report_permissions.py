"""T024 & T025 — unit-report permission matrix and Segregation of Duties (feature 032, US2; quickstart §4)."""

import uuid
from datetime import date
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from django.utils import timezone
from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride
from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from sub_reports.models import (
    DisciplineSubReport,
    SubReportStatus,
    UnitReportEventType,
    UnitReportStatusEvent,
)

User = get_user_model()
BASE = '/api/v1/projects/{project_id}/units/{unit}/daily-reports/'


def make_user(username: str, mobile: str, is_superuser: bool = False):
    if is_superuser:
        return User.objects.create(
            username=username,
            mobile=mobile,
            full_name=f'Super {username}',
            is_superuser=True,
            is_staff=True,
        )
    return User.objects.create(
        username=username,
        mobile=mobile,
        full_name=f'User {username}',
    )


def make_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def make_member(project, user, permissions: list[str] | None = None):
    member = ProjectMember.objects.create(
        project=project,
        user=user,
        status=MemberStatus.ACTIVE,
    )
    if permissions:
        for codename in permissions:
            ProjectMemberPermissionOverride.objects.create(
                member=member,
                permission_codename=codename,
                is_granted=True,
            )
    return member


@pytest.fixture
def viewer_user(db, project):
    u = make_user('view_only_user', '+989121110001')
    make_member(project, u, permissions=['view_reports'])
    return u


@pytest.fixture
def editor_user(db, project):
    u = make_user('editor_user', '+989121110002')
    make_member(project, u, permissions=['view_reports', 'edit_reports'])
    return u


@pytest.fixture
def approver_user(db, project):
    u = make_user('approver_user', '+989121110003')
    make_member(project, u, permissions=['view_reports', 'approve_reports'])
    return u


@pytest.fixture
def full_user(db, project):
    u = make_user('full_user', '+989121110004')
    make_member(project, u, permissions=['view_reports', 'edit_reports', 'approve_reports'])
    return u


@pytest.fixture
def non_member_user(db):
    return make_user('non_member_user', '+989121110005')


@pytest.fixture
def admin_superuser(db):
    return make_user('admin_superuser', '+989121110006', is_superuser=True)


@pytest.fixture
def other_project(db, non_member_user):
    p = create_project_with_creator(
        creator=non_member_user,
        project_code='PRJ-099',
        project_name='Other Project',
        employer='Other Employer',
        start_date='2024-01-01',
    )
    p.status = ProjectStatus.ACTIVE
    p.save(update_fields=['status'])
    return p


@pytest.fixture
def existing_draft_report(db, project, editor_user):
    return DisciplineSubReport.objects.create(
        project=project,
        unit='buildings',
        discipline='civil',
        report_date=date(2026, 10, 20),
        lineage_id=uuid.uuid4(),
        version_number=1,
        is_current=True,
        status=SubReportStatus.DRAFT,
        created_by=editor_user,
        updated_by=editor_user,
    )


@pytest.fixture
def existing_submitted_report(db, project, editor_user):
    report = DisciplineSubReport.objects.create(
        project=project,
        unit='buildings',
        discipline='civil',
        report_date=date(2026, 10, 21),
        lineage_id=uuid.uuid4(),
        version_number=1,
        is_current=True,
        status=SubReportStatus.SUBMITTED,
        created_by=editor_user,
        submitted_by=editor_user,
        updated_by=editor_user,
    )
    UnitReportStatusEvent.objects.create(
        report_version=report,
        event_type=UnitReportEventType.SUBMITTED,
        from_status=SubReportStatus.DRAFT,
        to_status=SubReportStatus.SUBMITTED,
        actor=editor_user,
        occurred_at=timezone.now(),
    )
    return report


@pytest.mark.django_db
class TestPermissionMatrix:
    """T024: view_reports for reads, edit_reports for writes, approve_reports for review."""

    def test_view_reports_can_read(self, viewer_user, project, existing_draft_report):
        client = make_client(viewer_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res_current = client.get(f'{base}current/', {'date': '2026-10-20'})
        assert res_current.status_code == status.HTTP_200_OK
        assert res_current.data['id'] == str(existing_draft_report.id)

        res_detail = client.get(f'{base}{existing_draft_report.id}/')
        assert res_detail.status_code == status.HTTP_200_OK
        assert res_detail.data['id'] == str(existing_draft_report.id)

        res_history = client.get(f'{base}{existing_draft_report.id}/history/')
        assert res_history.status_code == status.HTTP_200_OK
        assert res_history.data['lineage_id'] == str(existing_draft_report.lineage_id)

    def test_view_reports_cannot_mutate(self, viewer_user, project, existing_draft_report):
        client = make_client(viewer_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        # Cannot open/create
        res_open = client.post(f'{base}open/', {'report_date': '2026-10-25'}, format='json')
        assert res_open.status_code == status.HTTP_403_FORBIDDEN

        # Cannot edit
        res_edit = client.patch(f'{base}{existing_draft_report.id}/', {'form_code': 'HACK'}, format='json')
        assert res_edit.status_code == status.HTTP_403_FORBIDDEN

        # Cannot submit
        res_submit = client.post(f'{base}{existing_draft_report.id}/submit/')
        assert res_submit.status_code == status.HTTP_403_FORBIDDEN

        # Cannot delete
        res_delete = client.delete(f'{base}{existing_draft_report.id}/')
        assert res_delete.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_reports_can_open_edit_submit_delete(self, editor_user, project):
        client = make_client(editor_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res_open = client.post(f'{base}open/', {'report_date': '2026-10-22'}, format='json')
        assert res_open.status_code == status.HTTP_201_CREATED
        rid = res_open.data['id']

        res_edit = client.patch(f'{base}{rid}/', {'form_code': 'B-101'}, format='json')
        assert res_edit.status_code == status.HTTP_200_OK

        res_submit = client.post(f'{base}{rid}/submit/')
        assert res_submit.status_code == status.HTTP_200_OK
        assert res_submit.data['status'] == SubReportStatus.SUBMITTED

    def test_edit_reports_cannot_approve_or_reject(self, editor_user, project, existing_submitted_report):
        client = make_client(editor_user)
        base = BASE.format(project_id=project.id, unit='buildings')
        rid = existing_submitted_report.id

        res_approve = client.post(f'{base}{rid}/approve/')
        assert res_approve.status_code == status.HTTP_403_FORBIDDEN

        res_reject = client.post(f'{base}{rid}/reject/', {'rejection_reason': 'Reason'}, format='json')
        assert res_reject.status_code == status.HTTP_403_FORBIDDEN

    def test_approve_reports_can_review_but_cannot_mutate_draft(
        self, approver_user, project, existing_submitted_report, existing_draft_report,
    ):
        client = make_client(approver_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        # Cannot open draft
        res_open = client.post(f'{base}open/', {'report_date': '2026-10-28'}, format='json')
        assert res_open.status_code == status.HTTP_403_FORBIDDEN

        # Cannot patch draft
        res_patch = client.patch(f'{base}{existing_draft_report.id}/', {'form_code': 'B-200'}, format='json')
        assert res_patch.status_code == status.HTTP_403_FORBIDDEN

        # Cannot submit draft
        res_submit = client.post(f'{base}{existing_draft_report.id}/submit/')
        assert res_submit.status_code == status.HTTP_403_FORBIDDEN

        # Can approve submitted report
        res_approve = client.post(f'{base}{existing_submitted_report.id}/approve/')
        assert res_approve.status_code == status.HTTP_200_OK
        assert res_approve.data['status'] == SubReportStatus.APPROVED

    def test_non_member_denied_without_disclosure(self, non_member_user, project, existing_draft_report):
        client = make_client(non_member_user)
        base = BASE.format(project_id=project.id, unit='buildings')
        rid = existing_draft_report.id

        assert client.get(f'{base}current/?date=2026-10-20').status_code == status.HTTP_403_FORBIDDEN
        assert client.post(f'{base}open/', {'report_date': '2026-10-20'}, format='json').status_code == status.HTTP_403_FORBIDDEN
        assert client.get(f'{base}{rid}/').status_code == status.HTTP_403_FORBIDDEN
        assert client.patch(f'{base}{rid}/', {'form_code': 'X'}, format='json').status_code == status.HTTP_403_FORBIDDEN
        assert client.delete(f'{base}{rid}/').status_code == status.HTTP_403_FORBIDDEN
        assert client.get(f'{base}{rid}/history/').status_code == status.HTTP_403_FORBIDDEN
        assert client.post(f'{base}{rid}/submit/').status_code == status.HTTP_403_FORBIDDEN
        assert client.post(f'{base}{rid}/approve/').status_code == status.HTTP_403_FORBIDDEN
        assert client.post(f'{base}{rid}/reject/', {'rejection_reason': 'R'}, format='json').status_code == status.HTTP_403_FORBIDDEN

    def test_cross_project_report_access_returns_404(
        self, full_user, project, other_project, non_member_user,
    ):
        """Report in other project cannot be accessed via current project URL."""
        client = make_client(full_user)
        other_report = DisciplineSubReport.objects.create(
            project=other_project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.DRAFT,
            created_by=non_member_user,
            updated_by=non_member_user,
        )
        base = BASE.format(project_id=project.id, unit='buildings')
        rid = other_report.id

        # GET detail returns 404 unit_report_not_found
        res_get = client.get(f'{base}{rid}/')
        assert res_get.status_code == status.HTTP_404_NOT_FOUND
        assert res_get.data['error']['code'] == 'unit_report_not_found'

        # PATCH returns 404 unit_report_not_found
        res_patch = client.patch(f'{base}{rid}/', {'form_code': 'HACK'}, format='json')
        assert res_patch.status_code == status.HTTP_404_NOT_FOUND
        assert res_patch.data['error']['code'] == 'unit_report_not_found'

        # History returns 404 unit_report_not_found
        res_hist = client.get(f'{base}{rid}/history/')
        assert res_hist.status_code == status.HTTP_404_NOT_FOUND
        assert res_hist.data['error']['code'] == 'unit_report_not_found'

    def test_wrong_unit_report_access_returns_404(self, full_user, project, existing_draft_report):
        """Report for 'buildings' accessed through 'electrical' URL returns 404 unit_report_not_found."""
        client = make_client(full_user)
        elec_base = BASE.format(project_id=project.id, unit='electrical')
        rid = existing_draft_report.id

        res_get = client.get(f'{elec_base}{rid}/')
        assert res_get.status_code == status.HTTP_404_NOT_FOUND
        assert res_get.data['error']['code'] == 'unit_report_not_found'

        res_patch = client.patch(f'{elec_base}{rid}/', {'form_code': 'HACK'}, format='json')
        assert res_patch.status_code == status.HTTP_404_NOT_FOUND
        assert res_patch.data['error']['code'] == 'unit_report_not_found'

        res_hist = client.get(f'{elec_base}{rid}/history/')
        assert res_hist.status_code == status.HTTP_404_NOT_FOUND
        assert res_hist.data['error']['code'] == 'unit_report_not_found'

    def test_foreign_key_injection_does_not_modify_project_or_unit(
        self, full_user, project, other_project, existing_draft_report,
    ):
        client = make_client(full_user)
        base = BASE.format(project_id=project.id, unit='buildings')
        rid = existing_draft_report.id

        res = client.patch(
            f'{base}{rid}/',
            {
                'project_id': str(other_project.id),
                'unit': 'electrical',
                'lineage_id': str(uuid.uuid4()),
                'version_number': 99,
                'form_code': 'VALID-CODE',
            },
            format='json',
        )
        assert res.status_code == status.HTTP_200_OK
        existing_draft_report.refresh_from_db()
        assert existing_draft_report.project_id == project.id
        assert existing_draft_report.unit == 'buildings'
        assert existing_draft_report.version_number == 1
        assert existing_draft_report.form_code == 'VALID-CODE'


@pytest.mark.django_db
class TestSegregationOfDuties:
    """T025: Preparer or Submitter cannot approve the same report; superuser break-glass allows."""

    def test_preparer_cannot_approve_own_report(self, full_user, approver_user, project):
        """User who created the report cannot approve it even if someone else submitted it."""
        report = DisciplineSubReport.objects.create(
            project=project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.SUBMITTED,
            created_by=full_user,
            submitted_by=approver_user,
            updated_by=approver_user,
        )
        client = make_client(full_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res = client.post(f'{base}{report.id}/approve/')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.data['error']['code'] == 'sod_self_approve'

        report.refresh_from_db()
        assert report.status == SubReportStatus.SUBMITTED
        assert report.approved_by is None
        assert report.approved_at is None

    def test_submitter_cannot_approve_own_report(self, full_user, editor_user, project):
        """User who submitted the report cannot approve it even if someone else prepared it."""
        report = DisciplineSubReport.objects.create(
            project=project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.SUBMITTED,
            created_by=editor_user,
            submitted_by=full_user,
            updated_by=full_user,
        )
        client = make_client(full_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res = client.post(f'{base}{report.id}/approve/')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.data['error']['code'] == 'sod_self_approve'

        report.refresh_from_db()
        assert report.status == SubReportStatus.SUBMITTED
        assert report.approved_by is None
        assert report.approved_at is None

    def test_preparer_and_submitter_cannot_approve(self, full_user, project):
        """User who both created and submitted the report cannot approve it."""
        report = DisciplineSubReport.objects.create(
            project=project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.SUBMITTED,
            created_by=full_user,
            submitted_by=full_user,
            updated_by=full_user,
        )
        client = make_client(full_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res = client.post(f'{base}{report.id}/approve/')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.data['error']['code'] == 'sod_self_approve'

        report.refresh_from_db()
        assert report.status == SubReportStatus.SUBMITTED

    def test_superuser_break_glass_can_approve_as_preparer_and_submitter(
        self, admin_superuser, project,
    ):
        """Superuser break-glass allows approving even if superuser created and submitted it."""
        report = DisciplineSubReport.objects.create(
            project=project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.SUBMITTED,
            created_by=admin_superuser,
            submitted_by=admin_superuser,
            updated_by=admin_superuser,
        )
        client = make_client(admin_superuser)
        base = BASE.format(project_id=project.id, unit='buildings')

        res = client.post(f'{base}{report.id}/approve/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == SubReportStatus.APPROVED
        assert res.data['audit']['approved_by']['id'] == str(admin_superuser.id)

        report.refresh_from_db()
        assert report.status == SubReportStatus.APPROVED
        assert report.approved_by_id == admin_superuser.id
        assert report.approved_at is not None

    def test_independent_approver_can_approve(self, editor_user, approver_user, project):
        """Independent approver (not creator, not submitter) successfully approves."""
        report = DisciplineSubReport.objects.create(
            project=project,
            unit='buildings',
            discipline='civil',
            report_date=date(2026, 10, 20),
            lineage_id=uuid.uuid4(),
            version_number=1,
            is_current=True,
            status=SubReportStatus.SUBMITTED,
            created_by=editor_user,
            submitted_by=editor_user,
            updated_by=editor_user,
        )
        client = make_client(approver_user)
        base = BASE.format(project_id=project.id, unit='buildings')

        res = client.post(f'{base}{report.id}/approve/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == SubReportStatus.APPROVED

        report.refresh_from_db()
        assert report.status == SubReportStatus.APPROVED
        assert report.approved_by_id == approver_user.id
