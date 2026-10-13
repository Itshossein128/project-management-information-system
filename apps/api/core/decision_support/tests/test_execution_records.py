import copy
import pytest
from django.http import Http404
from config.exceptions import CodedValidationError
from decision_support.models import DecisionCase, DecisionRun
from decision_support.services.case_service import create_case, update_case
from decision_support.services.execution_service import create_run
from decision_support.tests.execution_records_fixtures import payload, METHODS, TIME, IDS

@pytest.mark.django_db
@pytest.mark.parametrize('method', METHODS)
@pytest.mark.parametrize('change', ['input', 'selection', 'deleted'])
def test_authoritative_record(project, user, method, change):
    case=create_case(project.id,user,payload())
    if change=='input':
        DecisionCase.objects.filter(pk=case.pk).update(criteria=['New cost','New quality'],weights=[3,2])
        run=create_run(case,method,user)
        assert run.input_snapshot['criteria']==['New cost','New quality']
        assert run.input_snapshot['weights']==[3,2]
        assert run.project_id==project.id and run.extracted_by_id==user.id
        assert run.result['status']==('stub' if method=='dematel' else 'ok')
    else:
        DecisionCase.objects.filter(pk=case.pk).update(**({'selected_methods':[]} if change=='selection' else {'is_deleted':True}))
        with pytest.raises(CodedValidationError if change=='selection' else Http404):create_run(case,method,user)
        assert not DecisionRun.objects.filter(case=case).exists()

@pytest.mark.django_db
def test_fixed_history_order_and_scoped_pagination(auth_client,project,user):
    case=create_case(project.id,user,payload())
    for i,uid in enumerate(IDS):
        DecisionRun.objects.create(id=uid,case=case,project=project,method=METHODS[i%5],input_snapshot={},result={},extracted_at=TIME,extracted_by=user)
    url=f'/api/v1/projects/{project.id}/decision-cases/{case.id}/runs/'
    collected=[]
    for page in (1,2,3):
        r=auth_client.get(url,{'page':page,'page_size':10});assert r.status_code==200
        assert r.data['count']==25;collected.extend(x['id'] for x in r.data['results'])
    assert collected==list(reversed(IDS))
    for method in METHODS:
        r=auth_client.get(url,{'method':method,'page_size':10});assert r.data['count']==5
        assert all(x['method']==method for x in r.data['results'])
    assert auth_client.get(url,{'method':'unknown'}).status_code==400
    assert auth_client.get(url,{'page':99}).status_code==404

@pytest.mark.django_db
def test_independent_disagreement_ties_and_deselection(project,user,auth_client):
    case=create_case(project.id,user,payload(types=['benefit','benefit'],weights=[1,1],performance_matrix=[[1,3],[1,3],[3,1]],alternatives=['Alpha','Beta','Gamma']))
    before=copy.deepcopy(DecisionCase.objects.filter(pk=case.pk).values().get())
    saw=create_run(case,'saw',user);topsis=create_run(case,'topsis',user)
    assert saw.result['ranking'][0]['option']=='Alpha'
    assert topsis.result['ranking'][0]['option']=='Gamma'
    assert saw.result['ranking']!=topsis.result['ranking']
    assert DecisionCase.objects.filter(pk=case.pk).values().get()==before
    tied=create_case(project.id,user,payload(types=['benefit','benefit'],weights=[1,1],performance_matrix=[[1,1],[1,1]]))
    for method in ('saw','topsis'):
        result=create_run(tied,method,user).result['ranking']
        assert [(r['option'],r['rank']) for r in result]==[('Alpha',1),('Beta',2)]
    update_case(case,user,{'selected_methods':[]})
    url=f'/api/v1/projects/{project.id}/decision-cases/{case.id}/runs/'
    assert auth_client.get(url,{'method':'saw'}).data['count']==1
    assert auth_client.get(url+str(saw.id)+'/').data['result']==saw.result
