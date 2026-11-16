"""Create five distinct acceptance logins and disposable projects, saving secrets privately."""
import json
import os
import subprocess
from pathlib import Path

script = '''
import json, os, secrets, time
from uuid import uuid4
from django.db import connection
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from authentication.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from master_data.models import Role, Permission, RolePermission, ProjectMember, ProjectMemberRole
from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
from projects.services import create_project_with_creator
from projects.models import ProjectStatus, ProjectKickoffCharter
from schedule.models import MspImportJob
from schedule.tests.a7_p5_runtime_matrix import XML
from schedule.services.msp_import import execute_msp_import
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
assert 'a7p5' in connection.settings_dict['NAME'] and os.environ.get('A7_P5_ISOLATED') == '1'
for name in ['project_manager','viewer']:
 role,_=Role.objects.get_or_create(role_name=name)
 for code in DEFAULT_ROLE_PERMISSIONS[name]:
  Permission.objects.get_or_create(codename=code,defaults={'label':PERMISSIONS[code]})
  RolePermission.objects.get_or_create(role=role,permission_codename=code)
roles={n:Role.objects.get(role_name=n) for n in ['project_manager','viewer']}
personas={}
users={}
for name in ['creator_planner','independent_approver','viewer','system_admin','org_reference_steward']:
 password=secrets.token_urlsafe(20)
 mobile='+989'+str(int(uuid4().hex[:12],16)).zfill(12)[-9:]
 u=get_user_model().objects.create_user(username='a7-'+name+'-'+uuid4().hex[:8],mobile=mobile,full_name='A7 '+name,password=password,is_staff=name=='system_admin')
 if name in ['system_admin','org_reference_steward']:u.groups.add(Group.objects.get_or_create(name='admin')[0])
 token=RefreshToken.for_user(u)
 users[name]=u
 personas[name]={'access':str(token.access_token),'refresh':str(token),'user':dict(UserSerializer(u).data),'username':u.username,'mobile':mobile,'password':password}
def member(p,u,role='project_manager'):
 m,_=ProjectMember.objects.get_or_create(project=p,user=u,defaults={'status':'active'})
 ProjectMemberRole.objects.get_or_create(member=m,role=roles[role])
def project(owner,name):
 p=create_project_with_creator(creator=owner,project_code='A7DEL-'+uuid4().hex[:10],project_name=name,employer='A7 acceptance',start_date='2026-01-01')
 p.status=ProjectStatus.ACTIVE;p.project_manager=owner;p.scope_description='Acceptance scope';p.contract_amount=1000000;p.budget_approved_at=timezone.now();p.budget_approved_by=users['independent_approver'];p.save()
 return p
main=project(users['creator_planner'],'A7 delivery reference')
for key in ['system_admin','independent_approver']:member(main,users[key])
member(main,users['viewer'],'viewer')
ProjectKickoffCharter.objects.create(project=main,created_by=users['creator_planner'],**{k:'A7 retained '+k for k in ['justification','success_criteria','constraints','assumptions','key_stakeholders_summary','pm_authority']})
execute_msp_import(main,XML,filename='initial.xml',user=users['creator_planner'])
b=project(users['system_admin'],'A7 independent project B')
cases=[]
for lang in ['fa','en']:
 for width in [1280,390]:
  p=project(users['system_admin'],f'A7 import {lang} {width}')
  cases.append({'lang':lang,'width':width,'project':str(p.id)})
print(json.dumps({'admin_auth':personas['system_admin'],'viewer_auth':personas['viewer'],'project_main':str(main.id),'project_b':str(b.id),'cases':cases,'personas':personas,'role_ids':{k:str(v.id) for k,v in roles.items()}}))
'''
root = Path(__file__).resolve().parents[2]
r=subprocess.run(['docker','exec','-i',os.environ.get('A7P6_API_CONTAINER','a7p5-import-api-1'),'python','manage.py','shell'],input=script,text=True,capture_output=True,check=True)
value=json.loads(r.stdout.strip().splitlines()[-1])
target=root/'ops/a7-p5/.runtime-delivery.json'
fd=os.open(target,os.O_CREAT|os.O_TRUNC|os.O_WRONLY,0o600)
os.fchmod(fd,0o600)
with os.fdopen(fd,'w') as out:json.dump(value,out)
print('Five acceptance personas and disposable reference projects created; credentials saved privately.')
