"""Run through manage.py shell; safe for the production database.

Checks actual dedicated consumers and kernel containment. Optional reference
preparation writes only bounded, temporary processing-slot/workspace metadata;
project, charter, WBS, schedule and import-job counts must remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import uuid

from django.conf import settings
from config.celery import app
from projects.models import Project, ProjectKickoffCharter, WBS, Activity, ActivityRelation
from schedule.models import MspImportJob, P6ImportJob, BaselineSchedule
from schedule.services.import_process import cgroup_ready, scratch_root, _arm_cgroup, _finish_cgroup, prepare_bytes

assert settings.IMPORT_CONTAINMENT_REQUIRED and settings.IMPORT_ADMISSION_REQUIRES_CATCHUP
assert not settings.IMPORT_PREPARE_INLINE and not settings.CELERY_TASK_ALWAYS_EAGER
assert settings.IMPORT_EXECUTION_QUEUE != settings.IMPORT_MAINTENANCE_QUEUE
assert cgroup_ready(), 'Delegated cgroup unavailable'
root=scratch_root();assert os.statvfs(root).f_blocks*os.statvfs(root).f_frsize <= settings.IMPORT_SCRATCH_QUOTA_BYTES
inspector=app.control.inspect(timeout=5)
queues=inspector.active_queues() or {}
imports={n for n,q in queues.items() if any(x['name']==settings.IMPORT_EXECUTION_QUEUE for x in q)}
maintenance={n for n,q in queues.items() if any(x['name']==settings.IMPORT_MAINTENANCE_QUEUE for x in q)}
assert imports and maintenance and imports.isdisjoint(maintenance), 'Independent queue consumers are required'
process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'],start_new_session=True)
group=None
try:
 group=_arm_cgroup(uuid.uuid4(),process.pid)
 _finish_cgroup(group,process)
finally:
 if process.poll() is None:process.kill();process.wait()
models=[Project,ProjectKickoffCharter,WBS,Activity,ActivityRelation,BaselineSchedule,MspImportJob,P6ImportJob]
before=[m.objects.count() for m in models]
report={'status':'pass','cgroup':'actual_attach_and_cleanup_pass','scratch_size_bytes':os.statvfs(root).f_blocks*os.statvfs(root).f_frsize,'independent_import_consumers':len(imports),'independent_maintenance_consumers':len(maintenance),'eager':False,'inline':False,'schedule_tree_sha256':hashlib.sha256(b''.join(p.read_bytes() for p in sorted((Path(settings.BASE_DIR)/'schedule').rglob('*.py')))).hexdigest()}
reference=os.environ.get('VELORA_IMPORT_REFERENCE')
if reference:
 parsed=prepare_bytes(Path(reference).read_bytes(),'plan.mpp','msp')
 assert len(parsed.tasks)==80 and sum(t.is_summary for t in parsed.tasks)==6
 report['native_mpp']={'status':'pass','parsed_tasks':80,'summary_tasks':6,'reference_sha256':hashlib.sha256(Path(reference).read_bytes()).hexdigest()}
assert [m.objects.count() for m in models]==before,'Business data changed during readiness check'
report['business_data_unchanged']=True
print('VELORA_IMPORT_PREFLIGHT '+json.dumps(report))
