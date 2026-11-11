"""Safety checks for schedule import. Uses project codes that start with A7P2-IMPORT-SAFETY."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import translation
from rest_framework.test import APIClient

from cost_control.models import Budget
from documents.models import ProjectDocument
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole
from projects.models import Activity, ProjectStatus, WBS
from projects.services import create_project_with_creator
from schedule.models import (
    ActivityProgress,
    BaselineActivity,
    BaselineSchedule,
    MspImportJob,
    MspImportStatus,
)
from schedule.services.import_safety import ImportSafetyError, message_for
from schedule.services.msp_import import execute_msp_import
from schedule.services.p6_import import execute_p6_import
from schedule.tasks import run_msp_import_task
from schedule.tests.test_msp_import import SAMPLE_MSP_XML
from schedule.tests.test_p6_import import SAMPLE_XER
from wbs.services import create_wbs_node

PROTECTION_CODES = {
    'wbs_has_progress',
    'wbs_has_cost',
    'wbs_has_documents',
    'wbs_has_activities',
    'baseline_history_protected',
}


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P2-IMPORT-SAFETY-{suffix}',
        project_name=f'Import safety {suffix}',
        employer='Safety Co',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


def _live_counts(project):
    return {
        'wbs': WBS.objects.filter(project=project, is_deleted=False).count(),
        'activities': Activity.objects.filter(project=project, is_deleted=False).count(),
        'baseline_rows': BaselineActivity.objects.filter(baseline__project=project).count(),
        'baselines': BaselineSchedule.objects.filter(project=project, is_deleted=False).count(),
    }


def _node(project):
    node, _warnings = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    return node


def _activity(project, node, user, code='A1'):
    return Activity.objects.create(
        project=project,
        wbs=node,
        activity_code=code,
        activity_name=code,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
def test_replacement_refuses_each_protection_before_any_change(user):
    cases = []

    progress_project = _project(user, 'PROGRESS')
    progress_node = _node(progress_project)
    progress_activity = _activity(progress_project, progress_node, user)
    ActivityProgress.objects.create(activity=progress_activity, report_date=date(2026, 1, 2), actual_progress=1)
    cases.append((progress_project, 'wbs_has_progress'))

    cost_project = _project(user, 'COST')
    cost_node = _node(cost_project)
    Budget.objects.create(
        project=cost_project,
        wbs=cost_node,
        cost_category='labor',
        budget_amount=10,
        created_by=user,
        updated_by=user,
    )
    cases.append((cost_project, 'wbs_has_cost'))

    document_project = _project(user, 'DOC')
    document_node = _node(document_project)
    ProjectDocument.objects.create(
        project=document_project,
        title='Drawing',
        related_wbs=document_node,
        created_by=user,
        updated_by=user,
        uploaded_by=user,
    )
    cases.append((document_project, 'wbs_has_documents'))

    activity_project = _project(user, 'ACT')
    _activity(activity_project, _node(activity_project), user)
    cases.append((activity_project, 'wbs_has_activities'))

    baseline_project = _project(user, 'BASE')
    _node(baseline_project)
    BaselineSchedule.objects.create(
        project=baseline_project,
        version_name='Approved',
        is_locked=True,
        is_current=True,
        approved_at=date(2026, 1, 3),
        created_by=user,
        updated_by=user,
    )
    cases.append((baseline_project, 'baseline_history_protected'))

    for project, expected in cases:
        before = _live_counts(project)
        with pytest.raises(ImportSafetyError) as exc:
            execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=True, user=user)
        assert exc.value.code == expected
        assert exc.value.code in PROTECTION_CODES
        with pytest.raises(ImportSafetyError) as xer_exc:
            execute_p6_import(project, SAMPLE_XER, filename='plan.xer', replace=True, user=user)
        assert xer_exc.value.code == expected
        assert _live_counts(project) == before


@pytest.mark.django_db
def test_mpp_replacement_of_protected_project_is_refused_by_the_api(auth_client, user):
    from unittest.mock import patch

    project = _project(user, 'MPP')
    _activity(project, _node(project), user)
    before = _live_counts(project)
    upload = SimpleUploadedFile('plan.mpp', b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1body', content_type='application/octet-stream')
    with patch('schedule.services.mpp_convert.convert_mpp_to_mspdi', return_value=SAMPLE_MSP_XML):
        response = auth_client.post(
            f'/api/v1/projects/{project.id}/import/msp/',
            {'file': upload, 'replace': 'true'},
            format='multipart',
        )
    assert response.status_code == 400
    assert response.data['error']['code'] == 'wbs_has_activities'
    assert _live_counts(project) == before


@pytest.mark.django_db
def test_unprotected_replacement_soft_deletes_and_reports_counts(user):
    project = _project(user, 'OPEN')
    node = _node(project)
    other = _project(user, 'OTHER')
    other_node = _node(other)
    result = execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=True, user=user)
    node.refresh_from_db()
    assert node.is_deleted is True
    assert result['wbs_nodes_removed'] >= 1
    assert result['activities_created'] >= 1
    assert WBS.objects.filter(pk=node.id).exists()
    other_node.refresh_from_db()
    assert other_node.is_deleted is False
    with pytest.raises(ImportSafetyError) as second:
        execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=True, user=user)
    assert second.value.code == 'wbs_has_activities'
    assert WBS.objects.filter(pk=node.id, is_deleted=True).exists()
    assert Activity.objects.filter(project=project, is_deleted=False).count() == result['activities_created']


@pytest.mark.django_db
def test_repeat_append_does_not_publish_another_current_baseline(user, auth_client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    project = _project(user, 'REPEAT')
    first = execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=False, user=user)
    assert first['activities_created'] >= 1
    assert first['schedule_version_changed'] is True
    activity_count = Activity.objects.filter(project=project, is_deleted=False).count()
    current = BaselineSchedule.objects.filter(project=project, is_current=True).count()
    second = execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=False, user=user)
    assert second['nothing_changed'] is True
    assert second['schedule_version_changed'] is False
    assert second['baseline_id'] is None
    assert Activity.objects.filter(project=project, is_deleted=False).count() == activity_count
    assert BaselineSchedule.objects.filter(project=project, is_current=True).count() == current

    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        replace_existing=False,
        created_by=user,
        status=MspImportStatus.DONE,
        result=second,
    )
    before = _live_counts(project)
    status_url = f'/api/v1/projects/{project.id}/import/msp/status/{job.id}/'
    assert auth_client.get(status_url).status_code == 200
    assert auth_client.get(status_url).status_code == 200
    assert _live_counts(project) == before

    upload = SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': upload, 'replace': 'false'},
        format='multipart',
    )
    assert response.status_code == 202
    assert response.data['task_id'] != str(job.id)


@pytest.mark.django_db
def test_inflight_start_returns_the_same_job(auth_client, user):
    project = _project(user, 'FLIGHT')
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        replace_existing=False,
        created_by=user,
        status=MspImportStatus.PENDING,
    )
    upload = SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')
    response = auth_client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': upload, 'replace': 'false'},
        format='multipart',
    )
    assert response.status_code == 202
    assert response.data['task_id'] == str(job.id)
    assert MspImportJob.objects.filter(project=project).count() == 1


@pytest.mark.django_db
def test_archived_project_blocks_member_and_allows_admin_member_only_through_history_gate(
    user, other_user, project_manager_role,
):
    project = _project(user, 'ARCH')
    _activity(project, _node(project), user)
    project.archived_from_status = project.status
    project.archive_cycle_id = uuid4()
    project.status = ProjectStatus.ARCHIVED
    project.save(update_fields=['status', 'archived_from_status', 'archive_cycle_id', 'updated_at'])
    before = _live_counts(project)
    client = APIClient()
    client.force_authenticate(user=user)
    upload = SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')
    response = client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': upload, 'replace': 'true'},
        format='multipart',
    )
    assert response.status_code == 400
    assert response.data['error']['code'] == 'project_archived'
    preview = client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')},
        format='multipart',
    )
    assert preview.status_code == 200
    assert _live_counts(project) == before

    outsider = APIClient()
    group, _created = Group.objects.get_or_create(name='admin')
    other_user.groups.add(group)
    outsider.force_authenticate(user=other_user)
    denied = outsider.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'), 'replace': 'true'},
        format='multipart',
    )
    assert denied.status_code == 403

    member = ProjectMember.objects.create(project=project, user=other_user, status=MemberStatus.ACTIVE)
    ProjectMemberRole.objects.create(member=member, role=project_manager_role)
    allowed = outsider.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml'), 'replace': 'true'},
        format='multipart',
    )
    assert allowed.status_code == 400
    assert allowed.data['error']['code'] in PROTECTION_CODES
    assert allowed.data['error']['code'] != 'project_archived'
    assert _live_counts(project) == before

    with translation.override('fa'):
        assert 'بایگانی' in message_for('project_archived')
    with translation.override('en'):
        assert 'read-only' in message_for('project_archived')


@pytest.mark.django_db
def test_apply_rechecks_permission_and_hides_other_projects(user, other_user, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    project = _project(user, 'RECHECK')
    other = _project(other_user, 'FOREIGN')
    other_before = _live_counts(other)
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        replace_existing=False,
        created_by=user,
        status=MspImportStatus.PENDING,
    )
    membership = project.members.get(user=user)
    membership.status = MemberStatus.INACTIVE
    membership.save(update_fields=['status'])
    before = _live_counts(project)
    run_msp_import_task.apply(args=[str(job.id)])
    job.refresh_from_db()
    assert job.status == MspImportStatus.FAILED
    assert job.error_code == 'import_not_permitted'
    assert _live_counts(project) == before

    client = APIClient()
    client.force_authenticate(user=user)
    hidden = client.get(f'/api/v1/projects/{other.id}/import/msp/status/{job.id}/')
    assert hidden.status_code in (403, 404)
    upload = SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')
    cross = client.post(
        f'/api/v1/projects/{other.id}/import/msp/',
        {'file': upload, 'replace': 'false'},
        format='multipart',
    )
    assert cross.status_code == 403
    assert _live_counts(other) == other_before


@pytest.mark.django_db
def test_preview_and_mid_write_failure_leave_counts_and_a_later_import_works(auth_client, user):
    from unittest.mock import patch

    project = _project(user, 'FAIL')
    _node(project)
    before = _live_counts(project)
    preview = auth_client.post(
        f'/api/v1/projects/{project.id}/import/msp/preview/',
        {'file': SimpleUploadedFile('plan.xml', SAMPLE_MSP_XML, content_type='application/xml')},
        format='multipart',
    )
    assert preview.status_code == 200
    assert _live_counts(project) == before
    bad = auth_client.post(
        f'/api/v1/projects/{project.id}/import/msp/',
        {'file': SimpleUploadedFile('bad.xml', b'<not-project/>', content_type='application/xml'), 'replace': 'false'},
        format='multipart',
    )
    assert bad.status_code == 400
    assert _live_counts(project) == before

    with patch(
        'schedule.services.shared_import.Activity.objects.bulk_create',
        side_effect=RuntimeError('mid-write'),
    ):
        with pytest.raises(RuntimeError):
            execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=True, user=user)
    assert _live_counts(project) == before
    recovered = execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=True, user=user)
    assert recovered['activities_created'] >= 1


@pytest.mark.django_db
def test_missing_actor_writes_no_rows_and_success_names_the_member(user):
    project = _project(user, 'ACTOR')
    result = execute_msp_import(project, SAMPLE_MSP_XML, filename='plan.xml', replace=False, user=user)
    created = Activity.objects.filter(project=project, is_deleted=False)
    assert created.exists()
    assert set(created.values_list('created_by_id', flat=True)) == {user.id}
    nodes = WBS.objects.filter(project=project, is_deleted=False)
    assert set(nodes.values_list('created_by_id', flat=True)) == {user.id}
    baseline = BaselineSchedule.objects.get(pk=result['baseline_id'])
    assert baseline.created_by_id == user.id
    assert baseline.is_locked is False
    assert baseline.approved_at is None

    empty = _project(user, 'NOACTOR')
    before = _live_counts(empty)
    with pytest.raises(ImportSafetyError) as exc:
        execute_msp_import(empty, SAMPLE_MSP_XML, filename='plan.xml', replace=False, user=None)
    assert exc.value.code == 'import_actor_missing'
    assert _live_counts(empty) == before
    assert not Activity.objects.filter(project=empty).exclude(created_by=user).exists()
