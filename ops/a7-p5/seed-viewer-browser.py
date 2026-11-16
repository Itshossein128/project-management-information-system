"""Provision a private disposable owner/viewer fixture on the isolated A7 database."""
import os
import subprocess

script = '''
import json, os
from uuid import uuid4
from django.db import connection
from django.contrib.auth import get_user_model
from authentication.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from master_data.models import Role, Permission, RolePermission, ProjectMember, ProjectMemberRole
from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
from projects.services import create_project_with_creator
from projects.models import ProjectStatus, Activity, WBS, ProjectKickoffCharter
from schedule.models import BaselineSchedule, BaselineActivity
from schedule.services.msp_import import execute_msp_import
from schedule.tests.a7_p5_runtime_matrix import XML
assert 'a7p5' in connection.settings_dict['NAME'] and os.environ.get('A7_P5_ISOLATED') == '1'
for name in ['project_manager','viewer']:
 role,_=Role.objects.get_or_create(role_name=name)
 for code in DEFAULT_ROLE_PERMISSIONS[name]:
  Permission.objects.get_or_create(codename=code,defaults={'label':PERMISSIONS[code]})
  RolePermission.objects.get_or_create(role=role,permission_codename=code)
 assert name != 'viewer' or set(role.role_permissions.values_list('permission_codename',flat=True)) == set(DEFAULT_ROLE_PERMISSIONS[name]), 'viewer role has unexpected permissions'
def user(label):
 return get_user_model().objects.create_user(username='neg12-'+uuid4().hex[:12],full_name=label,password=None)
owner=user('NEG12 owner');viewer=user('NEG12 viewer')
p=create_project_with_creator(creator=owner,project_code='NEG12-'+uuid4().hex[:12],project_name='NEG12 retained project',employer='Retained employer',start_date='2026-01-01')
p.status=ProjectStatus.ACTIVE;p.save(update_fields=['status'])
execute_msp_import(p,XML,filename='viewer-fixture.xml',user=owner)
ProjectKickoffCharter.objects.create(project=p,justification='Retained charter',created_by=owner)
m=ProjectMember.objects.create(project=p,user=viewer,status='active')
ProjectMemberRole.objects.create(member=m,role=Role.objects.get(role_name='viewer'))
base=BaselineSchedule.objects.get(project=p)
assert not base.is_locked
base.version_name='NEG12 retained baseline';base.save(update_fields=['version_name'])
ba=BaselineActivity.objects.get(baseline=base)
act=Activity.objects.get(project=p);node=WBS.objects.get(project=p)
def auth(u):
 t=RefreshToken.for_user(u)
 return {'access':str(t.access_token),'refresh':str(t),'user':dict(UserSerializer(u).data)}
print(json.dumps({'admin_auth':auth(owner),'viewer_auth':auth(viewer),'project_main':str(p.id),'project_b':str(p.id),'cases':[], 'private_activity':str(act.id),'private_baseline':str(base.id),'private_baseline_activity':str(ba.id),'viewer_wbs':str(node.id),'viewer_baseline_name':base.version_name}))
'''
r=subprocess.run(['docker','exec','-i',os.environ.get('A7P6_API_CONTAINER','a7p5-import-api-1'),'python','manage.py','shell'],input=script,text=True,capture_output=True,check=True)
print(r.stdout.strip().splitlines()[-1])
