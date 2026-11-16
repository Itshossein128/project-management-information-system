"""NEG-11: real routes, valid foreign IDs and an ordinary project member."""
import pytest
from projects.models import Activity, ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import BaselineSchedule, BaselineActivity, MspImportJob, P6ImportJob
from schedule.services.msp_import import execute_msp_import
from schedule.tests.test_a7_neg01_duplicate_codes import FIXTURES, snapshot


@pytest.mark.django_db
def test_foreign_schedule_baseline_and_job_ids_are_isolated(project, user, other_user, auth_client):
    foreign = create_project_with_creator(creator=other_user, project_code='NEG11-B', project_name='Foreign', employer='B', start_date='2026-01-01')
    foreign.status = ProjectStatus.ACTIVE
    foreign.save(update_fields=['status'])
    execute_msp_import(foreign, (FIXTURES / 'branch.xml').read_bytes(), filename='branch.xml', user=other_user)
    activity = Activity.objects.filter(project=foreign).first()
    baseline = BaselineSchedule.objects.get(project=foreign)
    ba = BaselineActivity.objects.filter(baseline=baseline).first()
    before = snapshot(foreign)
    before_ba = list(BaselineActivity.objects.filter(baseline=baseline).order_by("pk").values())
    for suffix in ['activities/', 'baselines/', 'gantt/', 'schedule-status/']:
        assert auth_client.get(f'/api/v1/projects/{project.id}/{suffix}').status_code == 200
        assert auth_client.get(f'/api/v1/projects/{foreign.id}/{suffix}').status_code == 403
    assert auth_client.get(f'/api/v1/projects/{project.id}/activities/{activity.id}/').status_code == 404
    # A foreign baseline query must never include that baseline's rows.
    gantt = auth_client.get(f'/api/v1/projects/{project.id}/gantt/', {'baseline_id': str(baseline.id)})
    assert gantt.status_code == 200
    assert str(activity.id) not in str(gantt.data)
    assert str(baseline.id) not in str(gantt.data)
    for method in [auth_client.patch, auth_client.delete]:
        result = method(f'/api/v1/projects/{project.id}/baselines/{baseline.id}/activities/{ba.id}/', {'planned_duration': 999}, format='json')
        assert result.status_code == 404
        assert snapshot(foreign) == before
        assert list(BaselineActivity.objects.filter(baseline=baseline).order_by("pk").values()) == before_ba
    for family, model in [('msp', MspImportJob), ('p6', P6ImportJob)]:
        job = model.objects.create(project=foreign, created_by=other_user, filename='foreign.xml', file_data=b'private', status='done')
        assert auth_client.get(f'/api/v1/projects/{project.id}/import/{family}/status/{job.id}/').status_code == 404
        assert auth_client.get(f'/api/v1/projects/{foreign.id}/import/{family}/status/{job.id}/').status_code == 403
