import pytest
from decision_support.models import DecisionCase, DecisionRun
from decision_support.services.case_service import update_case, create_case
from config.exceptions import CodedValidationError

BASE='/api/v1/projects/{project_id}/decision-cases/'
def payload(**changes):
    return {'title':'ISM sample','criteria':['A','B','C'],'selected_methods':['ism'],'ism_matrix':[[0,1,0],[0,0,1],[0,0,0]],**changes}

@pytest.mark.django_db
def test_finite_incomplete_draft(auth_client,project):
    base=BASE.format(project_id=project.id)
    case=auth_client.post(base,payload(ism_matrix=[[0,None,9],[0,0,0],[0,0,0]]),format='json')
    assert case.status_code==201,case.data
    assert auth_client.get(base+case.data['id']+'/').data['ism_matrix'][0][1] is None
    for value in (float('inf'), float('nan'), 10**400):
        instance=DecisionCase.objects.get(id=case.data['id'])
        with pytest.raises(CodedValidationError):update_case(instance,None,{'ism_matrix':[[value]]})
        instance.refresh_from_db(); assert instance.ism_matrix[0][1] is None

@pytest.mark.django_db
def test_matrix_patch_isolated_from_invalid_ranking(project,user):
    case=DecisionCase.objects.create(project=project,title='draft',criteria=['A'],selected_methods=['ism'],performance_matrix=[[0]],types=['cost'],weights=[1],alternatives=['X'],created_by=user,updated_by=user)
    update_case(case,user,{'ism_matrix':[[None]]})
    case.refresh_from_db();assert case.ism_matrix==[[None]] and case.performance_matrix==[[0]]
    with pytest.raises(CodedValidationError):update_case(case,user,{'criteria':['A','B']})

@pytest.mark.django_db
def test_exact_independent_run_and_frozen_rerun(auth_client,project,user):
    base=BASE.format(project_id=project.id)
    response=auth_client.post(base,payload(ahp_matrix=[[9]],dematel_matrix=[[8]],weights=[4]),format='json')
    assert response.status_code==201,response.data
    case_id=response.data['id'];before=auth_client.get(base+case_id+'/').data
    run=auth_client.post(base+case_id+'/runs/',{'method':'ism'},format='json')
    assert run.status_code==201,run.data
    assert run.data['result']['status']=='ok' and run.data['result']['engine']=='ism'
    assert run.data['result']['reachability_matrix']==[[1,1,1],[0,1,1],[0,0,1]]
    assert run.data['result']['layers']==[{'level':1,'criteria':['C']},{'level':2,'criteria':['B']},{'level':3,'criteria':['A']}]
    assert run.data['result']['mutual_groups']==[]
    assert str(run.data['extracted_by'])==str(user.id)
    assert auth_client.get(base+case_id+'/').data==before
    first=dict(run.data)
    update=auth_client.patch(base+case_id+'/',{'criteria':['D','E','F'],'ism_matrix':[[1,0,0],[0,1,0],[0,0,1]]},format='json')
    assert update.status_code==200,update.data
    rerun=auth_client.post(base+case_id+'/runs/',{'method':'ism'},format='json')
    assert rerun.status_code==201 and rerun.data['id']!=first['id']
    assert auth_client.get(base+case_id+'/runs/'+first['id']+'/').data==first
    assert DecisionRun.objects.filter(case_id=case_id).count()==2

@pytest.mark.django_db
@pytest.mark.parametrize('change',[{'selected_methods':[]},{'criteria':['X'],'ism_matrix':[[1]]},{'is_deleted':True}])
def test_authoritative_reload(project,user,change):
    from decision_support.services.execution_service import create_run
    case=create_case(project.id,user,payload())
    DecisionCase.objects.filter(pk=case.pk).update(**change)
    if 'selected_methods' in change:
        with pytest.raises(CodedValidationError):create_run(case,'ism',user)
        assert not DecisionRun.objects.filter(case=case).exists()
    elif 'is_deleted' in change:
        from django.http import Http404
        with pytest.raises(Http404):create_run(case,'ism',user)
        assert not DecisionRun.objects.filter(case=case).exists()
    else:
        run=create_run(case,'ism',user)
        assert run.input_snapshot['criteria']==['X']
        assert run.result['layers']==[{'level':1,'criteria':['X']}]

@pytest.mark.django_db(transaction=True)
def test_postgres_case_lock_serializes_authoritative_snapshot(project,user):
    import threading,time
    from django.db import connection,close_old_connections,transaction
    from decision_support.services.execution_service import create_run
    case=create_case(project.id,user,payload()); shared={};started=threading.Event()
    def execute():
        close_old_connections()
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_backend_pid()');shared['pid']=cursor.fetchone()[0]
            started.set();shared['run']=create_run(case,'ism',user)
        except BaseException as error:shared['error']=error
        finally:close_old_connections()
    with transaction.atomic():
        locked=DecisionCase.objects.select_for_update().get(pk=case.pk)
        worker=threading.Thread(target=execute);worker.start();assert started.wait(5)
        deadline=time.monotonic()+5;waiting=False
        while time.monotonic()<deadline:
            with connection.cursor() as cursor:
                cursor.execute('SELECT wait_event_type FROM pg_stat_activity WHERE pid=%s',[shared['pid']]);row=cursor.fetchone()
            if row and row[0]=='Lock':waiting=True;break
            if 'run' in shared or 'error' in shared:break
            time.sleep(.01)
        assert waiting,'Expected an actual PostgreSQL lock wait, not elapsed-time inference'
        locked.criteria=['X'];locked.ism_matrix=[[1]];locked.save(update_fields=['criteria','ism_matrix'])
    worker.join(5);assert not worker.is_alive();assert 'error' not in shared,shared.get('error')
    assert shared['run'].input_snapshot['criteria']==['X']
    assert shared['run'].result['layers']==[{'level':1,'criteria':['X']}]

@pytest.mark.django_db
def test_recover_malformed_persisted_ism(project,user):
    case=create_case(project.id,user,payload())
    DecisionCase.objects.filter(pk=case.pk).update(ism_matrix=9)
    case.refresh_from_db()
    update_case(case,user,{'title':'recovered draft'})
    case.refresh_from_db();assert case.ism_matrix==9
    update_case(case,user,{'ism_matrix':[[0,1,0],[0,0,1],[0,0,0]]})
    assert case.ism_matrix[0][1]==1

@pytest.mark.django_db
@pytest.mark.parametrize('matrix,path', [([[0,None,0],[0,0,0],[0,0,0]],'ism_matrix.0.1'), ([[0,True,0],[0,0,0],[0,0,0]],'ism_matrix.0.1'), ([[0,'1',0],[0,0,0],[0,0,0]],'ism_matrix.0.1'), ([[0,.5,0],[0,0,0],[0,0,0]],'ism_matrix.0.1'), ([[]],'ism_matrix'), (4,'ism_matrix')])
def test_invalid_run_appends_nothing(auth_client,project,matrix,path):
    base=BASE.format(project_id=project.id)
    case=auth_client.post(base,payload(ism_matrix=matrix),format='json');assert case.status_code==201,case.data
    run=auth_client.post(base+case.data['id']+'/runs/',{'method':'ism'},format='json')
    assert run.status_code==400,run.data
    assert any(issue['path']==path for issue in run.data['error']['details']['issues'])
    assert not DecisionRun.objects.filter(case_id=case.data['id']).exists()

@pytest.mark.django_db
def test_access_denials_and_foreign_scoping(auth_client,api_client,project,user,other_user,member):
    from projects.services import create_project_with_creator
    base=BASE.format(project_id=project.id)
    case=auth_client.post(base,payload(),format='json');assert case.status_code==201
    detail=base+case.data['id']+'/'
    run=auth_client.post(detail+'runs/',{'method':'ism'},format='json');assert run.status_code==201
    api_client.force_authenticate(other_user)
    assert api_client.get(detail).status_code==200
    assert api_client.get(detail+'runs/'+run.data['id']+'/').status_code==200
    for method,url,data in [('post',base,payload()),('patch',detail,{'ism_matrix':[[1]]}),('post',detail+'runs/',{'method':'ism'})]:
        assert getattr(api_client,method)(url,data,format='json').status_code==403
    foreign=create_project_with_creator(creator=user,project_code='ISM-OTHER',project_name='Foreign',employer='Other',start_date='2026-01-01')
    foreign_base=BASE.format(project_id=foreign.id)
    for suffix in ('',case.data['id']+'/',case.data['id']+'/runs/',case.data['id']+'/runs/'+run.data['id']+'/'):
        assert api_client.get(foreign_base+suffix).status_code in (403,404)
    for method,url,data in [('post',foreign_base,payload()),('patch',foreign_base+case.data['id']+'/',{}),('post',foreign_base+case.data['id']+'/runs/',{'method':'ism'})]:
        assert getattr(api_client,method)(url,data,format='json').status_code in (403,404)
    api_client.force_authenticate(user)
    assert auth_client.get(foreign_base+case.data['id']+'/').status_code==404
    assert auth_client.get(foreign_base+case.data['id']+'/runs/'+run.data['id']+'/').status_code==404
    assert DecisionRun.objects.filter(case_id=case.data['id']).count()==1
    # No-view membership overrides cannot read otherwise allowed resources.
    from master_data.models import ProjectMemberPermissionOverride
    ProjectMemberPermissionOverride.objects.create(member=member,permission_codename='view_decision_support',is_granted=False)
    api_client.force_authenticate(other_user)
    assert api_client.get(detail).status_code==403
    api_client.force_authenticate(None)
    assert api_client.get(detail).status_code==401

@pytest.mark.django_db
def test_localized_binary_error(auth_client,project):
    base=BASE.format(project_id=project.id)
    case=auth_client.post(base,payload(ism_matrix=[[.5,0,0],[0,0,0],[0,0,0]]),format='json')
    response=auth_client.post(base+case.data['id']+'/runs/',{'method':'ism'},format='json',HTTP_ACCEPT_LANGUAGE='fa')
    assert response.status_code==400
    assert 'رابطه' in response.data['error']['details']['issues'][0]['message']

@pytest.mark.django_db
@pytest.mark.parametrize('operation', ['create', 'matrix_patch', 'shared_patch', 'persisted'])
def test_root_json_null_draft_is_preserved_and_recoverable(auth_client, project, operation):
    from django.db.models import JSONField, Value
    base = BASE.format(project_id=project.id)
    if operation == 'create':
        response = auth_client.post(base, payload(ism_matrix=None), format='json')
        assert response.status_code == 201, response.data
        case_id = response.data['id']
    else:
        response = auth_client.post(base, payload(), format='json')
        assert response.status_code == 201, response.data
        case_id = response.data['id']
        if operation == 'persisted':
            DecisionCase.objects.filter(pk=case_id).update(ism_matrix=Value(None, output_field=JSONField()))
            changes = {'title': 'Recovered raw null draft'}
        else:
            changes = {'ism_matrix': None}
            if operation == 'shared_patch':
                changes['title'] = 'Shared null draft'
        response = auth_client.patch(base + case_id + '/', changes, format='json')
        assert response.status_code == 200, response.data
    assert response.data['ism_matrix'] is None
    assert auth_client.get(base + case_id + '/').data['ism_matrix'] is None
    run = auth_client.post(base + case_id + '/runs/', {'method': 'ism'}, format='json')
    assert run.status_code == 400, run.data
    assert any(issue['code'] == 'dimension_invalid' and issue['path'] == 'ism_matrix' for issue in run.data['error']['details']['issues'])
    assert not DecisionRun.objects.filter(case_id=case_id).exists()
    corrected = auth_client.patch(base + case_id + '/', {'ism_matrix': [[0,0,0],[0,0,0],[0,0,0]]}, format='json')
    assert corrected.status_code == 200, corrected.data
    assert auth_client.post(base + case_id + '/runs/', {'method': 'ism'}, format='json').status_code == 201
    assert DecisionRun.objects.filter(case_id=case_id).count() == 1

@pytest.mark.django_db
def test_ahp_execution_retains_root_null_ism_draft_in_snapshot(auth_client, project):
    base = BASE.format(project_id=project.id)
    case = auth_client.post(base, payload(criteria=['A'], selected_methods=['ahp', 'ism'], ahp_matrix=[[1]], ism_matrix=None), format='json')
    assert case.status_code == 201, case.data
    run = auth_client.post(base + case.data['id'] + '/runs/', {'method': 'ahp'}, format='json')
    assert run.status_code == 201, run.data
    assert run.data['input_snapshot']['ism_matrix'] is None
    assert auth_client.get(base + case.data['id'] + '/').data['ism_matrix'] is None
