"""Use real independent PostgreSQL transactions, never sequential HTTP substitutes."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import pytest
from django.db import close_old_connections, connections
from config.exceptions import CodedValidationError
from projects import lifecycle_service as life
from projects.models import Project
from .archive_restore_helpers import actor, ready_project

pytestmark = pytest.mark.django_db(transaction=True, serialized_rollback=True)


def consumed_resume_context(project,user):
    """Real signed old occurrence; late new request must never undo another state."""
    from uuid import uuid4
    from projects import status_undo_service as undo_service
    project=life.suspend(project,user)
    preview=undo_service.preview(project,user,'resume')
    body={'request_id':str(uuid4()),'confirmation_token':preview['confirmation_token'],'reason':'Correct mistaken suspension'}
    life.resume(project,user,**body)
    body['request_id']=str(uuid4())
    project.refresh_from_db()
    return project,body


def test_stale_lifecycle_cannot_overwrite_archive():
    user = actor(admin=True)
    project = ready_project(user)
    loaded, proceed = Event(), Event()

    def stale_complete():
        close_old_connections()
        try:
            stale = Project.objects.get(pk=project.pk)
            loaded.set()
            assert proceed.wait(10)
            try:
                life.complete(stale, user)
            except CodedValidationError:
                return 'rejected'
            return 'overwritten'
        finally:
            connections.close_all()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(stale_complete)
        assert loaded.wait(10)
        life.archive(project, user)
        proceed.set()
        assert future.result(timeout=10) == 'rejected'
    assert Project.objects.get(pk=project.pk).status == 'archived'


def test_stale_patch_preserves_archive_metadata():
    from projects.serializers import ProjectUpdateSerializer
    user = actor(admin=True)
    project = ready_project(user)
    stale = Project.objects.get(pk=project.pk)
    archived = life.archive(project, user)
    serializer = ProjectUpdateSerializer(stale, data={'project_name': 'Corrected name'}, partial=True)
    assert serializer.is_valid(), serializer.errors
    saved = serializer.save()
    assert saved.status == 'archived'
    assert saved.archive_cycle_id == archived.archive_cycle_id
    assert saved.archived_from_status == 'active'
    assert saved.lifecycle_version > archived.lifecycle_version


def test_stale_cr_approval_preserves_archive_metadata():
    from projects import change_request_service as crs
    user = actor(superuser=True)
    project = ready_project(user)
    cr = crs.create_change_request(project=project, user=user, reason='Correct employer identity', proposed_changes={'employer': 'New name'})
    cr = crs.submit_change_request(cr, user)
    # Force the old related object to be cached before the archive.
    assert cr.project.status == 'active'
    archived = life.archive(project, user)
    crs.approve_change_request(cr, user)
    current = Project.objects.get(pk=project.pk)
    assert current.status == 'archived'
    assert current.archive_cycle_id == archived.archive_cycle_id
    assert current.employer == 'New name'


@pytest.mark.parametrize('different_request',[False,True])
@pytest.mark.parametrize('different_admin',[False,True])
def test_parallel_restores_have_one_immutable_winner(different_request,different_admin):
    from threading import Barrier
    from uuid import uuid4
    from audit.models import AuditLog
    from projects.models import ProjectArchiveRestore
    from .archive_restore_helpers import archived_project, client_for, base
    from .test_project_archive_restore import confirmation, body
    u=actor(admin=True);other=actor(admin=True) if different_admin else u
    p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    second=body(confirmation(client_for(other),p)) if different_admin else dict(payload)
    second['request_id']=str(uuid4()) if different_request else payload['request_id']
    barrier=Barrier(3)
    def send(who,data):
        close_old_connections()
        try:
            barrier.wait(timeout=10)
            r=client_for(who).post(base(p)+'restore/',data,format='json')
            return r.status_code,r.json()
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=2) as pool:
        a=pool.submit(send,u,payload);b=pool.submit(send,other,second);barrier.wait(timeout=10)
        results=[a.result(timeout=15),b.result(timeout=15)]
    assert sum(code==200 and data.get('outcome')=='restored' for code,data in results)==1
    assert all(code in (200,409) for code,_ in results)
    receipts=ProjectArchiveRestore.objects.filter(project=p)
    assert receipts.count()==1
    winner=next(data['receipt'] for code,data in results if code==200 and data['outcome']=='restored')
    assert str(receipts.get().request_id)==winner['request_id']
    assert life.restore_receipt_data(receipts.get())==winner
    assert AuditLog.objects.filter(project=p).count()==1
    assert Project.objects.get(pk=p.pk).status=='active'


@pytest.mark.parametrize('writer',['patch','manager','complete','suspend','resume','archive','cr','delete'])
def test_restore_serializes_with_other_project_writers(monkeypatch,writer):
    from threading import current_thread
    from projects import change_request_service as crs
    from projects.models import ProjectArchiveRestore
    from audit.models import AuditLog
    from .archive_restore_helpers import client_for, base
    from .test_project_archive_restore import confirmation, body
    u=actor(superuser=True);p=ready_project(u)
    cr=None
    if writer=='cr':
        cr=crs.create_change_request(project=p,user=u,reason='Correct employer before archive',proposed_changes={'employer':'Verified employer'})
        cr=crs.submit_change_request(cr,u)
    resume_body=None
    if writer=='resume':p,resume_body=consumed_resume_context(p,u)
    p=life.archive(p,u);original_cycle=p.archive_cycle_id
    payload=body(confirmation(client_for(u),p))
    restore_locked,writer_entered,release=Event(),Event(),Event()
    original_save,original_lock=life.save_project,life.lock_project
    def pause_restore(project,fields):
        if current_thread().name.startswith('restorer') and project.status=='active':
            restore_locked.set();assert release.wait(10)
        return original_save(project,fields)
    def observe_writer_lock(project):
        if current_thread().name.startswith('writer'):writer_entered.set()
        return original_lock(project)
    monkeypatch.setattr(life,'save_project',pause_restore)
    monkeypatch.setattr(life,'lock_project',observe_writer_lock)
    monkeypatch.setattr(crs,'lock_project',observe_writer_lock)
    from projects import status_undo_service as undo_service
    monkeypatch.setattr(undo_service,'lock_project',observe_writer_lock)
    def restore_request():
        close_old_connections()
        try:return client_for(u).post(base(p)+'restore/',payload,format='json').status_code
        finally:connections.close_all()
    def write_request():
        close_old_connections()
        try:
            c=client_for(u)
            if writer=='patch':return c.patch(base(p),{'project_name':'Renamed after restore'},format='json').status_code
            if writer=='manager':return c.patch(base(p),{'project_manager':None},format='json').status_code
            if writer=='delete':return c.delete(base(p)).status_code
            if writer=='cr':return c.post(base(p)+f'change-requests/{cr.pk}/approve/').status_code
            return c.post(base(p)+writer+'/',resume_body if writer=='resume' else {},format='json').status_code
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=1,thread_name_prefix='restorer') as restore_pool, ThreadPoolExecutor(max_workers=1,thread_name_prefix='writer') as writer_pool:
        first=restore_pool.submit(restore_request)
        try:
            assert restore_locked.wait(10)
            pending=client_for(u).get(base(p)+f"restore-attempts/{payload['request_id']}/").json()
            assert pending['outcome']=='not_recorded' and pending['current_project']['status']=='archived'
            second=writer_pool.submit(write_request)
            assert writer_entered.wait(10)
        finally:release.set()
        assert first.result(timeout=15)==200
        code=second.result(timeout=15)
    if writer=='delete':
        assert code==204 and not Project.objects.filter(pk=p.pk).exists()
        assert AuditLog.objects.filter(resource_id=p.pk,changes__event='project.restored_from_archive').count()==1
        return
    assert code==(409 if writer=='resume' else 200)
    p.refresh_from_db()
    assert p.status=={'complete':'completed','suspend':'suspended','archive':'archived'}.get(writer,'active')
    assert ProjectArchiveRestore.objects.filter(project=p).count()==1
    assert AuditLog.objects.filter(project=p,changes__event='project.restored_from_archive').count()==1
    if writer=='archive':assert p.archive_cycle_id!=original_cycle
    if writer=='patch':assert p.project_name=='Renamed after restore'
    if writer=='cr':assert p.employer=='Verified employer'


@pytest.mark.parametrize('writer',['patch','manager','complete','suspend','resume','archive','cr','delete'])
def test_other_writer_wins_root_lock_before_restore(monkeypatch,writer):
    from threading import current_thread
    from projects import change_request_service as crs
    from projects.models import ProjectArchiveRestore
    from .archive_restore_helpers import client_for,base
    from .test_project_archive_restore import confirmation,body
    u=actor(superuser=True);p=ready_project(u);cr=None
    if writer=='cr':
        cr=crs.create_change_request(project=p,user=u,reason='Approved scope correction',proposed_changes={'scope_description':'New approved scope'})
        cr=crs.submit_change_request(cr,u)
    resume_body=None
    if writer=='resume':p,resume_body=consumed_resume_context(p,u)
    p=life.archive(p,u);payload=body(confirmation(client_for(u),p))
    locked,restore_entered,release=Event(),Event(),Event();original=life.lock_project
    def controlled_lock(project):
        if current_thread().name.startswith('restorer'):restore_entered.set()
        row=original(project)
        if current_thread().name.startswith('writer'):
            locked.set();assert release.wait(10)
        return row
    monkeypatch.setattr(life,'lock_project',controlled_lock);monkeypatch.setattr(crs,'lock_project',controlled_lock)
    from projects import status_undo_service as undo_service
    monkeypatch.setattr(undo_service,'lock_project',controlled_lock)
    def send(restoring):
        close_old_connections()
        try:
            c=client_for(u)
            if restoring:return c.post(base(p)+'restore/',payload,format='json').status_code
            if writer=='patch':return c.patch(base(p),{'project_name':'Changed before restore'},format='json').status_code
            if writer=='manager':return c.patch(base(p),{'project_manager':None},format='json').status_code
            if writer=='delete':return c.delete(base(p)).status_code
            if writer=='cr':return c.post(base(p)+f'change-requests/{cr.pk}/approve/').status_code
            return c.post(base(p)+writer+'/',resume_body if writer=='resume' else {},format='json').status_code
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=1,thread_name_prefix='writer') as wp,ThreadPoolExecutor(max_workers=1,thread_name_prefix='restorer') as rp:
        a=wp.submit(send,False)
        try:
            assert locked.wait(10);b=rp.submit(send,True);assert restore_entered.wait(10)
        finally:release.set()
        first,second=a.result(timeout=15),b.result(timeout=15)
    if writer=='delete':assert (first,second)==(204,404);return
    if writer in ('patch','manager','cr'):
        assert (first,second)==(200,409)
        assert Project.objects.get(pk=p.pk).status=='archived'
        assert not ProjectArchiveRestore.objects.filter(project=p).exists()
    else:
        assert (first,second)==(409 if writer=='resume' else 400,200)
        assert Project.objects.get(pk=p.pk).status=='active'
        assert ProjectArchiveRestore.objects.filter(project=p).count()==1


@pytest.mark.parametrize('first',['restore','patch'])
def test_postgresql_reports_real_root_lock_contention(monkeypatch,first):
    """Observe PostgreSQL's waiting backend, not only arrival at a Python barrier."""
    import time
    from threading import current_thread
    from .archive_restore_helpers import archived_project,client_for,base
    from .test_project_archive_restore import confirmation,body
    u=actor(admin=True);p=archived_project(u);payload=body(confirmation(client_for(u),p))
    first_locked,second_entered,release=Event(),Event(),Event();pids={};original=life.lock_project
    def controlled(project):
        name='first' if current_thread().name.startswith('first') else 'second'
        pids[name]=connections['default'].connection.info.backend_pid
        if name=='second':second_entered.set()
        row=original(project)
        if name=='first':first_locked.set();assert release.wait(10)
        return row
    monkeypatch.setattr(life,'lock_project',controlled)
    def send(action):
        close_old_connections()
        try:
            c=client_for(u)
            if action=='restore':return c.post(base(p)+'restore/',payload,format='json').status_code
            return c.patch(base(p),{'project_name':'Changed under actual root contention'},format='json').status_code
        finally:connections.close_all()
    with ThreadPoolExecutor(max_workers=1,thread_name_prefix='first') as a,ThreadPoolExecutor(max_workers=1,thread_name_prefix='second') as b:
        f=a.submit(send,first)
        try:
            assert first_locked.wait(10);s=b.submit(send,'patch' if first=='restore' else 'restore');assert second_entered.wait(10)
            deadline=time.monotonic()+5;waiting=False
            while time.monotonic()<deadline:
                with connections['default'].cursor() as cursor:
                    cursor.execute("SELECT wait_event_type FROM pg_stat_activity WHERE pid=%s",[pids['second']])
                    row=cursor.fetchone();waiting=bool(row and row[0]=='Lock')
                if waiting:break
                time.sleep(0.01)
            assert waiting,'PostgreSQL must observe the overlapping root-row lock wait'
        finally:release.set()
        assert f.result(timeout=15)==200
        assert s.result(timeout=15)==(200 if first=='restore' else 409)
