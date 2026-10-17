"""Actual independent PostgreSQL connections and observed row-lock waits."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Event, current_thread
import time
import pytest
from django.db import connections,close_old_connections,transaction
from projects.tests.status_undo_helpers import *
from projects.models import Project,ProjectStatusUndo
from projects import status_undo_service as service, change_request_service as crs
from audit.models import AuditLog
pytestmark=pytest.mark.django_db(transaction=True,serialized_rollback=True)

@pytest.mark.parametrize('operation',['resume','undo_completion'])
@pytest.mark.parametrize('different_request,different_actor',[(False,False),(True,False),(False,True),(True,True)])
def test_parallel_requests_commit_one_success(operation,different_request,different_actor):
    user=actor(admin=True);other=actor(admin=True) if different_actor else user;p=source_project(user,operation)
    first=confirmed_body(client_for(user),p,operation);second=confirmed_body(client_for(other),p,operation)
    second['request_id']=str(uuid4()) if different_request else first['request_id']
    if not different_actor:second['confirmation_token']=first['confirmation_token']
    barrier=Barrier(3)
    def send(who,body):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            return client_for(who).post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),body,format='json')
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(send,user,first);b=pool.submit(send,other,second);barrier.wait(timeout=10);results=[a.result(timeout=15),b.result(timeout=15)]
    assert sorted(r.status_code for r in results)==([200,200] if not different_actor and not different_request else [200,409])
    assert ProjectStatusUndo.objects.filter(project=p).count()==1
    assert AuditLog.objects.filter(project=p,changes__event__in=['project.resumed','project.completion_undone']).count()==1

@pytest.mark.parametrize('operation',['resume','undo_completion'])
@pytest.mark.parametrize('writer',['name','manager','archive','complete','suspend','cr','delete'])
@pytest.mark.parametrize('first',['undo','writer'])
def test_project_writers_serialize_with_both_root_lock_orders(monkeypatch,operation,writer,first):
    user=actor(superuser=True);p=ready_project(user)
    cr=None
    if writer=='bound_cr':
        p=lifecycle.complete(p,user);p.scope_description='';p.save(update_fields=['scope_description'])
    if writer in ('cr','bound_cr'):
        cr=crs.create_change_request(project=p,user=user,reason='Existing scope correction',proposed_changes={'scope_description':'Approved independent scope'})
        cr=crs.submit_change_request(cr,user)
    if writer!='bound_cr':p=lifecycle.suspend(p,user) if operation=='resume' else lifecycle.complete(p,user)
    body=confirmed_body(client_for(user),p,operation)
    restore_body=None
    if writer=='restore':
        assert service.undo(p,user,operation,**body)['outcome']=='applied'
        p.refresh_from_db();p=lifecycle.archive(p,user);v=lifecycle.restore_preview(p,user)
        restore_body={'request_id':str(uuid4()),'confirmation_token':v['confirmation_token'],'reason':'Restore same known archive'}
    budget=(p.budget_approved_at,p.budget_approved_by_id)
    locked,entered,release=Event(),Event(),Event();pids={};original=lifecycle.lock_project
    def controlled(project):
        name='first' if current_thread().name.startswith('first') else 'second'
        pids[name]=connections['default'].connection.info.backend_pid
        if name=='second':entered.set()
        row=original(project)
        if name=='first':locked.set();assert release.wait(15)
        return row
    monkeypatch.setattr(service,'lock_project',controlled);monkeypatch.setattr(lifecycle,'lock_project',controlled);monkeypatch.setattr(crs,'lock_project',controlled)
    def send(action):
        close_old_connections()
        try:
            c=client_for(user)
            if action=='undo':return c.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),body,format='json').status_code
            if writer=='name':return c.patch(base(p),{'project_name':'Independent rename'},format='json').status_code
            if writer=='manager':return c.patch(base(p),{'project_manager':None},format='json').status_code
            if writer=='delete':return c.delete(base(p)).status_code
            if writer=='restore':return c.post(base(p)+'restore/',restore_body,format='json').status_code
            if writer in ('cr','bound_cr'):return c.post(base(p)+f'change-requests/{cr.pk}/approve/').status_code
            return c.post(base(p)+writer+'/').status_code
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=1,thread_name_prefix='first') as a,ThreadPoolExecutor(max_workers=1,thread_name_prefix='second') as b:
        one=a.submit(send,first)
        try:
            assert locked.wait(15);two=b.submit(send,'writer' if first=='undo' else 'undo');assert entered.wait(15)
            deadline=time.monotonic()+5;waiting=False
            while time.monotonic()<deadline:
                with connections['default'].cursor() as cursor:
                    cursor.execute('SELECT wait_event_type FROM pg_stat_activity WHERE pid=%s',[pids['second']]);row=cursor.fetchone()
                if row and row[0]=='Lock':waiting=True;break
                time.sleep(.02)
            assert waiting,'PostgreSQL never reported the second root writer waiting'
        finally:release.set()
        codes=[one.result(timeout=20),two.result(timeout=20)]
    undo_code,writer_code=codes if first=='undo' else codes[::-1]
    if writer=='delete':
        assert writer_code==204 and undo_code==(200 if first=='undo' else 404)
        assert not Project.objects.filter(pk=p.pk).exists()
        if first=='undo':assert AuditLog.objects.filter(resource_id=p.pk,changes__event__in=['project.resumed','project.completion_undone']).count()==1
        return
    p.refresh_from_db();assert (p.budget_approved_at,p.budget_approved_by_id)==budget
    if writer=='bound_cr':
        assert writer_code==200 and undo_code==(400 if first=='undo' else 409)
        assert p.status=='completed' and not p.status_undos.exists()
        cr.refresh_from_db();assert cr.status=='approved'
        return
    if writer=='restore':
        assert undo_code==writer_code==200 and p.status=='active' and p.status_undos.count()==1
        return
    if first=='undo':assert undo_code==200 and writer_code==200
    elif writer in ('name','manager','archive','cr') or writer=='complete' and operation=='resume':assert undo_code==409 and writer_code==200
    else:assert undo_code==200 and writer_code==400
    assert ProjectStatusUndo.objects.filter(project=p).count()==(undo_code==200)

@pytest.mark.parametrize('operation',['resume','undo_completion'])
def test_authority_revoked_while_waiting_is_rechecked(monkeypatch,operation):
    user=actor(admin=True);p=source_project(user,operation);body=confirmed_body(client_for(user),p,operation)
    entered,release=Event(),Event();original=service.lock_project
    def blocked(project):entered.set();assert release.wait(10);return original(project)
    monkeypatch.setattr(service,'lock_project',blocked)
    def send():
        close_old_connections()
        try:return client_for(user).post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),body,format='json').status_code
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=1) as pool:
        pending=pool.submit(send)
        try:assert entered.wait(10);user.groups.clear()
        finally:release.set()
        assert pending.result(timeout=15)==403
    assert not p.status_undos.exists()


@pytest.mark.parametrize('first',['undo','writer'])
def test_completion_bound_approval_contends_with_old_undo_context(monkeypatch,first):
    test_project_writers_serialize_with_both_root_lock_orders(monkeypatch,'undo_completion','bound_cr',first)

@pytest.mark.parametrize('operation',['resume','undo_completion'])
@pytest.mark.parametrize('first',['undo','writer'])
def test_archive_restore_contends_with_read_only_historical_replay(monkeypatch,operation,first):
    test_project_writers_serialize_with_both_root_lock_orders(monkeypatch,operation,'restore',first)
