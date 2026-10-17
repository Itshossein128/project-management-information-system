from unittest.mock import patch
from django.core import signing
import pytest
from projects.tests.status_undo_helpers import *
from projects.models import ProjectStatusUndo,Project
from projects import status_undo_service as service
from audit.models import AuditLog
pytestmark=pytest.mark.django_db

def post(c,p,operation,body):return c.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),body,format='json')

@pytest.mark.parametrize('operation',['resume','undo_completion'])
@pytest.mark.parametrize('later',['suspend','complete','archive'])
def test_old_exact_result_precedes_current_state_but_new_request_cannot_apply(operation,later):
    user=actor(admin=True);p=source_project(user,operation);c=client_for(user);body=confirmed_body(c,p,operation)
    original=post(c,p,operation,body);assert original.status_code==200
    p.refresh_from_db();getattr(lifecycle,later)(p,user)
    before=state(p);audits=list(AuditLog.objects.filter(project=p).order_by('id').values());receipts=list(p.status_undos.values())
    repeated=post(c,p,operation,body);assert repeated.status_code==200 and repeated.data['outcome']=='replayed'
    assert repeated.data['receipt']==original.data['receipt'] and repeated.data['current_project']['status']==before['status']
    assert state(p)==before and list(p.status_undos.values())==receipts
    assert list(AuditLog.objects.filter(project=p).order_by('id').values())==audits
    assert post(c,p,operation,{**body,'request_id':str(uuid4())}).status_code==409
    assert post(c,p,operation,{**body,'reason':'Different reason'}).data['error']['code']=='status_undo_request_conflict'

@pytest.mark.parametrize('operation',['resume','undo_completion'])
def test_owned_lookup_recovers_real_commit_privately_under_current_authority(operation):
    user=actor(admin=True);other=actor(admin=True);p=source_project(user,operation);c=client_for(user);body=confirmed_body(c,p,operation)
    actual=post(c,p,operation,body);assert actual.status_code==200 and ProjectStatusUndo.objects.filter(project=p,request_id=body['request_id']).exists()
    p.refresh_from_db();lifecycle.archive(p,user)
    url=base(p)+f"status-undo-attempts/{operation}/{body['request_id']}/"
    result=c.get(url);assert result.status_code==200,result.data
    assert result.data['outcome']=='completed' and result.data['receipt']==actual.data['receipt'] and result.data['current_project']['status']=='archived'
    assert result['Cache-Control']=='no-store'
    private=client_for(other).get(url);assert private.data['outcome']=='not_recorded' and private.data['receipt'] is None
    absent=c.get(base(p)+f'status-undo-attempts/{operation}/{uuid4()}/');assert absent.data['outcome']=='not_recorded'
    user.groups.clear();assert c.get(url).status_code==403


def test_canonical_decoded_context_has_no_clock_cutoff_and_no_cross_scope():
    user=actor(admin=True);p=source_project(user);c=client_for(user);body=confirmed_body(c,p)
    ctx=signing.loads(body['confirmation_token'],salt=service.SALT)
    with patch('django.core.signing.time.time',return_value=1000):alternate=signing.dumps(ctx,salt=service.SALT)
    first=post(c,p,'resume',{**body,'confirmation_token':alternate});assert first.status_code==200
    assert post(c,p,'resume',body).data['receipt']==first.data['receipt']
    other=actor(admin=True);assert post(client_for(other),p,'resume',body).status_code==403
    foreign=source_project(user);assert post(c,foreign,'resume',body).status_code==403
    assert post(c,p,'undo_completion',body).status_code==403
    user.groups.clear();assert post(c,p,'resume',body).status_code==403

@pytest.mark.parametrize('corruption',['foreign','kind','version','association'])
def test_invalid_original_audit_cannot_be_used(corruption):
    user=actor(admin=True);p=source_project(user,'undo_completion','suspended');c=client_for(user);body=confirmed_body(c,p,'undo_completion')
    if corruption=='foreign':
        other=source_project(user,'undo_completion');Project.objects.filter(pk=p.pk).update(completion_event_id=other.completion_event_id)
    else:
        audit=p.completion_event;data=dict(audit.changes)
        if corruption=='kind':data['event']='project.restored_from_archive'
        if corruption=='version':data['version_after']=False
        if corruption=='association':data['suspension_event_id']=str(uuid4())
        audit.changes=data;audit.save(update_fields=['changes'])
    before=state(p);r=post(c,p,'undo_completion',body)
    assert r.status_code==409 and state(p)==before and not p.status_undos.exists()
