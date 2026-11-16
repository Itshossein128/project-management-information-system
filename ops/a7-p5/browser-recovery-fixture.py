"""Private isolated browser fixtures and bounded existing fault barrier controls."""
import os
import subprocess
import sys
from uuid import UUID

COMMON = '''
import os, json
from pathlib import Path
from django.conf import settings
from django.db import connection
from schedule.models import MspImportJob, P6ImportJob
assert 'a7p5' in connection.settings_dict['NAME'] and os.environ.get('A7_P5_ISOLATED') == '1'
assert not settings.CELERY_TASK_ALWAYS_EAGER
'''
action = sys.argv[1]
if action == 'seed':
    script = '''
from uuid import uuid4
from django.contrib.auth import get_user_model
from authentication.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from master_data.models import Permission, Role, RolePermission
from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
from projects.services import create_project_with_creator
from projects.models import ProjectStatus
from schedule.services.msp_import import execute_msp_import
from schedule.tests.a7_p5_runtime_matrix import XML
role, _ = Role.objects.get_or_create(role_name='project_manager')
for code, label in PERMISSIONS.items():
 Permission.objects.get_or_create(codename=code, defaults={'label':label})
for code in DEFAULT_ROLE_PERMISSIONS['project_manager']:
 RolePermission.objects.get_or_create(role=role, permission_codename=code)
def user():
 return get_user_model().objects.create_user(username='neg0811-'+uuid4().hex[:12],full_name='Isolated planner',password=None)
def project(u, name):
 p=create_project_with_creator(creator=u, project_code='N0811-'+uuid4().hex[:12],project_name=name,employer='Acceptance',start_date='2026-01-01')
 p.status=ProjectStatus.ACTIVE;p.save(update_fields=['status']);return p
u=user();other=user();a=project(u,'NEG0811 project A');b=project(other,'NEG0811 confidential project B')
r=execute_msp_import(b,XML,filename='private-b.xml',user=other)
from projects.models import Activity
from schedule.models import BaselineSchedule, BaselineActivity
act=Activity.objects.get(project=b)
act.activity_name='PRIVATE-B-ACTIVITY-'+uuid4().hex;act.save(update_fields=['activity_name'])
base=BaselineSchedule.objects.get(project=b)
base.version_name='PRIVATE-B-BASELINE-'+uuid4().hex;base.save(update_fields=['version_name'])
job=MspImportJob.objects.create(project=b,created_by=other,filename='private-b.xml',status='done')
t=RefreshToken.for_user(u)
auth={'access':str(t.access_token),'refresh':str(t),'user':dict(UserSerializer(u).data)}
print(json.dumps({'admin_auth':auth,'viewer_auth':auth,'project_main':str(a.id),'project_b':str(b.id),'cases':[], 'private_job':str(job.id),'private_activity':str(act.id),'private_baseline':str(base.id),'private_baseline_activity':str(BaselineActivity.objects.get(baseline=base).id),'private_markers':[act.activity_name,base.version_name]}))
'''
else:
    pid = str(UUID(sys.argv[2]))
    script = "pid = %r\n" % pid
    script += '''
root=Path(os.environ['A7_P5_FAULT_DIR'])
marker=root/'arm-before_prepare'
reached=root/'reached-before_prepare'
'''
    if action == 'hold':
        script += '''
assert not list(root.glob('arm-*')), 'another fault test is active'
assert not MspImportJob.objects.filter(status__in=['pending','running']).exists()
assert not P6ImportJob.objects.filter(status__in=['pending','running']).exists()
reached.unlink(missing_ok=True)
marker.write_text('pause')
print('armed')
'''
    elif action == 'release':
        script += "marker.unlink(missing_ok=True)\nprint('released')\n"
    elif action == 'jobs':
        script += "print(json.dumps({'msp':list(MspImportJob.objects.filter(project_id=pid).values('id','status')), 'p6':list(P6ImportJob.objects.filter(project_id=pid).values('id','status')), 'held':reached.exists() and marker.exists()},default=str))\n"
    else:
        raise SystemExit('unknown action')
result = subprocess.run(['docker','exec','-i',os.environ.get('A7P6_API_CONTAINER','a7p5-import-api-1'),'python','manage.py','shell'],input=COMMON+script,text=True,capture_output=True,check=True)
print(result.stdout.strip().splitlines()[-1])
