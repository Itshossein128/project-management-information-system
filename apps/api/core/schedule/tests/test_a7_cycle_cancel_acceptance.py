"""NEG-03/07 acceptance: rejected cycles and preview never mutate the domain."""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from schedule.models import MspImportJob, P6ImportJob, BaselineActivity
from schedule.services.msp_import import execute_msp_import
from schedule.services.p6_import import execute_p6_import
from schedule.services.import_fidelity import ImportFidelityError
from schedule.tests.test_a7_neg01_duplicate_codes import FIXTURES, snapshot as domain_snapshot
from wbs.services import create_wbs_node


def snapshot(project):
    data = domain_snapshot(project)
    data["baseline_activities"] = list(BaselineActivity.objects.filter(baseline__project=project).order_by("pk").values())
    return data


def cycle_file(family, length):
    if family == 'msp':
        tasks = '<Task><UID>1</UID><Name>Root</Name><WBS>1</WBS><OutlineNumber>1</OutlineNumber><Summary>1</Summary></Task>'
        for i in range(length):
            tasks += f'<Task><UID>{i+2}</UID><Name>Work {i}</Name><WBS>1.{i+1}</WBS><OutlineNumber>1.{i+1}</OutlineNumber><Summary>0</Summary><Duration>PT8H0M0S</Duration><PredecessorLink><PredecessorUID>{(i-1)%length+2}</PredecessorUID><Type>1</Type></PredecessorLink></Task>'
        return f'<?xml version="1.0"?><Project xmlns="http://schemas.microsoft.com/project"><Tasks>{tasks}</Tasks></Project>'.encode()
    lines = ['ERMHDR\t18.8', '%T\tPROJWBS', '%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name', '%R\t1\t\t1\tRoot', '%T\tTASK', '%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt']
    lines += [f'%R\t{i+2}\t1\tA{i}\tWork {i}\t8' for i in range(length)]
    lines += ['%T\tTASKPRED', '%F\ttask_id\tpred_task_id\tpred_type\tlag_hr_cnt']
    lines += [f'%R\t{i+2}\t{(i-1)%length+2}\tPR_FS\t0' for i in range(length)]
    return ('\n'.join(lines)+'\n').encode()


@pytest.mark.django_db
@pytest.mark.parametrize('family', ['msp', 'p6'])
@pytest.mark.parametrize('length', [1, 2, 3])
def test_cycles_reject_preview_and_append_replace_atomically(project, user, auth_client, family, length, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    create_wbs_node(project_id=project.id, wbs_code='KEEP', wbs_name='Keep')
    runner = execute_msp_import if family == 'msp' else execute_p6_import
    valid_name = 'branch.xml' if family == 'msp' else 'branch.xer'
    runner(project, (FIXTURES / valid_name).read_bytes(), filename=valid_name, user=user)
    before = snapshot(project)
    assert before['activities'] and before['baselines'] and before['baseline_activities']
    payload = cycle_file(family, length)
    filename = 'cycle.xml' if family == 'msp' else 'cycle.xer'
    preview = auth_client.post(f'/api/v1/projects/{project.id}/import/{family}/preview/', {'file': SimpleUploadedFile(filename, payload)}, format='multipart')
    assert preview.status_code == 200, preview.data
    assert any(x['code'] == 'structure_cycle' for x in preview.data['blocking'])
    assert snapshot(project) == before
    for replace in [False, True]:
        with pytest.raises(ImportFidelityError) as exc:
            runner(project, payload, filename=filename, replace=replace, user=user)
        assert exc.value.code == 'structure_cycle'
        assert snapshot(project) == before
        start = auth_client.post(f'/api/v1/projects/{project.id}/import/{family}/', {'file': SimpleUploadedFile(filename, payload), 'replace': str(replace).lower()}, format='multipart')
        if replace:
            # Admission rejects replacing populated schedules before dispatch.
            assert start.status_code == 400, start.data
            assert start.data['error']['code'] == 'wbs_has_activities'
            assert snapshot(project) == before
            continue
        assert start.status_code == 202, start.data
        result = auth_client.get(f'/api/v1/projects/{project.id}/import/{family}/status/{start.data["task_id"]}/')
        assert result.data['status'] == 'failed', result.data
        assert result.data['error_code'] == 'structure_cycle'
        assert snapshot(project) == before


@pytest.mark.django_db
def test_wbs_direct_and_indirect_cycles_preserve_tree(auth_client, project):
    root, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
    child, _ = create_wbs_node(project_id=project.id, parent_id=root.id, wbs_code='1.1', wbs_name='Child')
    grandchild, _ = create_wbs_node(project_id=project.id, parent_id=child.id, wbs_code='1.1.1', wbs_name='Grandchild')
    before = snapshot(project)
    for target in [root, child, grandchild]:
        result = auth_client.post(f'/api/v1/projects/{project.id}/wbs/{root.id}/move/', {'new_parent_id': str(target.id), 'position': 'last-child'}, format='json')
        assert result.status_code == 400, result.data
        assert 'wbs_cycle' in str(result.data)
        assert snapshot(project) == before


@pytest.mark.django_db
@pytest.mark.parametrize('family,filename', [('msp', 'branch.xml'), ('p6', 'branch.xer')])
def test_preview_without_confirmation_creates_no_jobs(project, auth_client, family, filename):
    create_wbs_node(project_id=project.id, wbs_code='KEEP', wbs_name='Keep')
    before = snapshot(project)
    jobs = (list(MspImportJob.objects.values()), list(P6ImportJob.objects.values()))
    result = auth_client.post(f'/api/v1/projects/{project.id}/import/{family}/preview/', {'file': SimpleUploadedFile(filename, (FIXTURES / filename).read_bytes())}, format='multipart')
    assert result.status_code == 200, result.data
    assert snapshot(project) == before
    assert (list(MspImportJob.objects.values()), list(P6ImportJob.objects.values())) == jobs
