from itertools import combinations
import pytest
from projects.tests.status_undo_helpers import *
from master_data.models import ProjectMemberPermissionOverride

pytestmark=pytest.mark.django_db

@pytest.mark.parametrize('kind',['admin','superuser','editor','approver','viewer','manager','outsider','inactive'])
@pytest.mark.parametrize('operation',['resume','undo_completion'])
def test_actual_authority(kind,operation):
    owner=actor(admin=True);p=source_project(owner,operation);user=actor(admin=kind=='admin',superuser=kind=='superuser')
    codes={'editor':['edit_project'],'approver':['approve_project'],'viewer':['view_project']}.get(kind,[])
    if codes:member(user,p,*codes)
    if kind=='manager':p.project_manager=user;p.save(update_fields=['project_manager'])
    if kind=='inactive':user.is_active=False;user.save()
    client=client_for(user)
    permitted=kind in ('admin','superuser') or kind=='editor' and operation=='resume'
    result=preview(client,p,operation)
    assert result.status_code==(200 if permitted else 403),result.data
    denied=client.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),{},format='json')
    if not permitted:assert denied.status_code==403

MISSING=[list(c) for n in (1,2,3) for c in combinations(['project_manager','scope_description','budget_approved'],n)]
@pytest.mark.parametrize('missing',MISSING)
@pytest.mark.parametrize('operation',['resume','undo_completion'])
def test_all_missing_gates_exactly(missing,operation):
    user=actor(admin=True);p=source_project(user,operation);client=client_for(user)
    values={'project_manager':None,'scope_description':'   ','budget_approved':None}
    for key in missing:setattr(p,'contract_amount' if key=='budget_approved' else key,values[key])
    p.save()
    view=preview(client,p,operation);assert view.status_code==200
    assert set(view.data['missing'])==set(missing) and not view.data['can_confirm']
    assert {r['field'] for r in view.data['remediation']}==set(missing)
    before=state(p)
    result=client.post(base(p)+('resume/' if operation=='resume' else 'undo-completion/'),confirmed_body(client,p,operation),format='json')
    assert result.status_code==400 and result.data['error']['code']=='activation_gates_failed'
    assert state(p)==before


def test_zero_valid_nonactive_target_unrestricted_and_fresh_revocation():
    user=actor(admin=True);p=source_project(user);client=client_for(user)
    p.contract_amount=0;p.save()
    view=preview(client,p);assert view.data['can_confirm']
    body=confirmed_body(client,p)
    p.project_manager=None;p.save()
    result=client.post(base(p)+'resume/',body,format='json')
    assert result.status_code==409
    user.groups.clear()
    assert client.post(base(p)+'resume/',body,format='json').status_code==403
    owner=actor(admin=True);p=source_project(owner,'undo_completion','suspended')
    p.project_manager=None;p.scope_description='';p.contract_amount=None;p.save()
    client=client_for(owner);view=preview(client,p,'undo_completion')
    assert view.data['can_confirm'] and view.data['missing']==[]
    assert client.post(base(p)+'undo-completion/',confirmed_body(client,p,'undo_completion'),format='json').data['current_project']['status']=='suspended'


def test_editor_with_only_edit_project_can_confirm_resume():
    owner=actor(admin=True);p=source_project(owner);editor=actor()
    member(editor,p,'edit_project');client=client_for(editor)
    result=client.post(base(p)+'resume/',confirmed_body(client,p),format='json')
    assert result.status_code==200,result.data
    assert result.data['current_project']['status']=='active'
    assert result.data['receipt']['actor']['id']==str(editor.pk)


@pytest.mark.parametrize('change',['grant_revoked','actor_inactive','manager_deleted'])
def test_editor_confirmation_rechecks_real_grant_account_and_manager_deletion(change):
    from projects.models import ProjectStatusUndo
    owner=actor(admin=True);p=source_project(owner);editor=actor()
    membership=member(editor,p,'edit_project');client=client_for(editor)
    body=confirmed_body(client,p)
    if change=='grant_revoked':
        ProjectMemberPermissionOverride.objects.filter(member=membership).delete()
    elif change=='actor_inactive':
        editor.is_active=False;editor.save(update_fields=['is_active'])
    else:
        owner.delete()
    before=state(p)
    result=client.post(base(p)+'resume/',body,format='json')
    assert result.status_code==(409 if change=='manager_deleted' else 403),result.data
    assert state(p)==before
    assert not ProjectStatusUndo.objects.filter(project=p).exists()


def test_undo_completion_to_suspended_keeps_existing_baseline_and_commitment_restrictions():
    from projects.readiness import assert_project_allows_definitive_baseline,assert_project_allows_binding_commitment
    from config.exceptions import CodedValidationError
    owner=actor(admin=True);p=source_project(owner,'undo_completion','suspended');client=client_for(owner)
    result=client.post(base(p)+'undo-completion/',confirmed_body(client,p,'undo_completion'),format='json')
    assert result.status_code==200,result.data
    p.refresh_from_db()
    for gate in [assert_project_allows_definitive_baseline,assert_project_allows_binding_commitment]:
        with pytest.raises(CodedValidationError):gate(p)


@pytest.mark.parametrize('operation',['resume','undo_completion'])
@pytest.mark.parametrize('surface',['preview','apply','attempt','history'])
def test_anonymous_status_undo_interfaces_never_disclose_or_write(operation,surface):
    from rest_framework.test import APIClient
    from audit.models import AuditLog
    from projects.models import ProjectStatusUndo
    owner=actor(admin=True);p=source_project(owner,operation);authorized=client_for(owner)
    body=confirmed_body(authorized,p,operation,reason='Private authenticated correction')
    action='resume/' if operation=='resume' else 'undo-completion/'
    if surface in ['attempt','history']:
        assert authorized.post(base(p)+action,body,format='json').status_code==200
    before=state(p);audits=list(AuditLog.objects.filter(project=p).order_by('id').values())
    receipts=list(ProjectStatusUndo.objects.filter(project=p).values())
    path=base(p)+({'preview':'resume-preview/' if operation=='resume' else 'undo-completion-preview/',
                   'apply':action,'attempt':f"status-undo-attempts/{operation}/{body['request_id']}/",'history':'status-undo-history/'}[surface])
    anonymous=APIClient()
    response=anonymous.post(path,body,format='json') if surface=='apply' else anonymous.get(path)
    assert response.status_code==401 and response.data['error']['code']=='not_authenticated'
    assert response['Cache-Control']=='no-store'
    assert b'Private authenticated correction' not in response.content
    assert state(p)==before
    assert list(AuditLog.objects.filter(project=p).order_by('id').values())==audits
    assert list(ProjectStatusUndo.objects.filter(project=p).values())==receipts
