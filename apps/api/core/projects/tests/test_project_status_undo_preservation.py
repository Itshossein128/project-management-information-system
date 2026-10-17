import pytest
from django.db import IntegrityError
from projects.tests.status_undo_helpers import *
from projects.models import ProjectStatusUndo
from audit.models import AuditLog
pytestmark=pytest.mark.django_db

@pytest.mark.parametrize('operation,origin',[('resume','active'),('undo_completion','active'),('undo_completion','suspended')])
@pytest.mark.parametrize('async_audit',[False,True])
@pytest.mark.parametrize('failure',['audit','receipt'])
def test_required_undo_persistence_failure_rolls_back_everything(monkeypatch,settings,operation,origin,async_audit,failure):
    from audit import service
    user=actor(admin=True);p=source_project(user,operation,origin);c=client_for(user);body=confirmed_body(c,p,operation);before=state(p);logs=list(AuditLog.objects.filter(project=p).order_by('id').values())
    settings.AUDIT_LOG_ASYNC=async_audit
    def fail(*args,**kwargs):raise IntegrityError('injected required persistence failure')
    monkeypatch.setattr(service if failure=='audit' else ProjectStatusUndo.objects,'persist_audit_log' if failure=='audit' else 'create',fail)
    response=c.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),body,format='json')
    assert response.status_code==503 and response.data['error']['code']=='status_undo_not_applied'
    assert state(p)==before and not p.status_undos.exists() and list(AuditLog.objects.filter(project=p).order_by('id').values())==logs


@pytest.mark.parametrize('operation,origin',[('resume','active'),('undo_completion','active'),('undo_completion','suspended')])
def test_populated_business_data_survives_undo_and_replay(monkeypatch,operation,origin):
    from .archive_restore_helpers import populate_business_records,business_snapshot
    from projects import lifecycle_service as life, change_request_service
    from contracts import collection_service
    from contracts.services import ipc_service
    from cost_control import cbs_services
    from schedule.services import baseline_service
    from events.publisher import EventPublisher
    from schedule.models import BaselineSchedule
    from .archive_restore_helpers import ready_project
    u=actor(admin=True);p=ready_project(u);records=populate_business_records(p,u)
    if operation=='resume' or origin=='suspended':p=life.suspend(p,u)
    if operation=='undo_completion':p=life.complete(p,u)
    c=client_for(u)
    assert c.patch(base(p),{'project_name':'Independent newer name','contractor':'New contractor'},format='json').status_code==200
    p.refresh_from_db()
    before=business_snapshot(records);root=state(p);prior_audit_count=AuditLog.objects.filter(project=p).count()
    counts=[type(row)._base_manager.count() for row in records[:-1]]
    restricted=list(records[0].restricted_to.values_list('pk',flat=True))
    def forbidden(*args,**kwargs):raise AssertionError('restore replayed a money, approval or baseline operation')
    monkeypatch.setattr(life,'approve',forbidden)
    monkeypatch.setattr(change_request_service,'approve_change_request',forbidden)
    monkeypatch.setattr(collection_service,'add_collection',forbidden)
    monkeypatch.setattr(ipc_service,'pay_ipc',forbidden)
    monkeypatch.setattr(cbs_services,'create_payment',forbidden)
    monkeypatch.setattr(cbs_services,'approve_commitment',forbidden)
    monkeypatch.setattr(baseline_service,'approve_lock_baseline',forbidden)
    monkeypatch.setattr(baseline_service,'create_baseline_snapshot',forbidden)
    monkeypatch.setattr(BaselineSchedule,'save',forbidden)
    monkeypatch.setattr(EventPublisher,'publish',forbidden)
    c=client_for(u);payload=confirmed_body(c,p,operation)
    for outcome in ('applied','replayed'):
        response=c.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),payload,format='json')
        assert response.status_code==200 and response.json()['outcome']==outcome
        assert business_snapshot(records)==before
        assert [type(row)._base_manager.count() for row in records[:-1]]==counts
        assert list(records[0].restricted_to.values_list('pk',flat=True))==restricted
    after=state(p)
    for key,value in root.items():
        if key not in ('status','lifecycle_version','updated_at'):assert after[key]==value,key
    assert after['status']==('suspended' if operation=='undo_completion' and origin=='suspended' else 'active')
    assert AuditLog.objects.filter(project=p).count()==prior_audit_count+1
    assert ProjectStatusUndo.objects.filter(project=p).count()==1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('operation,origin,target',[('resume','active','active'),('undo_completion','active','active'),('undo_completion','suspended','suspended')])
def test_lost_database_commit_acknowledgment_recovers_committed_result(monkeypatch,operation,origin,target):
    from django.db import connection,OperationalError
    from projects import status_undo_service as undo
    user=actor(admin=True);p=source_project(user,operation,origin);c=client_for(user)
    c.raise_request_exception=False
    body=confirmed_body(c,p,operation);route=base(p)+('resume/' if operation=='resume' else 'undo-completion/')
    original=p.suspension_event if operation=='resume' else p.completion_event
    original_payload=dict(original.changes)
    actual_commit=connection._commit;committed=[]
    def commit_then_lose_ack():
        actual_commit()
        committed.append(True)
        raise OperationalError('Injected lost acknowledgment after actual PostgreSQL commit')
    with monkeypatch.context() as patch:
        patch.setattr(connection,'_commit',commit_then_lose_ack)
        response=c.post(route,body,format='json')
    assert committed==[True]
    assert response.status_code==500  # Unknown outcome, never the known-rollback 503.
    p.refresh_from_db();assert p.status==target
    receipt=ProjectStatusUndo.objects.get(project=p);public=undo.receipt_data(receipt)
    assert str(receipt.request_id)==body['request_id']
    event='project.resumed' if operation=='resume' else 'project.completion_undone'
    assert AuditLog.objects.filter(project=p,changes__event=event).count()==1
    original.refresh_from_db();assert original.changes==original_payload
    lookup=base(p)+f"status-undo-attempts/{operation}/{body['request_id']}/"
    recovered=c.get(lookup);assert recovered.status_code==200
    assert recovered.data['outcome']=='completed' and recovered.data['receipt']==public
    assert recovered.data['current_project']['status']==target
    # An independent later occurrence must survive recovery of the uncertain one.
    getattr(lifecycle,'suspend' if operation=='resume' else 'complete')(p,user)
    later=state(p);audits=list(AuditLog.objects.filter(project=p).order_by('id').values())
    replay=c.post(route,body,format='json');assert replay.status_code==200
    assert replay.data['outcome']=='replayed' and replay.data['receipt']==public
    assert replay.data['current_project']['status']==later['status']
    assert c.post(route,{**body,'request_id':str(uuid4())},format='json').status_code==409
    assert state(p)==later and ProjectStatusUndo.objects.filter(project=p).count()==1
    assert list(AuditLog.objects.filter(project=p).order_by('id').values())==audits
