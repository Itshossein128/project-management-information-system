#!/usr/bin/env python3
"""Use a second real importer for overlapping duplicate delivery, then remove it."""
import json
import subprocess
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=['docker','compose','--env-file','ops/a7-p5/.env.acceptance','-f','ops/a7-p5/compose.yml']
def run(*args):
    return subprocess.run(C+list(args),cwd=ROOT,check=True,text=True,capture_output=True).stdout
config=json.loads(run('config','--format','json'))
assert config['name']=='a7p5-import' and config['services']['postgres']['environment']['POSTGRES_DB']=='a7p5_import'
container=run('run','-d','--no-deps','--name','a7p5-repeat-probe','import-worker','celery','-A','config','worker','-l','warning','-Q','a7p5-import','-c','1','--prefetch-multiplier=1','-n','a7p5-repeat@%h').strip().splitlines()[-1]
try:
    for attempt in range(40):
        ready=run('exec','-T','api','python','manage.py','shell','-c',"from config.celery import app; q=app.control.inspect(timeout=2).active_queues() or {}; print('READY' if sum(any(x['name']=='a7p5-import' for x in v) for v in q.values())>=2 else 'WAIT')")
        if 'READY' in ready:break
        time.sleep(.5)
    else:raise RuntimeError('second actual importer unavailable')
    output=run('exec','-T','api','python','manage.py','shell','-c',"""
import json
from django.core.files.uploadedfile import SimpleUploadedFile
from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix,XER
from schedule.models import MspImportJob,P6ImportJob
from schedule.tasks import run_msp_import_task,run_p6_import_task
from django.conf import settings
m=RuntimeMatrix('A7P5-CONCURRENT-','/fixtures/plan.mpp');cases=[]
try:
 for family in ('msp','p6'):
  p=m.project();m.arm('before_prepare')
  task=run_msp_import_task if family=='msp' else run_p6_import_task
  if family=='msp':j=m.started(p)
  else:
   response=m.client.post(f'/api/v1/projects/{p.pk}/import/p6/',{'file':SimpleUploadedFile('plan.xer',XER),'replace':'false','intent':'new'},format='multipart')
   assert response.status_code==202,response.data
   j=P6ImportJob.objects.get(pk=response.data['task_id'])
  m.reached('before_prepare')
  duplicate=task.apply_async(args=[str(j.id)],queue=settings.IMPORT_EXECUTION_QUEUE).get(timeout=15)
  assert duplicate=={'duplicate':True},duplicate
  m.release('before_prepare');m.wait(j);assert j.status=='done',j.error_code
  counts=m.counts(p);anchor=j.completed_at
  task.apply_async(args=[str(j.id)],queue=settings.IMPORT_EXECUTION_QUEUE).get(timeout=15)
  j.refresh_from_db();assert m.counts(p)==counts and j.completed_at==anchor
  cases.append({'family':family,'job':str(j.id),'live_duplicate_result':duplicate,'committed_counts':counts,'immutable_completion':True})
 print('A7P5_CONCURRENT_JSON '+json.dumps({'status':'pass','actual_import_consumers':2,'cases':cases,'healthy_follow_up':m.healthy()}))
finally:m.release('before_prepare')
""")
    report=json.loads(next(x.removeprefix('A7P5_CONCURRENT_JSON ') for x in output.splitlines() if x.startswith('A7P5_CONCURRENT_JSON ')))
    (ROOT/'specs/055-a7-p5-import-operations/evidence/runtime/concurrent-delivery.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'families':len(report['cases']),'actual_import_consumers':2}))
finally:
    subprocess.run(['docker','rm','-f',container],check=True,capture_output=True,text=True)
