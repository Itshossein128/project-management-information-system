from itertools import combinations
import pytest
from django.contrib.auth.models import Group
from master_data.models import ProjectMember, ProjectMemberRole, ProjectMemberPermissionOverride, Role
from projects.models import ProjectArchiveRestore
from .archive_restore_helpers import actor, archived_project, client_for, base, state
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db
GATES=['project_manager','scope_description','budget_approved']


@pytest.mark.parametrize('missing',[c for n in range(1,4) for c in combinations(GATES,n)])
def test_all_missing_prerequisites_and_real_support_flags(missing):
    u=actor(admin=True);p=archived_project(u)
    if 'project_manager' in missing:p.project_manager=None
    if 'scope_description' in missing:p.scope_description=' \t '
    if 'budget_approved' in missing:p.contract_amount=None
    p.save();c=client_for(u);before=state(p)
    detail=c.get(base(p)).json()
    assert detail.get('can_edit_manager_for_restore')==('project_manager' in missing)
    assert detail.get('can_create_restore_remediation')==bool(set(missing)&{'scope_description','budget_approved'})
    preview=confirmation(c,p)
    assert preview['missing']==[f for f in GATES if f in missing]
    assert len(preview['remediation'])==len(missing)
    r=c.post(base(p)+'restore/',body(preview),format='json')
    assert r.status_code==400 and r.json()['error']['code']=='activation_gates_failed'
    assert r.json()['error']['details']['missing']==preview['missing']
    assert state(p)==before and not ProjectArchiveRestore.objects.exists()


@pytest.mark.parametrize('kind',['outsider','viewer','editor','approver','inactive','anonymous'])
def test_denied_actor_matrix(kind):
    admin=actor(admin=True);p=archived_project(admin);u=actor()
    if kind in ('viewer','editor','approver','inactive'):
        m=ProjectMember.objects.create(project=p,user=u,status='inactive' if kind=='inactive' else 'active')
        if kind!='inactive':
            role=Role.objects.get(role_name='viewer');ProjectMemberRole.objects.create(member=m,role=role)
            for code in ['view_project']+(['edit_project'] if kind=='editor' else ['approve_project'] if kind=='approver' else []):
                ProjectMemberPermissionOverride.objects.create(member=m,permission_codename=code,is_granted=True)
    c=client_for(None if kind=='anonymous' else u);before=state(p)
    r=c.get(base(p)+'restore-preview/')
    assert r.status_code in (401,403)
    r=c.post(base(p)+'restore/',{'reason':'test'},format='json')
    assert r.status_code in (401,403)
    assert state(p)==before


@pytest.mark.parametrize('origin',['suspended','completed'])
def test_nonactive_target_does_not_require_activation(origin):
    u=actor(superuser=True);p=archived_project(u,origin)
    p.project_manager=None;p.scope_description='';p.contract_amount=None;p.save()
    c=client_for(u);preview=confirmation(c,p)
    assert preview['missing']==[]
    r=c.post(base(p)+'restore/',body(preview),format='json')
    assert r.status_code==200 and r.json()['current_project']['status']==origin


def test_authority_revoked_after_preview():
    u=actor(admin=True);p=archived_project(u);c=client_for(u);payload=body(confirmation(c,p));before=state(p)
    u.groups.clear()
    r=c.post(base(p)+'restore/',payload,format='json')
    assert r.status_code==403 and state(p)==before


@pytest.mark.parametrize('key',['status','archive_cycle_id','archived_from_status','lifecycle_version','budget_approved_at','budget_approved_by'])
def test_patch_cannot_write_lifecycle_fields(key):
    u=actor(admin=True);p=archived_project(u);c=client_for(u);before=state(p)
    r=c.patch(base(p),{key:'active'},format='json')
    assert r.status_code==400
    assert state(p)==before


def test_project_manager_membership_alone_is_not_restore_authority():
    admin=actor(admin=True);manager=actor();p=archived_project(admin)
    p.project_manager=manager;p.save(update_fields=['project_manager'])
    member=ProjectMember.objects.create(project=p,user=manager,status='active')
    for code in ('view_project','edit_project','approve_project'):
        ProjectMemberPermissionOverride.objects.create(member=member,permission_codename=code,is_granted=True)
    c=client_for(manager);before=state(p)
    assert c.get(base(p)).json()['can_restore_from_archive'] is False
    assert c.get(base(p)+'restore-preview/').status_code==403
    assert c.post(base(p)+'restore/',{'reason':'Not sufficient'},format='json').status_code==403
    assert state(p)==before and not ProjectArchiveRestore.objects.filter(project=p).exists()


def test_groupless_superuser_preview_and_restore_need_no_membership():
    creator=actor(admin=True);user=actor(superuser=True);p=archived_project(creator)
    assert not user.groups.exists() and not ProjectMember.objects.filter(project=p,user=user).exists()
    c=client_for(user)
    assert c.get(base(p)).json()['can_restore_from_archive'] is True
    assert c.post(base(p)+'restore/',body(confirmation(c,p)),format='json').status_code==200
