"""NEG-12: viewer reads are allowed; all project/schedule mutations are denied."""
import pytest
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from master_data.models import ProjectMember, ProjectMemberRole
from projects.models import Project, ProjectKickoffCharter, Activity, WBS
from schedule.models import BaselineSchedule, BaselineActivity, MspImportJob, P6ImportJob
from schedule.services.msp_import import execute_msp_import
from schedule.tests.test_a7_neg01_duplicate_codes import FIXTURES
from schedule.tests.test_a7_cycle_cancel_acceptance import snapshot


@pytest.mark.django_db
def test_viewer_cannot_mutate_project_baseline_wbs_or_import(project, user, other_user, viewer_role):
    member = ProjectMember.objects.create(project=project, user=other_user, status='active')
    ProjectMemberRole.objects.create(member=member, role=viewer_role)
    client = APIClient()
    client.force_authenticate(other_user)
    execute_msp_import(project, (FIXTURES / 'branch.xml').read_bytes(), filename='branch.xml', user=user)
    ProjectKickoffCharter.objects.create(project=project, justification='Retained charter', created_by=user)
    baseline = BaselineSchedule.objects.get(project=project)
    assert not baseline.is_locked
    ba = BaselineActivity.objects.filter(baseline=baseline).first()
    node = WBS.objects.filter(project=project).first()
    activity = Activity.objects.filter(project=project).first()
    base = f'/api/v1/projects/{project.id}/'
    for path in ['', 'wbs/', 'activities/', 'baselines/', 'gantt/', 'schedule-status/', 'kickoff-charter/']:
        response = client.get(base + path)
        assert response.status_code == 200, (path, response.data)

    def state():
        return {
            'project': list(Project.objects.filter(pk=project.id).values()),
            'charter': list(ProjectKickoffCharter.objects.filter(project=project).values()),
            'domain': snapshot(project),
            'msp_jobs': list(MspImportJob.objects.filter(project=project).values()),
            'p6_jobs': list(P6ImportJob.objects.filter(project=project).values()),
        }

    before = state()
    mutations = [
        ('patch', '', {'project_name': 'Forbidden rename'}),
        ('delete', '', {}),
        ('put', 'kickoff-charter/', {'justification': 'Forbidden charter'}),
        ('post', 'baselines/', {'version_name': 'Forbidden snapshot'}),
        ('post', f'baselines/{baseline.id}/approve-lock/', {}),
        ('patch', f'baselines/{baseline.id}/activities/{ba.id}/', {'planned_duration': 999}),
        ('delete', f'baselines/{baseline.id}/activities/{ba.id}/', {}),
        ('post', 'wbs/', {'wbs_code': 'VIEWER', 'wbs_name': 'Forbidden'}),
        ('patch', f'wbs/{node.id}/', {'wbs_name': 'Forbidden rename'}),
        ('delete', f'wbs/{node.id}/', {}),
        ('patch', f'activities/{activity.id}/', {'activity_name': 'Forbidden rename'}),
    ]
    for method, path, payload in mutations:
        response = getattr(client, method)(base + path, payload, format='json')
        assert response.status_code == 403, (method, path, response.data)
        assert state() == before, (method, path)
    for family, filename in [('msp', 'branch.xml'), ('p6', 'branch.xer')]:
        for suffix in ['preview/', '']:
            response = client.post(base + f'import/{family}/' + suffix,
                {'file': SimpleUploadedFile(filename, (FIXTURES / filename).read_bytes())}, format='multipart')
            assert response.status_code == 403, response.data
            assert state() == before
