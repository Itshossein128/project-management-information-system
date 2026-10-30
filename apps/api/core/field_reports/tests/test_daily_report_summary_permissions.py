import pytest
from rest_framework import status

from field_reports.models import DailyReport, ReportStatus
from field_reports.services.daily_report_aggregation import ensure_daily_report_summary
from field_reports.tests.daily_report_summary_helpers import (
    SUMMARY_DATE,
    add_activity,
    make_sub_report,
)
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role, RolePermission
from sub_reports.models import SubReportStatus


@pytest.fixture
def viewer_member(project, other_user):
    role = Role.objects.create(role_name='summary_viewer_only', description='Summary viewer')
    RolePermission.objects.create(role=role, permission_codename='view_project')
    RolePermission.objects.create(role=role, permission_codename='view_reports')
    member = ProjectMember.objects.create(
        project=project, user=other_user, status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member, role=role)
    return member


@pytest.mark.django_db
def test_view_reports_without_edit_can_get_by_date_existing_but_cannot_post(
    api_client, project, user, other_user, viewer_member,
):
    sr = make_sub_report(project, user, status=SubReportStatus.SUBMITTED)
    add_activity(sr)
    ensure_daily_report_summary(project.id, SUMMARY_DATE, user=user)

    api_client.force_authenticate(user=other_user)
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'

    # GET existing returns 200
    assert api_client.get(by_date, {'date': SUMMARY_DATE.isoformat()}).status_code == status.HTTP_200_OK

    # POST returns 403 Forbidden because user lacks edit_reports
    post_res = api_client.post(by_date, {'date': SUMMARY_DATE.isoformat()}, format='json')
    assert post_res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_view_reports_without_edit_can_get_shell_but_cannot_post(
    api_client, project, other_user, viewer_member,
):
    api_client.force_authenticate(user=other_user)
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
    initial_count = DailyReport.objects.filter(project=project).count()

    res = api_client.get(by_date, {'date': '2026-08-01'})
    # Feature 039 explicitly permits server-owned shell provisioning on GET
    # for read-only viewers; it does not grant user-authored write access.
    assert res.status_code == status.HTTP_200_OK
    assert res.data['is_auto_summary'] is True
    assert DailyReport.objects.filter(project=project).count() == initial_count + 1

    # POST returns 403 and creates no additional records.
    post_res = api_client.post(by_date, {'date': '2026-08-01'}, format='json')
    assert post_res.status_code == status.HTTP_403_FORBIDDEN
    assert DailyReport.objects.filter(project=project).count() == initial_count + 1


@pytest.mark.django_db
def test_editor_can_post_by_date_and_ensures_single_summary(
    auth_client, project, user,
):
    by_date = f'/api/v1/projects/{project.id}/daily-reports/by-date/'
    post_res_1 = auth_client.post(by_date, {'date': '2026-08-15'}, format='json')
    assert post_res_1.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)

    # Calling post again for the same date returns the same report, exactly 1 row
    post_res_2 = auth_client.post(by_date, {'date': '2026-08-15'}, format='json')
    assert post_res_2.status_code in (status.HTTP_200_OK, status.HTTP_201_CREATED)
    assert DailyReport.objects.filter(project=project, report_date='2026-08-15', is_deleted=False).count() == 1


@pytest.mark.django_db
def test_viewer_cannot_cancel_correction_request(
    api_client, project, user, other_user, viewer_member,
):
    source = DailyReport.objects.create(
        project=project,
        report_date='2026-08-20',
        status=ReportStatus.APPROVED,
        is_current=True,
        created_by=user,
        updated_by=user,
    )
    api_client.force_authenticate(user=user)
    opened = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{source.id}/correction-requests/',
        {'reason': 'اصلاح برای آزمایش مجوز لغو'},
        format='json',
    )
    assert opened.status_code == status.HTTP_201_CREATED

    api_client.force_authenticate(user=other_user)
    denied = api_client.post(
        f'/api/v1/projects/{project.id}/correction-requests/{opened.data["id"]}/cancel/',
        format='json',
    )
    assert denied.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_cancel_correction_rejects_foreign_project_scope(
    api_client, project, user, db,
):
    from projects.models import Project

    other = Project.objects.create(
        project_code='PRJ-LIFECYCLE-OTHER',
        project_name='Other lifecycle project',
        employer='Employer Co',
    )
    source = DailyReport.objects.create(
        project=project,
        report_date='2026-08-21',
        status=ReportStatus.APPROVED,
        is_current=True,
        created_by=user,
        updated_by=user,
    )
    api_client.force_authenticate(user=user)
    opened = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{source.id}/correction-requests/',
        {'reason': 'اصلاح برای آزمایش دامنه پروژه'},
        format='json',
    )
    assert opened.status_code == status.HTTP_201_CREATED

    missing = api_client.post(
        f'/api/v1/projects/{other.id}/correction-requests/{opened.data["id"]}/cancel/',
        format='json',
    )
    assert missing.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_viewer_and_non_member_cannot_open_correction_request(
    api_client, project, user, other_user, viewer_member,
):
    source = DailyReport.objects.create(
        project=project,
        report_date='2026-08-22',
        status=ReportStatus.APPROVED,
        is_current=True,
        created_by=user,
        updated_by=user,
    )
    from field_reports.models import DailyReportCorrectionRequest
    initial_corr_count = DailyReportCorrectionRequest.objects.filter(project=project).count()

    # 1. Viewer attempt
    api_client.force_authenticate(user=other_user)
    viewer_res = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{source.id}/correction-requests/',
        {'reason': 'تلاش ناظر برای باز کردن اصلاح'},
        format='json',
    )
    assert viewer_res.status_code == status.HTTP_403_FORBIDDEN

    # 2. Non-member attempt
    from django.contrib.auth import get_user_model
    User = get_user_model()
    unaffiliated = User.objects.create_user(
        username='unaffiliated_user',
        mobile='+989129999999',
        password='testpass123',
        is_active=True,
    )
    api_client.force_authenticate(user=unaffiliated)
    non_member_res = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{source.id}/correction-requests/',
        {'reason': 'تلاش کاربر غیرعضو برای باز کردن اصلاح'},
        format='json',
    )
    assert non_member_res.status_code == status.HTTP_403_FORBIDDEN

    # Verify zero mutations
    assert DailyReportCorrectionRequest.objects.filter(project=project).count() == initial_corr_count
    source.refresh_from_db()
    assert source.is_current is True


@pytest.mark.django_db
def test_dual_project_member_idor_isolation_for_initiation_and_cancellation(
    api_client, project, user, db,
):
    """Even a user with edit_reports on both projects cannot access resources across project URLs."""
    from projects.models import Project
    from master_data.models import ProjectMember, ProjectMemberRole, Role, RolePermission, MemberStatus
    from field_reports.models import DailyReportCorrectionRequest, CorrectionRequestStatus

    project_b = Project.objects.create(
        project_code='PRJ-IDOR-B',
        project_name='Project B for IDOR Test',
        employer='Employer B',
    )
    # Grant user edit_reports in both projects
    role_editor = Role.objects.create(role_name='editor_role_idor', description='Editor')
    RolePermission.objects.create(role=role_editor, permission_codename='view_project')
    RolePermission.objects.create(role=role_editor, permission_codename='view_reports')
    RolePermission.objects.create(role=role_editor, permission_codename='edit_reports')

    member_b = ProjectMember.objects.create(
        project=project_b, user=user, status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=member_b, role=role_editor)

    # Approved report in Project B
    report_b = DailyReport.objects.create(
        project=project_b,
        report_date='2026-08-23',
        status=ReportStatus.APPROVED,
        is_current=True,
        created_by=user,
        updated_by=user,
    )

    api_client.force_authenticate(user=user)

    # 1. IDOR initiation: Try opening correction for report_b using project A URL
    idor_open = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/{report_b.id}/correction-requests/',
        {'reason': 'تلاش باز کردن اصلاح با شناسه گزارش پروژه دیگر'},
        format='json',
    )
    assert idor_open.status_code == status.HTTP_404_NOT_FOUND
    assert DailyReportCorrectionRequest.objects.filter(source_report=report_b).count() == 0

    # Open legitimate correction in Project B
    legit_open = api_client.post(
        f'/api/v1/projects/{project_b.id}/daily-reports/{report_b.id}/correction-requests/',
        {'reason': 'درخواست اصلاح معتبر در پروژه ب'},
        format='json',
    )
    assert legit_open.status_code == status.HTTP_201_CREATED
    corr_b_id = legit_open.data['id']

    # 2. IDOR cancellation: Try cancelling Project B correction using Project A URL (canonical)
    idor_cancel = api_client.post(
        f'/api/v1/projects/{project.id}/correction-requests/{corr_b_id}/cancel/',
        format='json',
    )
    assert idor_cancel.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN)

    # 3. IDOR cancellation: Try cancelling Project B correction using Project A URL (alias)
    idor_cancel_alias = api_client.post(
        f'/api/v1/projects/{project.id}/daily-reports/correction-requests/{corr_b_id}/cancel/',
        format='json',
    )
    assert idor_cancel_alias.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN)

    # Verify zero mutations on Project B correction and report
    corr_b = DailyReportCorrectionRequest.objects.get(pk=corr_b_id)
    assert corr_b.status == CorrectionRequestStatus.SUBMITTED
    report_b.refresh_from_db()
    assert report_b.is_current is False
    result_b = DailyReport.objects.get(pk=legit_open.data['result_report_id'])
    assert result_b.is_current is True
    assert not result_b.is_deleted
