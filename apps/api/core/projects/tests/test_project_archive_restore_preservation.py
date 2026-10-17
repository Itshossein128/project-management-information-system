"""Persistence faults are tested against the real transaction and response middleware."""
import pytest
from django.db import IntegrityError
from audit.models import AuditLog
from projects.models import ProjectArchiveRestore
from .archive_restore_helpers import actor, archived_project, base, client_for, state
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db


@pytest.mark.parametrize('async_audit',[False,True])
@pytest.mark.parametrize('failure',['audit','receipt'])
def test_required_persistence_failure_rolls_everything_back(settings,monkeypatch,async_audit,failure):
    from audit import service
    settings.AUDIT_LOG_ASYNC=async_audit
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p));before=state(p)
    def fail(*args,**kwargs):raise IntegrityError('injected required persistence failure')
    if failure=='audit':monkeypatch.setattr(service,'persist_audit_log',fail)
    else:monkeypatch.setattr(ProjectArchiveRestore.objects,'create',fail)
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==503 and r.json()['error']['code']=='restore_not_applied'
    assert state(p)==before
    assert not ProjectArchiveRestore.objects.filter(project=p).exists()
    assert not AuditLog.objects.filter(project=p).exists()


def test_restore_and_replay_never_use_async_audit_or_approval(settings,monkeypatch):
    from audit import service
    from projects import lifecycle_service as life
    settings.AUDIT_LOG_ASYNC=True
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    calls=[]
    def forbidden(*args,**kwargs):
        calls.append((args,kwargs))
        raise AssertionError('restore must not rerun approval or asynchronous audit')
    monkeypatch.setattr(service,'record_audit_log',forbidden)
    from audit import middleware
    monkeypatch.setattr(middleware,'record_audit_log',forbidden)
    monkeypatch.setattr(life,'approve',forbidden)
    for expected in ['restored','replayed']:
        response=c.post(base(p)+'restore/',payload,format='json')
        assert response.status_code==200 and response.json()['outcome']==expected
    assert calls==[]
    assert AuditLog.objects.filter(project=p).count()==1
    assert ProjectArchiveRestore.objects.filter(project=p).count()==1


@pytest.mark.parametrize('origin',['active','suspended','completed'])
def test_all_business_data_and_prior_history_survive_restore_and_replay(monkeypatch,origin):
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
    if origin=='suspended':p=life.suspend(p,u)
    elif origin=='completed':p=life.complete(p,u)
    p=life.archive(p,u)
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
    c=client_for(u);payload=body(confirmation(c,p))
    for outcome in ('restored','replayed'):
        response=c.post(base(p)+'restore/',payload,format='json')
        assert response.status_code==200 and response.json()['outcome']==outcome
        assert business_snapshot(records)==before
        assert [type(row)._base_manager.count() for row in records[:-1]]==counts
        assert list(records[0].restricted_to.values_list('pk',flat=True))==restricted
    after=state(p)
    for key,value in root.items():
        if key not in ('status','lifecycle_version','updated_at'):assert after[key]==value,key
    assert after['status']==origin
    assert AuditLog.objects.filter(project=p).count()==prior_audit_count+1
    assert ProjectArchiveRestore.objects.filter(project=p).count()==1
