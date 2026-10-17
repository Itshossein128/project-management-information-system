from unittest.mock import patch
import pytest
from django.test import override_settings
from projects.tests.status_undo_helpers import *
from audit.models import AuditLog

pytestmark = pytest.mark.django_db

@pytest.mark.parametrize('origin', ['active','suspended'])
def test_original_event_captures_exact_source_and_association(origin):
    user=actor(admin=True); project=ready_project(user)
    if origin=='suspended':
        project=lifecycle.suspend(project,user)
        event=AuditLog.objects.filter(project=project,changes__event='project.suspended').get()
        assert str(project.suspension_event_id)==str(event.pk)
    before=project.lifecycle_version
    project=lifecycle.complete(project,user)
    event=AuditLog.objects.filter(project=project,changes__event='project.completed').get()
    assert str(project.completion_event_id)==str(event.pk)
    assert project.completed_from_status==origin
    assert event.changes['from_status']==origin
    assert event.changes['version_before']==before
    assert event.changes['version_after']==before+1
    assert event.changes['actor']['id']==str(user.pk)
    assert event.changes['suspension_event_id']==(str(project.suspension_event_id) if origin=='suspended' else None)

@pytest.mark.parametrize('async_audit',[False,True])
@pytest.mark.parametrize('action',['suspend','complete'])
def test_required_original_audit_failure_rolls_back(async_audit,action):
    user=actor(admin=True);project=ready_project(user);before=state(project)
    with override_settings(AUDIT_LOG_ASYNC=async_audit), patch('audit.service.persist_audit_log',side_effect=RuntimeError('required audit failed')):
        with pytest.raises(RuntimeError): getattr(lifecycle,action)(project,user)
    assert state(project)==before
    assert not AuditLog.objects.filter(project=project,changes__event__in=['project.suspended','project.completed']).exists()

@pytest.mark.parametrize('field',['restore_completion_event','restore_completion_event_id','restore_archive_cycle_id'])
def test_cr_binding_cannot_be_supplied_to_existing_write_route(field):
    user=actor(admin=True);p=ready_project(user);client=client_for(user)
    before=state(p)
    response=client.post(base(p)+'change-requests/',{'reason':'Correction request reason','proposed_changes':{'scope_description':'Changed scope'},field:None},format='json')
    assert response.status_code==400,response.data
    assert not p.change_requests.exists() and state(p)==before

@pytest.mark.parametrize('operation,origin,target',[('resume','active','active'),('undo_completion','active','active'),('undo_completion','suspended','suspended')])
def test_confirmed_targets_replay_and_source_immutable(operation,origin,target):
    user=actor(admin=True);client=client_for(user);p=source_project(user,operation,origin)
    view=preview(client,p,operation);assert view.status_code==200
    assert view.data['to_status']==target
    body=confirmed_body(client,p,operation,'  Mistaken decision  ')
    original=AuditLog.objects.filter(project=p).order_by('id').values('id','changes','created_at');snap=list(original)
    route='resume/' if operation=='resume' else 'undo-completion/'
    response=client.post(base(p)+route,body,format='json')
    assert response.status_code==200,response.data
    result=response.data;assert result['outcome']=='applied' and result['current_project']['status']==target
    assert result['receipt']['reason']=='Mistaken decision'
    assert result['receipt']['source_event']['kind']==('suspend' if operation=='resume' else 'complete')
    duplicate=client.post(base(p)+route,body,format='json')
    assert duplicate.status_code==200 and duplicate.data['outcome']=='replayed'
    assert duplicate.data['receipt']==result['receipt']
    assert list(AuditLog.objects.filter(id__in=[r['id'] for r in snap]).order_by('id').values('id','changes','created_at'))==snap
    p.refresh_from_db()
    if target=='suspended':
        suspension=p.suspension_event_id
        resumed=client.post(base(p)+'resume/',confirmed_body(client,p),format='json')
        assert resumed.status_code==200 and resumed.data['current_project']['status']=='active'
        p.refresh_from_db();assert p.suspension_event_id==suspension

@pytest.mark.parametrize('extra',[{}, {'reason':' '}, {'reason':'Mistake','to_status':'active'}, {'request_id':'bad','confirmation_token':'bad','reason':'Mistake'}])
def test_reasonless_or_forged_existing_resume_rejected(extra):
    user=actor(admin=True);client=client_for(user);p=source_project(user);before=state(p)
    response=client.post(base(p)+'resume/',extra,format='json')
    assert response.status_code==400,response.data
    assert state(p)==before

@pytest.mark.parametrize('field',['suspension_event','suspension_event_id','completion_event','completion_event_id','completed_from_status','restore_completion_event','restore_completion_event_id'])
def test_metadata_is_not_client_input(field):
    user=actor(admin=True);client=client_for(user);p=ready_project(user)
    response=client.patch(base(p),{field:None},format='json')
    assert response.status_code==400


def test_resume_direct_service_requires_confirmation():
    user=actor(admin=True);p=source_project(user)
    with pytest.raises(TypeError):lifecycle.resume(p,user)


def test_source_references_survive_archive_and_separate_cycles():
    user=actor(admin=True);client=client_for(user);p=source_project(user,'undo_completion','suspended')
    before=(p.suspension_event_id,p.completion_event_id,p.completed_from_status)
    p=lifecycle.archive(p,user)
    v=lifecycle.restore_preview(p,user)
    lifecycle.restore(p,user,request_id=uuid4(),confirmation_token=v['confirmation_token'],reason='Mistaken archive')
    p.refresh_from_db();assert (p.suspension_event_id,p.completion_event_id,p.completed_from_status)==before
    result=client.post(base(p)+'undo-completion/',confirmed_body(client,p,'undo_completion'),format='json')
    assert result.status_code==200 and result.data['current_project']['status']=='suspended'
    p=lifecycle.complete(p,user)
    assert p.completed_from_status=='suspended' and p.completion_event_id!=before[1] and p.suspension_event_id==before[0]


def test_one_character_reason_is_valid_without_change_request_minimum():
    user=actor(admin=True);p=source_project(user);c=client_for(user)
    response=c.post(base(p)+'resume/',confirmed_body(c,p,reason='x'),format='json')
    assert response.status_code==200 and response.data['receipt']['reason']=='x'

@pytest.mark.parametrize('action',['suspend','complete'])
@pytest.mark.parametrize('language',['fa','en'])
def test_original_save_failure_has_localized_known_rollback_and_no_new_event(action,language,monkeypatch):
    from django.db import IntegrityError
    from projects.models import Project
    user=actor(admin=True);p=ready_project(user);before=state(p);c=client_for(user)
    def fail(*args,**kwargs):raise IntegrityError('Injected root save failure')
    monkeypatch.setattr(Project,'save',fail)
    response=c.post(base(p)+action+'/',HTTP_ACCEPT_LANGUAGE=language)
    assert response.status_code==503 and response.data['error']['code']=='lifecycle_not_applied'
    assert any('\u0600'<=ch<='\u06ff' for ch in response.data['error']['message'])==(language=='fa')
    assert state(p)==before and not AuditLog.objects.filter(project=p).exists()
