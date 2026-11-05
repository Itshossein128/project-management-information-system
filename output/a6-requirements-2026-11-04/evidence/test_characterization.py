"""Read-only audit probes: XFAIL is a reproduced invariant gap, not delivery acceptance."""
import uuid
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from projects.models import Project
from master_data.models import ProjectMember, Role, RolePermission, ProjectMemberRole, ProjectPosition
from inventory.models import Category

@pytest.fixture
def ctx(db,settings):
 settings.AUDIT_LOG_ASYNC=False
 settings.CACHES={'default':{'BACKEND':'django.core.cache.backends.locmem.LocMemCache'}}
 U=get_user_model()
 actor=U.objects.create_user(username='a6manager',mobile='+989120002001',password='Audit-only-123')
 target=U.objects.create_user(username='a6target',mobile='+989120002002',password='Audit-only-123')
 p=Project.objects.create(project_code='A6-AUDIT',project_name='A6 test project',status='active')
 role=Role.objects.create(role_name='a6_probe_manager')
 RolePermission.objects.create(role=role,permission_codename='manage_members')
 m=ProjectMember.objects.create(project=p,user=actor,status='active')
 ProjectMemberRole.objects.create(member=m,role=role)
 c=APIClient();c.force_authenticate(actor)
 return p,actor,target,c

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,reason='Unknown UUID role is silently skipped by assign_roles_to_member')
def test_invalid_role_id_must_not_create_roleless_member(ctx):
 p,a,t,c=ctx
 r=c.post(f'/api/v1/projects/{p.id}/members/',{'user_id':str(t.id),'role_ids':[str(uuid.uuid4())]},format='json')
 print('INVALID_ROLE observed_HTTP=',r.status_code,'returned_roles=',r.data.get('roles'),'membership_exists=',ProjectMember.objects.filter(project=p,user=t).exists())
 assert r.status_code==400
 assert not ProjectMember.objects.filter(project=p,user=t).exists()

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,reason='Legacy global Item writes lack visitor read-only policy')
def test_global_visitor_cannot_write_legacy_items(ctx):
 p,a,t,c=ctx
 g,_=Group.objects.get_or_create(name='visitor');t.groups.add(g)
 c.force_authenticate(t)
 cat=Category.objects.create(name='A6 audit category')
 r=c.post('/api/items/',{'name':'A6 audit item','quantity':1,'category':cat.id},format='json')
 print('VISITOR_ITEM_WRITE observed_HTTP=',r.status_code)
 assert r.status_code==403

@pytest.mark.django_db
@pytest.mark.xfail(strict=True,reason='CanViewProjectMembers tests membership existence without active status')
def test_inactive_member_cannot_list_project_positions(ctx):
 p,a,t,c=ctx
 ProjectMember.objects.create(project=p,user=t,status='inactive')
 ProjectPosition.objects.create(project=p,position_name='Audit position')
 c.force_authenticate(t)
 r=c.get(f'/api/v1/projects/{p.id}/positions/')
 print('INACTIVE_POSITION_READ observed_HTTP=',r.status_code)
 assert r.status_code==403
