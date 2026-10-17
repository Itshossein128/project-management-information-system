import pytest
from projects.tests.status_undo_helpers import *
from projects.models import ProjectStatusUndo
from django.db import IntegrityError
pytestmark=pytest.mark.django_db

@pytest.mark.parametrize('language',['fa','en'])
def test_localized_actionable_errors_keep_stable_machine_codes(language,monkeypatch):
    user=actor(admin=True);p=source_project(user);c=client_for(user);c.defaults['HTTP_ACCEPT_LANGUAGE']=language;body=confirmed_body(c,p)
    cases=[(c.post(base(p)+'resume/',{**body,'reason':' '},format='json'),'reason_required',400)]
    p.contract_amount=None;p.save();body=confirmed_body(c,p)
    cases.append((c.post(base(p)+'resume/',body,format='json'),'activation_gates_failed',400))
    p.contract_amount=1;p.save()
    cases.append((c.post(base(p)+'resume/',body,format='json'),'status_undo_context_changed',409))
    body=confirmed_body(c,p)
    def fail(*args,**kwargs):raise IntegrityError('injected known rollback')
    monkeypatch.setattr(ProjectStatusUndo.objects,'create',fail)
    cases.append((c.post(base(p)+'resume/',body,format='json'),'status_undo_not_applied',503))
    other=client_for(actor());other.defaults['HTTP_ACCEPT_LANGUAGE']=language
    cases.append((other.get(base(p)+'resume-preview/'),'permission_denied',403))
    for response,code,status in cases:
        assert response.status_code==status,response.data
        error=response.data['error'];assert error['code']==code
        assert len(error['message'])>15 and any('\u0600'<=ch<='\u06ff' for ch in error['message'])==(language=='fa'),error


@pytest.mark.parametrize('language',['fa','en'])
@pytest.mark.parametrize('case',['self_approve','short_reason','invalid_amount','invalid_state','open_conflict','invalid_keys'])
def test_completed_remediation_http_errors_are_localized(language,case):
    from projects.tests.test_project_status_undo_remediation import snapshot
    owner=actor(admin=True);other=actor(admin=True);p=source_project(owner,'undo_completion')
    p.scope_description='';p.contract_amount=None;p.save()
    c=client_for(owner);c.defaults['HTTP_ACCEPT_LANGUAGE']=language
    collection=base(p)+'change-requests/'
    valid={'reason':'Repair missing activation scope','proposed_changes':{'scope_description':'Approved scope'}}
    if case in ['self_approve','invalid_state','open_conflict']:
        created=c.post(collection,valid,format='json');assert created.status_code==201,created.data
        item=collection+created.data['id']+'/'
        if case=='self_approve':assert c.post(item+'submit/').status_code==200
    before=snapshot(p)
    if case=='self_approve':response=c.post(item+'approve/');expected=('sod_self_approve',400)
    elif case=='short_reason':response=c.post(collection,{**valid,'reason':'x'},format='json');expected=('reason_required',400)
    elif case=='invalid_amount':response=c.post(collection,{**valid,'proposed_changes':{'contract_amount':'NaN'}},format='json');expected=('invalid_proposed_keys',400)
    elif case=='invalid_keys':response=c.post(collection,{**valid,'proposed_changes':{'employer':'Forbidden employer'}},format='json');expected=('invalid_change_request_status',400)
    elif case=='open_conflict':response=c.post(collection,valid,format='json');expected=('change_request_already_open',409)
    else:
        c=client_for(other);c.defaults['HTTP_ACCEPT_LANGUAGE']=language
        response=c.post(item+'approve/');expected=('invalid_change_request_status',400)
    assert (response.data['error']['code'],response.status_code)==expected,response.data
    assert any('\u0600'<=ch<='\u06ff' for ch in response.data['error']['message'])==(language=='fa'),response.data
    assert snapshot(p)==before
