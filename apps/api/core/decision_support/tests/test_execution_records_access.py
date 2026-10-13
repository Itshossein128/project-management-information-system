import pytest
from rest_framework.test import APIClient
from master_data.models import ProjectMemberPermissionOverride
from projects.services import create_project_with_creator
from decision_support.models import DecisionRun
from decision_support.services.case_service import create_case
from decision_support.services.execution_service import create_run
from decision_support.tests.execution_records_fixtures import payload

@pytest.mark.django_db
def test_real_access_nested_scope_immutable_and_revocation(project,user,other_user,member,auth_client,api_client):
    case=create_case(project.id,user,payload());run=create_run(case,'saw',user)
    base=f'/api/v1/projects/{project.id}/decision-cases/';detail=base+str(case.id)+'/'
    urls=[base,detail,detail+'runs/',detail+'runs/'+str(run.id)+'/']
    api_client=APIClient()
    before=DecisionRun.objects.filter(pk=run.id).values().get()
    api_client.force_authenticate(other_user)
    for url in urls:assert api_client.get(url).status_code==200
    for verb,url,data in [('post',base,payload()),('patch',detail,{'title':'Denied'}),('delete',detail,{}),('post',detail+'runs/',{'method':'saw'})]:assert getattr(api_client,verb)(url,data,format='json').status_code==403
    auth_client.force_authenticate(user)
    for verb in ('put','patch','delete'):assert getattr(auth_client,verb)(urls[-1],{},format='json').status_code==400
    foreign=create_project_with_creator(creator=user,project_code='RECORDS-FOREIGN',project_name='Foreign',employer='Other',start_date='2026-01-01')
    fbase=f'/api/v1/projects/{foreign.id}/decision-cases/'
    for suffix in [str(case.id)+'/',str(case.id)+'/runs/',str(case.id)+'/runs/'+str(run.id)+'/']:
        assert auth_client.get(fbase+suffix).status_code==404
        assert api_client.get(fbase+suffix).status_code in (403,404)
    # Corrupt run project cannot escape nested double scoping.
    DecisionRun.objects.filter(pk=run.id).update(project=foreign)
    assert auth_client.get(urls[-1]).status_code==404
    assert auth_client.get(detail+'runs/').data['count']==0
    DecisionRun.objects.filter(pk=run.id).update(project=project)
    ProjectMemberPermissionOverride.objects.create(member=member,permission_codename='view_decision_support',is_granted=False)
    for url in urls:assert api_client.get(url).status_code==403
    api_client.force_authenticate(None)
    for url in urls:assert api_client.get(url).status_code==401
    # Authenticated nonmember.
    outsider=type(user).objects.create_user(username='outsider-records',mobile='+989121230009',password='localtest')
    api_client.force_authenticate(outsider)
    for url in urls:assert api_client.get(url).status_code==403
    assert DecisionRun.objects.filter(pk=run.id).values().get()==before
