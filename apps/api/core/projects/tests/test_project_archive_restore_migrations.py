"""Schema assertions; migration forward/reversal proof is extended below."""
import pytest
from django.apps import apps
from django.db import IntegrityError, transaction
from projects.models import Project
from .archive_restore_helpers import actor, ready_project

pytestmark = pytest.mark.django_db


def test_project_archive_schema():
    fields = {f.name for f in Project._meta.fields}
    assert {'archived_from_status', 'archive_cycle_id', 'lifecycle_version'} <= fields
    p = ready_project(actor())
    assert p.lifecycle_version == 0 and p.archive_cycle_id is None
    assert p.archived_from_status is None


def test_archived_requires_known_cycle_and_origin():
    p = ready_project(actor())
    with pytest.raises(IntegrityError), transaction.atomic():
        Project.objects.filter(pk=p.pk).update(status='archived')


def test_restore_receipt_schema():
    assert apps.is_installed('projects')
    assert any(m.__name__ == 'ProjectArchiveRestore' for m in apps.get_app_config('projects').get_models())
    model = apps.get_model('projects', 'ProjectArchiveRestore')
    names = {f.name for f in model._meta.fields}
    assert {'archive_cycle_id','request_id','request_fingerprint','actor_snapshot','project_snapshot','audit_log','restored_at'} <= names
    assert {tuple(c.fields) for c in model._meta.constraints if hasattr(c, 'fields')} >= {
        ('project','archive_cycle_id'), ('project','request_id'),
    }


@pytest.mark.parametrize('values', [
    {'archive_cycle_id': __import__('uuid').uuid4()},
    {'archived_from_status': 'active'},
    {'archived_from_status': 'draft', 'archive_cycle_id': __import__('uuid').uuid4()},
    {'lifecycle_version': -1},
])
def test_invalid_metadata_rejected(values):
    p = ready_project(actor())
    with pytest.raises(IntegrityError), transaction.atomic():
        Project.objects.filter(pk=p.pk).update(**values)


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_forward_reverse_preserves_valid_project():
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    p = ready_project(actor())
    original = (p.project_name, p.scope_description, p.contract_amount)
    before = [('projects', '0014_reportexportversion')]
    after = MigrationExecutor(connection).loader.graph.leaf_nodes('projects')
    try:
        executor = MigrationExecutor(connection)
        executor.migrate(before)
        old = executor.loader.project_state(before).apps.get_model('projects', 'Project')
        row = old.objects.get(pk=p.pk)
        assert (row.project_name, row.scope_description, row.contract_amount) == original
    finally:
        MigrationExecutor(connection).migrate(after)
    row = Project.objects.get(pk=p.pk)
    assert (row.project_name, row.scope_description, row.contract_amount) == original
    assert row.lifecycle_version == 0


def test_receipt_uniqueness_reason_and_actor_snapshot():
    from uuid import uuid4
    from django.utils import timezone
    from audit.models import AuditLog
    from projects.models import ProjectArchiveRestore
    user = actor()
    project = ready_project(user)
    cycle, request_id = uuid4(), uuid4()
    def values(**override):
        audit = AuditLog.objects.create(project=project, actor=user, http_method='POST', path='/restore/')
        return dict(project=project, actor=user, actor_snapshot={'id': str(user.pk), 'display_name': 'Original'}, project_snapshot={'id': str(project.pk)}, archive_cycle_id=cycle, request_id=request_id, request_fingerprint='a'*64, confirmation_version=1, reason='Mistake', from_status='archived', to_status='active', restored_at=timezone.now(), audit_log=audit, **override)
    row = ProjectArchiveRestore.objects.create(**values())
    for changes in ({'request_id': uuid4()}, {'archive_cycle_id': uuid4()}):
        data = values();data.update(changes)
        with pytest.raises(IntegrityError), transaction.atomic():
            ProjectArchiveRestore.objects.create(**data)
    for reason in ('', ' ', ' trimmed ', '\ttrimmed'):
        data = values();data.update(request_id=uuid4(), archive_cycle_id=uuid4(), reason=reason)
        with pytest.raises(IntegrityError), transaction.atomic():
            ProjectArchiveRestore.objects.create(**data)
    user.delete()
    row.refresh_from_db()
    assert row.actor_id is None and row.actor_snapshot['display_name'] == 'Original'


@pytest.mark.django_db(transaction=True, serialized_rollback=True)
def test_final_schema_reverse_after_real_restore_preserves_business_data():
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    from audit.models import AuditLog
    from projects.models import ProjectArchiveRestore
    from .archive_restore_helpers import archived_project,client_for,base,populate_business_records,business_snapshot
    from .test_project_archive_restore import confirmation,body
    from projects import lifecycle_service as life
    u=actor(admin=True);p=ready_project(u);records=populate_business_records(p,u)
    p=life.archive(p,u)
    before=business_snapshot(records);c=client_for(u)
    response=c.post(base(p)+'restore/',body(confirmation(c,p)),format='json')
    assert response.status_code==200
    receipt=ProjectArchiveRestore.objects.get(project=p)
    assert receipt.restored_at==receipt.audit_log.created_at
    assert receipt.audit_log.changes['actor']==receipt.actor_snapshot
    audit_id=receipt.audit_log_id
    latest=MigrationExecutor(connection).loader.graph.leaf_nodes('projects')
    try:
        executor=MigrationExecutor(connection);executor.migrate([('projects','0014_reportexportversion')])
        old=executor.loader.project_state([('projects','0014_reportexportversion')]).apps
        assert old.get_model('projects','Project').objects.get(pk=p.pk).status=='active'
        # Current CR model contains a field intentionally removed by reversal; use historical model for it.
        assert old.get_model('projects','ProjectChangeRequest').objects.get(pk=records[-2].pk).status=='approved'
        assert business_snapshot(records[:-2]+records[-1:])==before[:-2]+before[-1:]
        assert AuditLog.objects.filter(pk=audit_id).exists()
    finally:MigrationExecutor(connection).migrate(latest)
    assert business_snapshot(records)==before
    p.refresh_from_db();assert p.status=='active' and p.archive_cycle_id is None and p.lifecycle_version==0
    assert not ProjectArchiveRestore.objects.filter(project=p).exists()  # reversal deliberately removes this new table
