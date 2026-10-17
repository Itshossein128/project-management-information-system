import pytest
from django.db import IntegrityError, transaction
from projects.tests.status_undo_helpers import actor,ready_project

pytestmark=pytest.mark.django_db

@pytest.mark.parametrize('status',['suspended','completed'])
def test_unknown_effective_origin_cannot_persist(status):
    project=ready_project(actor(admin=True))
    with pytest.raises(IntegrityError), transaction.atomic():
        type(project).objects.filter(pk=project.pk).update(status=status)

@pytest.mark.parametrize('values',[
    {'completed_from_status':'active'}, {'completed_from_status':'draft'},
    {'status':'archived','archived_from_status':'completed','archive_cycle_id':__import__('uuid').uuid4()},
    {'status':'archived','archived_from_status':'suspended','archive_cycle_id':__import__('uuid').uuid4()},
])
def test_strict_effective_source_pairs(values):
    project=ready_project(actor(admin=True))
    with pytest.raises(IntegrityError), transaction.atomic():
        type(project).objects.filter(pk=project.pk).update(**values)


def test_retained_archive_suspended_origin_does_not_require_current_suspension():
    from uuid import uuid4
    project=ready_project(actor(admin=True))
    type(project).objects.filter(pk=project.pk).update(archived_from_status='suspended',archive_cycle_id=uuid4())
    project.refresh_from_db()
    assert project.status=='active' and project.suspension_event_id is None


def test_required_fk_receipt_constraints_and_deletion_collector():
    from uuid import uuid4
    from django.utils import timezone
    from django.db.models.deletion import ProtectedError
    from projects import lifecycle_service as life
    from projects.models import ProjectStatusUndo, ProjectChangeRequest
    from audit.models import AuditLog
    user=actor(admin=True); project=life.suspend(ready_project(user),user)
    source=project.suspension_event
    def values(**changes):
        success=AuditLog.objects.create(project=project,actor=user,http_method='POST',path='/resume/')
        fresh_source=AuditLog.objects.create(project=project,actor=user,http_method='POST',path='/suspend/')
        data=dict(project=project,operation='resume',source_audit_log=fresh_source,source_snapshot={'id':str(source.pk)},request_id=uuid4(),request_fingerprint='a'*64,confirmation_version=1,actor=user,actor_snapshot={'id':str(user.pk),'display_name':'Original'},project_snapshot={'project_name':project.project_name},reason='Mistake',from_status='suspended',to_status='active',performed_at=success.created_at,audit_log=success)
        data.update(changes);return data
    row=ProjectStatusUndo.objects.create(**values(source_audit_log=source))
    for changes in [{'request_id':row.request_id,'operation':'undo_completion','from_status':'completed'}, {'source_audit_log':source}, {'audit_log':source,'source_audit_log':source}, {'to_status':'draft'}, {'reason':' '}, {'reason':' trailing '}]:
        with pytest.raises(IntegrityError),transaction.atomic():ProjectStatusUndo.objects.create(**values(**changes))
    with pytest.raises(ProtectedError):source.delete()
    # A CR may have only one protected repair binding.
    with pytest.raises(IntegrityError),transaction.atomic():
        ProjectChangeRequest.objects.create(project=project,requested_by=user,reason='Missing scope repair',restore_archive_cycle_id=uuid4(),restore_completion_event=source)
    user.delete();row.refresh_from_db()
    assert row.actor_id is None and row.actor_snapshot['display_name']=='Original'
    source_id=source.pk;project.delete()
    source.refresh_from_db();assert source.project_id is None
    assert AuditLog.objects.filter(pk=source_id).exists() and not ProjectStatusUndo.objects.filter(pk=row.pk).exists()


@pytest.mark.django_db(transaction=True,serialized_rollback=True)
def test_0016_forward_reverse_preserves_prior_business_and_archive_receipt():
    from uuid import uuid4
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    from projects.models import Project,ProjectArchiveRestore
    from audit.models import AuditLog
    from projects.tests.status_undo_helpers import populate_business_records,business_snapshot
    user=actor(admin=True);project=ready_project(user);records=populate_business_records(project,user)
    before=business_snapshot(records);fields=type(project).objects.filter(pk=project.pk).values().get()
    audit=AuditLog.objects.create(project=project,actor=user,http_method='POST',path='/restore/',changes={'event':'prior'})
    receipt=ProjectArchiveRestore.objects.create(project=project,archive_cycle_id=uuid4(),request_id=uuid4(),request_fingerprint='a'*64,confirmation_version=0,actor=user,actor_snapshot={'id':str(user.pk)},project_snapshot={'project_name':project.project_name},reason='Prior archive restoration',from_status='archived',to_status='active',restored_at=audit.created_at,audit_log=audit)
    saved=ProjectArchiveRestore.objects.filter(pk=receipt.pk).values().get()
    old=[('projects','0016_bind_archive_remediation')]
    executor=MigrationExecutor(connection);latest=executor.loader.graph.leaf_nodes('projects')
    try:
        executor.migrate(old)
        historical=executor.loader.project_state(old).apps
        row=historical.get_model('projects','Project').objects.get(pk=project.pk)
        assert row.status=='active' and row.project_name==fields['project_name']
        assert historical.get_model('projects','ProjectChangeRequest').objects.get(pk=records[-2].pk).status=='approved'
        assert ProjectArchiveRestore.objects.filter(pk=receipt.pk).values().get()==saved
        assert business_snapshot(records[:-2]+records[-1:])==before[:-2]+before[-1:]
    finally:MigrationExecutor(connection).migrate(latest)
    assert business_snapshot(records)==before
    assert ProjectArchiveRestore.objects.filter(pk=receipt.pk).values().get()==saved
    project.refresh_from_db();assert project.suspension_event_id is None and project.completion_event_id is None

@pytest.mark.django_db(transaction=True,serialized_rollback=True)
def test_reverse_after_real_undos_and_bound_repair_preserves_old_business_and_all_audits():
    from uuid import uuid4
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    from audit.models import AuditLog
    from projects import lifecycle_service as life, status_undo_service as undo, change_request_service as crs
    from projects.models import Project,ProjectArchiveRestore,ProjectStatusUndo
    from projects.tests.archive_restore_helpers import populate_business_records,business_snapshot
    owner=actor(admin=True);other=actor(admin=True);p=ready_project(owner);records=populate_business_records(p,owner)
    p=life.archive(p,owner);v=life.restore_preview(p,owner);life.restore(p,owner,request_id=uuid4(),confirmation_token=v['confirmation_token'],reason='Original archive correction');p.refresh_from_db()
    p=life.suspend(p,owner);v=undo.preview(p,owner,'resume');undo.undo(p,owner,'resume',request_id=uuid4(),confirmation_token=v['confirmation_token'],reason='Correct suspension');p.refresh_from_db()
    clear=crs.create_change_request(project=p,user=owner,reason='Prepare known incomplete scope',proposed_changes={'scope_description':' '});clear=crs.submit_change_request(clear,owner);clear=crs.approve_change_request(clear,other)
    p=life.complete(p,owner)
    repair=crs.create_change_request(project=p,user=owner,reason='Repair missing scope with approval',proposed_changes={'scope_description':'Repaired approved scope'});repair=crs.submit_change_request(repair,owner);repair=crs.approve_change_request(repair,other)
    v=undo.preview(p,owner,'undo_completion');undo.undo(p,owner,'undo_completion',request_id=uuid4(),confirmation_token=v['confirmation_token'],reason='Correct completion');p.refresh_from_db()
    assert ProjectStatusUndo.objects.filter(project=p).count()==2 and repair.restore_completion_event_id==p.completion_event_id
    records += [clear,repair];before=business_snapshot(records)
    root=Project.objects.filter(pk=p.pk).values().get();old_fields={k:v for k,v in root.items() if k not in {'suspension_event_id','completion_event_id','completed_from_status'}}
    audits=list(AuditLog.objects.filter(project=p).order_by('id').values());archives=list(ProjectArchiveRestore.objects.filter(project=p).values())
    draft=ready_project(owner);draft.status='draft';draft.save();archived=life.archive(ready_project(owner),owner)
    old=[('projects','0016_bind_archive_remediation')];latest=MigrationExecutor(connection).loader.graph.leaf_nodes('projects')
    try:
        executor=MigrationExecutor(connection);executor.migrate(old);apps=executor.loader.project_state(old).apps
        assert apps.get_model('projects','Project').objects.filter(pk=p.pk).values().get()==old_fields
        assert apps.get_model('projects','Project').objects.get(pk=draft.pk).status=='draft'
        assert apps.get_model('projects','Project').objects.get(pk=archived.pk).status=='archived'
        for record in [records[-4],clear,repair]:
            historical=apps.get_model('projects','ProjectChangeRequest').objects.get(pk=record.pk)
            assert historical.status=='approved'
        assert list(AuditLog.objects.filter(project=p).order_by('id').values())==audits
        assert list(ProjectArchiveRestore.objects.filter(project=p).values())==archives
    finally:MigrationExecutor(connection).migrate(latest)
    after=business_snapshot(records)
    for (label,rows),(old_label,old_rows) in zip(after,before):
        assert label==old_label
        if label=='projects.ProjectChangeRequest':
            rows=[{k:v for k,v in row.items() if k!='restore_completion_event_id'} for row in rows];old_rows=[{k:v for k,v in row.items() if k!='restore_completion_event_id'} for row in old_rows]
        assert rows==old_rows,label
    assert Project.objects.filter(pk=p.pk).values().get()=={**old_fields,'suspension_event_id':None,'completion_event_id':None,'completed_from_status':None}
    assert not ProjectStatusUndo.objects.filter(project=p).exists()
    assert list(AuditLog.objects.filter(project=p).order_by('id').values())==audits
    assert list(ProjectArchiveRestore.objects.filter(project=p).values())==archives
