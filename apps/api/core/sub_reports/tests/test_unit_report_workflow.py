"""T013 — unit-report open/create/edit/submit workflow (feature 032, US1; quickstart §4)."""

from datetime import date

import pytest
from rest_framework import status

from sub_reports.models import (
    DisciplineSubReport,
    SubReportStatus,
    UnitReportEventType,
    UnitReportStatusEvent,
)

BASE = '/api/v1/projects/{project_id}/units/{unit}/daily-reports/'


@pytest.fixture
def base(project):
    return BASE.format(project_id=project.id, unit='buildings')


@pytest.mark.django_db
class TestOpenOrCreate:
    def test_open_creates_first_draft(self, auth_client, base, project, user):
        res = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data['status'] == SubReportStatus.DRAFT
        assert res.data['unit'] == 'buildings'
        assert res.data['version_number'] == 1
        assert res.data['is_current'] is True
        report = DisciplineSubReport.objects.get(id=res.data['id'])
        assert report.project_id == project.id
        assert report.report_date == date(2026, 10, 20)
        assert report.created_by_id == user.id

    def test_open_is_idempotent(self, auth_client, base):
        first = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        second = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_200_OK
        assert second.data['id'] == first.data['id']
        assert DisciplineSubReport.objects.filter(unit='buildings').count() == 1

    def test_current_returns_404_when_absent(self, auth_client, base):
        res = auth_client.get(base + 'current/', {'date': '2026-10-20'})
        assert res.status_code == status.HTTP_404_NOT_FOUND

    def test_current_returns_existing(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        res = auth_client.get(base + 'current/', {'date': '2026-10-20'})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['id'] == created.data['id']

    def test_invalid_unit_rejected(self, auth_client, project):
        url = BASE.format(project_id=project.id, unit='plumbing') + 'open/'
        res = auth_client.post(url, {'report_date': '2026-10-20'}, format='json')
        assert res.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST)

    def test_dates_separate_lineages(self, auth_client, base):
        a = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        b = auth_client.post(base + 'open/', {'report_date': '2026-10-21'}, format='json')
        assert a.data['id'] != b.data['id']


@pytest.mark.django_db
class TestEditAndSubmit:
    def test_draft_editable_updates_actor_and_time(self, auth_client, base, user):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        res = auth_client.patch(
            f'{base}{rid}/', {'form_code': 'B-1'}, format='json',
        )
        assert res.status_code == status.HTTP_200_OK
        report = DisciplineSubReport.objects.get(id=rid)
        assert report.form_code == 'B-1'
        assert report.updated_by_id == user.id
        assert report.updated_at is not None

    def test_submit_moves_draft_to_submitted(self, auth_client, base, user):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        res = auth_client.post(f'{base}{rid}/submit/')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == SubReportStatus.SUBMITTED
        assert res.data['audit']['submitted_by']['id'] == str(user.id)
        assert res.data['audit']['submitted_at'] is not None
        events = UnitReportStatusEvent.objects.filter(report_version_id=rid)
        assert events.filter(event_type=UnitReportEventType.SUBMITTED).exists()

    def test_submitted_content_immutable(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        auth_client.post(f'{base}{rid}/submit/')
        res = auth_client.patch(f'{base}{rid}/', {'form_code': 'B-2'}, format='json')
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        report = DisciplineSubReport.objects.get(id=rid)
        assert report.form_code != 'B-2'
        assert report.status == SubReportStatus.SUBMITTED

    def test_rejected_report_editable(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        auth_client.post(f'{base}{rid}/submit/')
        auth_client.post(
            f'{base}{rid}/reject/',
            {'rejection_reason': 'اطلاعات ناقص است و نیاز به تکمیل دارد'},
            format='json',
        )
        res = auth_client.patch(f'{base}{rid}/', {'form_code': 'B-3'}, format='json')
        assert res.status_code == status.HTTP_200_OK

    def test_rejection_requires_reason(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        auth_client.post(f'{base}{rid}/submit/')

        # Whitespace-only reason
        res_blank = auth_client.post(f'{base}{rid}/reject/', {'rejection_reason': '   '}, format='json')
        assert res_blank.status_code == status.HTTP_400_BAD_REQUEST
        assert res_blank.data['error']['code'] == 'rejection_reason_required'

        # Empty reason
        res_empty = auth_client.post(f'{base}{rid}/reject/', {'rejection_reason': ''}, format='json')
        assert res_empty.status_code == status.HTTP_400_BAD_REQUEST
        assert res_empty.data['error']['code'] == 'rejection_reason_required'

        # Missing field
        res_missing = auth_client.post(f'{base}{rid}/reject/', {}, format='json')
        assert res_missing.status_code == status.HTTP_400_BAD_REQUEST
        assert res_missing.data['error']['code'] == 'rejection_reason_required'

        # State remains submitted
        report = DisciplineSubReport.objects.get(id=rid)
        assert report.status == SubReportStatus.SUBMITTED

    def test_rejection_records_reviewer_time_reason_and_event(self, auth_client, base, user):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        auth_client.post(f'{base}{rid}/submit/')

        reason_text = 'گزارش نیازمند بازبینی و ثبت جزئیات دقیق‌تر بتن‌ریزی است'
        res = auth_client.post(f'{base}{rid}/reject/', {'rejection_reason': reason_text}, format='json')
        assert res.status_code == status.HTTP_200_OK
        assert res.data['status'] == SubReportStatus.REJECTED
        assert res.data['audit']['rejected_by']['id'] == str(user.id)
        assert res.data['audit']['rejection_reason'] == reason_text
        assert res.data['audit']['rejected_at'] is not None

        # Verify DB model
        report = DisciplineSubReport.objects.get(id=rid)
        assert report.status == SubReportStatus.REJECTED
        assert report.rejected_by_id == user.id
        assert report.rejected_at is not None
        assert report.rejection_reason == reason_text

        # Verify status event
        event = UnitReportStatusEvent.objects.filter(
            report_version_id=rid,
            event_type=UnitReportEventType.REJECTED,
        ).first()
        assert event is not None
        assert event.from_status == SubReportStatus.SUBMITTED
        assert event.to_status == SubReportStatus.REJECTED
        assert event.actor_id == user.id
        assert event.reason == reason_text

    def test_delete_soft_deletes_draft(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        res = auth_client.delete(f'{base}{rid}/')
        assert res.status_code == status.HTTP_204_NO_CONTENT
        report = DisciplineSubReport.all_objects.get(id=rid)
        assert report.is_deleted is True

    def test_capabilities_reflect_state(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        res = auth_client.get(f'{base}{rid}/')
        assert res.data['capabilities']['can_edit'] is True
        assert res.data['capabilities']['can_submit'] is True
        assert res.data['capabilities']['can_approve'] is False

    def test_history_lists_versions_and_events(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']
        auth_client.post(f'{base}{rid}/submit/')
        res = auth_client.get(f'{base}{rid}/history/')
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['versions']) == 1
        assert any(e['event_type'] == 'submitted' for e in res.data['events'])


@pytest.mark.django_db
class TestCorrectionWorkflow:
    """T047: Approved report correction and resubmission preserving lineage and events."""

    @pytest.fixture
    def approver_client(self, db, project):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from master_data.models import MemberStatus, ProjectMember, ProjectMemberPermissionOverride

        User = get_user_model()
        approver = User.objects.create(
            username='unit_approver',
            mobile='+989129998877',
            full_name='Unit Approver',
        )
        m = ProjectMember.objects.create(
            project=project,
            user=approver,
            status=MemberStatus.ACTIVE,
        )
        for perm in ['view_reports', 'approve_reports']:
            ProjectMemberPermissionOverride.objects.create(
                member=m, permission_codename=perm, is_granted=True,
            )
        client = APIClient()
        client.force_authenticate(user=approver)
        return client

    def test_approved_correction_creates_version_n_plus_one_draft(
        self, auth_client, approver_client, base, user,
    ):
        # 1. Create and submit v1
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        v1_id = created.data['id']
        auth_client.patch(f'{base}{v1_id}/', {'form_code': 'BLD-V1'}, format='json')
        auth_client.post(f'{base}{v1_id}/submit/')

        # 2. Approver approves v1
        appr_res = approver_client.post(f'{base}{v1_id}/approve/')
        assert appr_res.status_code == status.HTTP_200_OK
        v1 = DisciplineSubReport.objects.get(id=v1_id)
        assert v1.status == SubReportStatus.APPROVED
        assert v1.is_current is True
        assert v1.version_number == 1

        # 3. Editor calls correct on v1
        corr_res = auth_client.post(f'{base}{v1_id}/correct/')
        assert corr_res.status_code == status.HTTP_200_OK
        assert corr_res.data['version_number'] == 2
        assert corr_res.data['status'] == SubReportStatus.DRAFT
        assert corr_res.data['is_current'] is True
        assert corr_res.data['lineage_id'] == str(v1.lineage_id)
        assert corr_res.data['capabilities']['can_edit'] is True

        v2_id = corr_res.data['id']
        assert v2_id != str(v1_id)

        # 4. Old version v1 is now read-only history
        v1.refresh_from_db()
        assert v1.status == SubReportStatus.APPROVED
        assert v1.is_current is False
        assert v1.version_number == 1

        v2 = DisciplineSubReport.objects.get(id=v2_id)
        assert v2.supersedes_id == v1.id
        assert v2.lineage_id == v1.lineage_id

        # Status event for correction
        event = UnitReportStatusEvent.objects.filter(
            event_type=UnitReportEventType.CORRECTED,
        ).first()
        assert event is not None
        assert event.actor_id == user.id

        # Historical v1 cannot be mutated
        patch_res = auth_client.patch(f'{base}{v1_id}/', {'form_code': 'BLD-HACK'}, format='json')
        assert patch_res.status_code == status.HTTP_400_BAD_REQUEST

        submit_old_res = auth_client.post(f'{base}{v1_id}/submit/')
        assert submit_old_res.status_code == status.HTTP_400_BAD_REQUEST

    def test_correction_only_allowed_on_approved_current_report(self, auth_client, base):
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        rid = created.data['id']

        # Draft -> correct refused
        res_draft = auth_client.post(f'{base}{rid}/correct/')
        assert res_draft.status_code == status.HTTP_400_BAD_REQUEST
        assert res_draft.data['error']['code'] == 'invalid_unit_report_transition'

        # Submitted -> correct refused
        auth_client.post(f'{base}{rid}/submit/')
        res_sub = auth_client.post(f'{base}{rid}/correct/')
        assert res_sub.status_code == status.HTTP_400_BAD_REQUEST
        assert res_sub.data['error']['code'] == 'invalid_unit_report_transition'

        # Rejected -> correct refused
        auth_client.post(f'{base}{rid}/reject/', {'rejection_reason': 'Need details'}, format='json')
        res_rej = auth_client.post(f'{base}{rid}/correct/')
        assert res_rej.status_code == status.HTTP_400_BAD_REQUEST
        assert res_rej.data['error']['code'] == 'invalid_unit_report_transition'

    def test_rejected_correction_resubmits_cleanly_preserving_all_events(
        self, auth_client, approver_client, base,
    ):
        # Create and approve v1
        created = auth_client.post(base + 'open/', {'report_date': '2026-10-20'}, format='json')
        v1_id = created.data['id']
        auth_client.post(f'{base}{v1_id}/submit/')
        approver_client.post(f'{base}{v1_id}/approve/')

        # Correct to v2
        corr = auth_client.post(f'{base}{v1_id}/correct/')
        v2_id = corr.data['id']

        # Edit v2, submit v2
        auth_client.patch(f'{base}{v2_id}/', {'form_code': 'V2-REV1'}, format='json')
        auth_client.post(f'{base}{v2_id}/submit/')

        # Approver rejects v2
        rej = approver_client.post(
            f'{base}{v2_id}/reject/',
            {'rejection_reason': 'مقادیر بتن نیازمند تایید آزمایشگاه است'},
            format='json',
        )
        assert rej.status_code == status.HTTP_200_OK

        v2 = DisciplineSubReport.objects.get(id=v2_id)
        assert v2.status == SubReportStatus.REJECTED

        # Edit and resubmit v2
        auth_client.patch(f'{base}{v2_id}/', {'form_code': 'V2-FINAL'}, format='json')
        resub = auth_client.post(f'{base}{v2_id}/submit/')
        assert resub.status_code == status.HTTP_200_OK
        assert resub.data['status'] == SubReportStatus.SUBMITTED

        # History includes both versions and all state-transition events
        hist = auth_client.get(f'{base}{v2_id}/history/')
        assert hist.status_code == status.HTTP_200_OK
        data = hist.data

        assert len(data['versions']) == 2
        ver_map = {v['version_number']: v for v in data['versions']}
        assert ver_map[1]['is_current'] is False
        assert ver_map[1]['status'] == SubReportStatus.APPROVED
        assert ver_map[1]['superseded_by'] == v2_id

        assert ver_map[2]['is_current'] is True
        assert ver_map[2]['status'] == SubReportStatus.SUBMITTED
        assert ver_map[2]['supersedes'] == v1_id
        assert ver_map[2]['superseded_by'] is None

        event_types = [e['event_type'] for e in data['events']]
        assert event_types.count('created') == 1
        assert 'corrected' in event_types
        assert 'rejected' in event_types
        assert event_types.count('submitted') >= 2

