from uuid import uuid4
import pytest
from audit.models import AuditLog
from projects.models import ProjectArchiveRestore
from .archive_restore_helpers import actor, archived_project, base, client_for, state

pytestmark = pytest.mark.django_db


def confirmation(client, project):
    response = client.get(base(project)+'restore-preview/')
    assert response.status_code == 200, response.content
    return response.json()


def body(preview, reason='Archived by mistake'):
    return {'request_id': str(uuid4()), 'confirmation_token': preview['confirmation_token'], 'reason': reason}


@pytest.mark.parametrize('origin', ['active','suspended','completed'])
def test_exact_origin_preview_and_restore(origin):
    user = actor(admin=True)
    p = archived_project(user, origin)
    c = client_for(user)
    before = state(p)
    detail = c.get(base(p)).json()
    assert detail.get('can_restore_from_archive') is True
    preview = confirmation(c,p)
    assert preview['project_name'] == p.project_name
    assert preview['to_status'] == origin
    assert preview['can_confirm'] is True
    assert preview['missing'] == []
    assert state(p) == before
    prior_audits = list(AuditLog.objects.filter(project=p).values())
    response = c.post(base(p)+'restore/', body(preview), format='json')
    assert response.status_code == 200, response.content
    data = response.json()
    assert data['outcome'] == 'restored'
    assert data['current_project']['status'] == origin
    receipt = data['receipt']
    assert receipt['from_status'] == 'archived' and receipt['to_status'] == origin
    assert receipt['actor']['id'] == str(user.pk)
    assert receipt['reason'] == 'Archived by mistake'
    assert ProjectArchiveRestore.objects.filter(project=p).count() == 1
    logs = AuditLog.objects.filter(project=p)
    assert logs.count() == len(prior_audits) + 1
    assert logs.filter(changes__event='project.restored_from_archive').count() == 1
    assert list(AuditLog.objects.filter(pk__in=[row['id'] for row in prior_audits]).values()) == prior_audits
    after = state(p)
    assert after['budget_approved_at'] == before['budget_approved_at']
    assert after['budget_approved_by_id'] == before['budget_approved_by_id']
    assert after['archive_cycle_id'] == before['archive_cycle_id']
    assert {k:v for k,v in after.items() if k not in {'status','lifecycle_version','updated_at'}} == {k:v for k,v in before.items() if k not in {'status','lifecycle_version','updated_at'}}
    if origin != 'active':
        from projects.readiness import assert_project_allows_definitive_baseline, assert_project_allows_binding_commitment
        p.refresh_from_db()
        for gate in (assert_project_allows_definitive_baseline, assert_project_allows_binding_commitment):
            with pytest.raises(__import__('config.exceptions',fromlist=['CodedValidationError']).CodedValidationError): gate(p)


@pytest.mark.parametrize('reason', ['', '  \t\n '])
def test_empty_reason_has_no_effect(reason):
    user=actor(superuser=True);p=archived_project(user);c=client_for(user)
    payload=body(confirmation(c,p), reason);before=state(p)
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==400 and r.json()['error']['code']=='reason_required'
    assert state(p)==before and not ProjectArchiveRestore.objects.exists()


def test_exact_retry_is_not_a_new_success():
    user=actor(admin=True);p=archived_project(user);c=client_for(user)
    payload=body(confirmation(c,p), '  mistaken archive  ')
    first=c.post(base(p)+'restore/',payload,format='json')
    assert first.status_code==200
    before=state(p)
    second=c.post(base(p)+'restore/',payload,format='json')
    assert second.status_code==200
    assert second.json()['outcome']=='replayed'
    assert second.json()['receipt']==first.json()['receipt']
    assert state(p)==before and AuditLog.objects.filter(project=p).count()==1


@pytest.mark.parametrize('key', ['status','archived_from_status','archive_cycle_id','lifecycle_version','budget_approved_at','actor'])
def test_restore_rejects_injected_fields(key):
    user=actor(admin=True);p=archived_project(user);c=client_for(user)
    payload={**body(confirmation(c,p)),key:'active'};before=state(p)
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==400 and r.json()['error']['code']=='invalid_restore_request'
    assert state(p)==before


def test_no_project_permission_substitutes_for_global_admin():
    admin=actor(admin=True);p=archived_project(admin);ordinary=actor()
    c=client_for(ordinary);before=state(p)
    for method in ('get','post'):
        r=getattr(c,method)(base(p)+('restore-preview/' if method=='get' else 'restore/'),{},format='json')
        assert r.status_code==403
    assert state(p)==before


def test_core_audit_failure_rolls_back(monkeypatch):
    from audit import service
    from django.db import IntegrityError
    user=actor(admin=True);p=archived_project(user);c=client_for(user)
    payload=body(confirmation(c,p));before=state(p)
    def fail(*args, **kwargs):raise IntegrityError('forced audit insert failure')
    monkeypatch.setattr(service,'persist_audit_log',fail)
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==503 and r.json()['error']['code']=='restore_not_applied'
    assert state(p)==before and not ProjectArchiveRestore.objects.exists()


def test_new_archive_records_the_latest_origin():
    from projects import lifecycle_service as life
    from projects.models import Project
    user=actor(admin=True);p=archived_project(user);c=client_for(user)
    first_cycle=p.archive_cycle_id
    assert c.post(base(p)+'restore/',body(confirmation(c,p)),format='json').status_code==200
    p=life.complete(Project.objects.get(pk=p.pk),user)
    p=life.archive(p,user)
    assert p.archive_cycle_id!=first_cycle and p.archived_from_status=='completed'
    preview=confirmation(c,p)
    assert preview['to_status']=='completed'
    assert c.post(base(p)+'restore/',body(preview),format='json').json()['current_project']['status']=='completed'
    assert ProjectArchiveRestore.objects.filter(project=p).count()==2
