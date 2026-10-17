from uuid import uuid4
import pytest
from django.core import signing
from projects import lifecycle_service as life
from projects.models import Project, ProjectArchiveRestore
from audit.models import AuditLog
from .archive_restore_helpers import actor, archived_project, base, client_for, state
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db


def test_result_lookup_is_project_scoped_and_inconclusive_before_commit():
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    url=base(p)+f"restore-attempts/{payload['request_id']}/"
    before=state(p);r=c.get(url)
    assert r.status_code==200,r.content
    assert r.json()['outcome']=='not_recorded' and r.json()['receipt'] is None
    assert state(p)==before and not AuditLog.objects.filter(project=p).exists()
    first=c.post(base(p)+'restore/',payload,format='json').json()
    r=c.get(url)
    assert r.json()['outcome']=='completed' and r.json()['receipt']==first['receipt']
    assert r.headers['Cache-Control']=='no-store'
    other=archived_project(u)
    r=c.get(base(other)+f"restore-attempts/{payload['request_id']}/")
    assert r.json()['outcome']=='not_recorded'
    assert client_for(actor()).get(url).status_code==403


@pytest.mark.parametrize('later',['suspended','completed','new_archive'])
def test_exact_old_retry_reports_history_without_changing_current_state(later):
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    first=c.post(base(p)+'restore/',payload,format='json').json()
    p=Project.objects.get(pk=p.pk)
    if later=='suspended':life.suspend(p,u)
    elif later=='completed':life.complete(p,u)
    else:life.archive(life.complete(p,u),u)
    before=state(p);prior_audit_count=AuditLog.objects.filter(project=p).count()
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==200 and r.json()['outcome']=='replayed'
    assert r.json()['receipt']==first['receipt'] and state(p)==before
    assert r.json()['current_project']['status']==before['status']
    assert ProjectArchiveRestore.objects.filter(project=p).count()==1
    assert AuditLog.objects.filter(project=p).count()==prior_audit_count


@pytest.mark.parametrize('change',['reason','snapshot','actor','project','token','request'])
def test_changed_submission_cannot_reuse_confirmation_or_receipt(change):
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    if change in ('reason','request'):
        assert c.post(base(p)+'restore/',payload,format='json').status_code==200
        payload={**payload,**({'reason':'Different reason'} if change=='reason' else {'request_id':str(uuid4())})}
        expected='restore_request_conflict' if change=='reason' else 'archive_already_restored'
    elif change=='snapshot':
        c.patch(base(p),{'project_name':'Changed name'},format='json')
        c.patch(base(p),{'project_name':p.project_name},format='json')
        expected='restore_context_changed'
    elif change=='actor':c=client_for(actor(admin=True));expected='permission_denied'
    elif change=='project':p=archived_project(u);expected='permission_denied'
    else:payload={**payload,'confirmation_token':'tampered'};expected='invalid_restore_request'
    before=state(p);r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code in (400,403,409) and r.json()['error']['code']==expected
    assert state(p)==before


def test_preview_has_no_clock_expiry_and_post_does_not_restore_deleted_project():
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p))
    # The contract intentionally passes no max_age to signing.loads.
    context=signing.loads(payload['confirmation_token'],salt='projects.archive.restore.v1')
    assert context['archive_cycle_id']==str(p.archive_cycle_id)
    before=state(p);url=base(p);p.delete()
    assert c.post(url+'restore/',payload,format='json').status_code==404
    assert not Project.objects.filter(pk=before['id']).exists()


def test_confirmed_context_has_no_elapsed_time_cutoff(monkeypatch):
    from unittest.mock import patch
    u=actor(admin=True);p=archived_project(u);c=client_for(u)
    with patch('django.core.signing.time.time',return_value=1_000_000_000):payload=body(confirmation(c,p))
    assert c.post(base(p)+'restore/',payload,format='json').status_code==200
