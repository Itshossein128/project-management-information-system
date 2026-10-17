import pytest
from projects.models import Project, ProjectChangeRequest
from .archive_restore_helpers import actor, archived_project, client_for, base
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db


def incomplete(u):
    p=archived_project(u);p.project_manager=None;p.scope_description='';p.contract_amount=None;p.save();return p


def test_nonmember_admin_can_complete_information_through_existing_controls():
    requester=actor(admin=True);approver=actor(admin=True);p=incomplete(requester);c=client_for(requester)
    stamps=(p.budget_approved_at,p.budget_approved_by_id)
    r=c.patch(base(p),{'scope_description':'Direct bypass'},format='json');assert r.status_code==400
    r=c.post(base(p)+'change-requests/',{'reason':'Complete missing approved information','proposed_changes':{'scope_description':'Restored scope','contract_amount':'0.00'}},format='json')
    assert r.status_code==201,r.content
    cr_id=r.json()['id'];cr=ProjectChangeRequest.objects.get(pk=cr_id)
    assert cr.restore_archive_cycle_id==p.archive_cycle_id
    assert 'submit' in r.json()['restore_remediation_actions']
    assert c.get(base(p)).json()['can_create_restore_remediation'] is False
    assert c.post(base(p)+f'change-requests/{cr_id}/submit/').status_code==200
    assert 'approve' not in c.get(base(p)+f'change-requests/{cr_id}/').json()['restore_remediation_actions']
    own=c.post(base(p)+f'change-requests/{cr_id}/approve/')
    assert own.status_code==400 and own.json()['error']['code']=='sod_self_approve'
    other=client_for(approver)
    assert 'approve' in other.get(base(p)+f'change-requests/{cr_id}/').json()['restore_remediation_actions']
    assert other.post(base(p)+f'change-requests/{cr_id}/approve/').status_code==200
    assert c.patch(base(p),{'project_manager':str(approver.pk)},format='json').status_code==200
    p.refresh_from_db();assert (p.budget_approved_at,p.budget_approved_by_id)==stamps
    assert c.post(base(p)+'restore/',body(confirmation(c,p)),format='json').status_code==200


@pytest.mark.parametrize('changes',[{'employer':'Not allowed'},{'scope_description':' '},{'contract_amount':None}])
def test_remediation_is_not_general_archived_edit(changes):
    u=actor(admin=True);p=incomplete(u);c=client_for(u)
    r=c.post(base(p)+'change-requests/',{'reason':'Complete missing approved information','proposed_changes':changes},format='json')
    assert r.status_code==400 and not ProjectChangeRequest.objects.filter(project=p).exists()

@pytest.mark.parametrize('action',['update','submit','approve'])
@pytest.mark.parametrize('changed',['cycle','status','readiness','authority'])
def test_bound_remediation_rechecks_current_context_without_partial_writes(action,changed):
    from django.contrib.auth.models import Group
    from master_data.models import ProjectMember, ProjectMemberPermissionOverride
    from audit.models import AuditLog
    from projects.models import ProjectArchiveRestore
    from projects import lifecycle_service
    from .archive_restore_helpers import state
    requester=actor(admin=True);approver=actor(admin=True);p=incomplete(requester)
    for user in (requester,approver):
        member=ProjectMember.objects.create(project=p,user=user,status='active')
        for code in ('view_project','edit_project','approve_project'):
            ProjectMemberPermissionOverride.objects.create(member=member,permission_codename=code,is_granted=True)
    c=client_for(requester)
    response=c.post(base(p)+'change-requests/',{'reason':'Repair this exact archive cycle','proposed_changes':{'scope_description':'Completed scope','contract_amount':'100.00'}},format='json')
    assert response.status_code==201,response.content
    cr_id=response.json()['id'];url=base(p)+f'change-requests/{cr_id}/'
    if action=='approve':assert c.post(url+'submit/').status_code==200
    operator=approver if action=='approve' else requester
    if changed=='authority':operator.groups.clear()
    else:
        # Simulate information completed by a different authorized writer.
        p.project_manager=requester;p.scope_description='Scope completed elsewhere';p.contract_amount='200.00';p.save()
        if changed in ('cycle','status'):
            assert c.post(base(p)+'restore/',body(confirmation(c,p)),format='json').status_code==200
            if changed=='cycle':lifecycle_service.archive(p,requester)
    before=(state(p),list(ProjectChangeRequest.objects.filter(project=p).values()),list(ProjectArchiveRestore.objects.filter(project=p).values()),list(AuditLog.objects.order_by('id').values()))
    op=client_for(operator)
    result=op.patch(url,{'reason':'Updated remediation reason'},format='json') if action=='update' else op.post(url+action+'/')
    assert result.status_code==(403 if changed=='authority' else 400 if changed=='readiness' else 409),result.content
    after=(state(p),list(ProjectChangeRequest.objects.filter(project=p).values()),list(ProjectArchiveRestore.objects.filter(project=p).values()),list(AuditLog.objects.order_by('id').values()))
    assert after==before
    if changed=='authority':operator.groups.add(Group.objects.get(name='admin'))
    cancel=client_for(operator).post(url+'cancel/')
    assert cancel.status_code==200,cancel.content
    assert cancel.json()['status']=='cancelled'
    assert state(p)==before[0] and list(ProjectArchiveRestore.objects.filter(project=p).values())==before[2]
