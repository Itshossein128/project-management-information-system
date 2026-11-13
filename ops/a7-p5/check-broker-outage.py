#!/usr/bin/env python3
"""Stop only the private Redis after durable intake; restore and reconcile."""
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ['docker','compose','--env-file','ops/a7-p5/.env.acceptance','-f','ops/a7-p5/compose.yml']
def compose(*args, **kwargs):
    return subprocess.run(COMPOSE+list(args),cwd=ROOT,check=True,text=True,**kwargs)
def shell(code):
    return compose('exec','-T','api','python','manage.py','shell','-c',code,capture_output=True).stdout

# Compose's declared project/database/port identity is checked before stopping it.
config=json.loads(compose('config','--format','json',capture_output=True).stdout)
assert config['name']=='a7p5-import'
assert config['services']['postgres']['environment']['POSTGRES_DB']=='a7p5_import'
def control(action):
    return compose('exec','-T','api','python','-c',
        "from pathlib import Path;p=Path('/var/a7p5-scratch/faults');"+action, capture_output=True).stdout.strip()
control("(p/'reached-before_publish').unlink(missing_ok=True)")
code="""
import json,time
from pathlib import Path
from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix
m=RuntimeMatrix('A7P5-BROKER-','/fixtures/plan.mpp')
m.arm('before_publish');p=m.project();started=time.monotonic();j=m.started(p)
assert j.status=='pending'
Path('/tmp/a7p5-broker-job.json').write_text(json.dumps({'job':str(j.id),'project':str(p.id),'user':str(m.user.id),'http_elapsed_seconds':time.monotonic()-started,'dispatch_deadline':j.dispatch_deadline_at.isoformat()}))
"""
process=subprocess.Popen(COMPOSE+['exec','-T','api','python','manage.py','shell','-c',code],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
try:
    until=time.monotonic()+30
    while control("print((p/'reached-before_publish').exists())") != 'True':
        if process.poll() is not None:raise RuntimeError(process.communicate()[1][-1000:])
        if time.monotonic()>until:raise RuntimeError('publish barrier not reached')
        time.sleep(.1)
    compose('stop','redis',stdout=subprocess.DEVNULL)
    control("(p/'arm-before_publish').unlink(missing_ok=True)")
    # Wait for the admitted response observation, rather than timing process
    # shutdown (Python may still reap a bounded publication thread).
    until=time.monotonic()+12
    while True:
        result=subprocess.run(COMPOSE+['exec','-T','api','test','-f','/tmp/a7p5-broker-job.json'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if result.returncode==0:break
        if time.monotonic()>until:raise RuntimeError('admitted response exceeded deadline')
        time.sleep(.1)
finally:
    control("(p/'arm-before_publish').unlink(missing_ok=True)")
    compose('start','redis',stdout=subprocess.DEVNULL)
stdout,stderr=process.communicate(timeout=30)
if process.returncode:raise RuntimeError(stderr[-1000:])
for _ in range(50):
    ping=compose('exec','-T','redis','redis-cli','ping',capture_output=True)
    if 'PONG' in ping.stdout:break
    time.sleep(.2)
observed=shell("""
import json,time
from pathlib import Path
from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix
from schedule.models import MspImportJob
from schedule.services.import_operations import run_maintenance
meta=json.loads(Path('/tmp/a7p5-broker-job.json').read_text());j=MspImportJob.objects.get(pk=meta['job'])
before_deadline=j.dispatch_deadline_at
result=run_maintenance('recovery');assert result['status']=='ok',result
until=time.monotonic()+100
while True:
 j.refresh_from_db()
 if j.status in ('done','failed'):break
 assert time.monotonic()<until,j.status
 time.sleep(.2)
assert j.status=='done',(j.error_code,j.error_message)
assert j.dispatch_deadline_at==before_deadline
m=RuntimeMatrix('A7P5-BROKER-AFTER-','/fixtures/plan.mpp');healthy=m.healthy()
print('A7P5_BROKER_JSON '+json.dumps({**meta,'status':'pass','terminal':j.status,'recovery':result,'healthy_follow_up':healthy,'fixed_dispatch_deadline':True}))
""")
report=json.loads(next(line.removeprefix('A7P5_BROKER_JSON ') for line in observed.splitlines() if line.startswith('A7P5_BROKER_JSON ')))
target=ROOT/'specs/055-a7-p5-import-operations/evidence/runtime/broker-outage.json'
target.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'terminal':report['terminal'],'http_elapsed_seconds':report['http_elapsed_seconds']}))
