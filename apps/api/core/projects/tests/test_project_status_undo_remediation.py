import pytest
from projects.tests.status_undo_helpers import *
from projects.models import ProjectChangeRequest,ProjectStatusUndo
from audit.models import AuditLog
pytestmark=pytest.mark.django_db

def snapshot(project):
    return state(project),list(ProjectChangeRequest.objects.filter(project=project).order_by('id').values()),list(ProjectStatusUndo.objects.filter(project=project).order_by('id').values()),list(AuditLog.objects.filter(project=project).order_by('id').values())

@pytest.mark.parametrize('changes',[{'scope_description':'Fixed scope'},{'contract_amount':'0'},{'scope_description':'Scope','contract_amount':'25.00'}])
def test_completed_repair_is_bound_missing_only_and_other_approved(changes):
    owner=actor(admin=True);other=actor(admin=True);p=source_project(owner,'undo_completion');c=client_for(owner)
    p.scope_description='';p.contract_amount=None;p.project_manager=None;p.save()
    budget=(p.budget_approved_at,p.budget_approved_by_id)
    r=c.post(base(p)+'change-requests/',{'reason':'Repair missing activation data','proposed_changes':changes},format='json')
    assert r.status_code==201,r.data
    cr=ProjectChangeRequest.objects.get(pk=r.data['id']);assert cr.restore_completion_event_id==p.completion_event_id and cr.restore_archive_cycle_id is None
    assert c.post(base(p)+f'change-requests/{cr.pk}/submit/').status_code==200
    denied=c.post(base(p)+f'change-requests/{cr.pk}/approve/')
    assert denied.status_code==400 and denied.data['error']['code']=='sod_self_approve'
    r=client_for(other).post(base(p)+f'change-requests/{cr.pk}/approve/')
    assert r.status_code==200,r.data
    p.refresh_from_db();assert p.status=='completed' and (p.budget_approved_at,p.budget_approved_by_id)==budget
    assert not p.status_undos.exists()

@pytest.mark.parametrize('action',['patch','submit','approve'])
@pytest.mark.parametrize('invalid',['event','status','filled','authority'])
def test_stale_binding_rejects_without_partial_write(action,invalid):
    from projects import change_request_service as crs
    owner=actor(admin=True);other=actor(admin=True);p=source_project(owner,'undo_completion');p.scope_description='';p.save()
    cr=crs.create_change_request(project=p,user=owner,reason='Repair missing activation scope',proposed_changes={'scope_description':'Restored'})
    if action=='approve':cr=crs.submit_change_request(cr,owner)
    if invalid=='filled':p.scope_description='Independently repaired';p.save()
    if invalid=='status':p=lifecycle.archive(p,owner)
    if invalid=='event':
        p.scope_description='Ready';p.save();c=client_for(owner)
        assert c.post(base(p)+'undo-completion/',confirmed_body(c,p,'undo_completion'),format='json').status_code==200
        p=lifecycle.complete(p,owner);p.scope_description='';p.save()
    who=other if action=='approve' else owner
    if invalid=='authority':who.groups.clear()
    c=client_for(who);before=snapshot(p);path=base(p)+f'change-requests/{cr.pk}/'
    r=c.patch(path,{'proposed_changes':{'scope_description':'Replacement'}},format='json') if action=='patch' else c.post(path+action+'/')
    assert r.status_code in (400,403,409),r.data
    assert snapshot(p)==before

@pytest.mark.parametrize('changes',[{'employer':'Other'},{'scope_description':'Already filled'},{'contract_amount':None},{'contract_amount':'NaN'},{'contract_amount':'Infinity'},{'contract_amount':'0','employer':'Other'}])
def test_completion_repair_does_not_broaden_protected_editing(changes):
    user=actor(admin=True);p=source_project(user,'undo_completion');p.contract_amount=None;p.save();c=client_for(user);before=snapshot(p)
    r=c.post(base(p)+'change-requests/',{'reason':'Repair only missing amount','proposed_changes':changes},format='json')
    assert r.status_code in (400,409) and snapshot(p)==before
    assert c.patch(base(p),{'contract_amount':'1'},format='json').status_code==400


def test_stale_cancel_and_same_completion_archive_roundtrip():
    from projects import change_request_service as crs
    user=actor(admin=True);p=source_project(user,'undo_completion');p.scope_description='';p.save()
    cr=crs.create_change_request(project=p,user=user,reason='Restore missing project scope',proposed_changes={'scope_description':'Scope'})
    p=lifecycle.archive(p,user)
    r=client_for(user).get(base(p)+f'change-requests/{cr.pk}/');assert r.data['restore_remediation_actions']==['cancel']
    v=lifecycle.restore_preview(p,user);lifecycle.restore(p,user,request_id=uuid4(),confirmation_token=v['confirmation_token'],reason='Mistaken archive')
    assert crs.submit_change_request(cr,user).status=='submitted'
    p=lifecycle.archive(p,user)
    assert crs.cancel_change_request(cr,user).status=='cancelled'
