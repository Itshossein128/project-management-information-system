"""Reproduce startup and native MPP on a disposable, separately named stack."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
from uuid import uuid4

ROOT=Path(__file__).resolve().parents[3]
# evidence/ -> feature/ -> specs/ -> repository/
E=Path(__file__).resolve().parent
project='a7p6-delivery-smoke'
scratch=Path('/run/a7p6-delivery-smoke')
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
report={'status':'failed','project_name':project,'fresh_database':True,'ports':{'api':18010,'postgres':55444,'redis':56389}}
def run(args,**kwargs):return subprocess.run(args,cwd=ROOT,check=True,text=True,**kwargs)
with tempfile.TemporaryDirectory(prefix='a7-startup-') as directory:
 private=Path(directory);config_path=private/'compose.json'
 config=json.loads(run(['docker','compose','--env-file','ops/a7-p5/.env.acceptance','-f','ops/a7-p5/compose.yml','config','--format','json'],capture_output=True).stdout)
 config['name']=project
 config['networks']['default']['name']=project+'_default'
 assert not run(['docker','network','ls','-q','--filter',f'name=^{project}_default$'],capture_output=True).stdout.strip()
 for name,service in config['services'].items():
  if name in ['api','postgres','redis']:
   service['ports'][0]['published']=str({'api':18010,'postgres':55444,'redis':56389}[name])
  service.pop('build',None)
  if name in ['api','import-worker','maintenance-worker','beat']:
   service['environment']['IMPORT_RUNTIME_HOST_ID']='a7p6-delivery-smoke'
  for volume in service.get('volumes',[]):
   if volume.get('target')=='/var/a7p5-scratch':volume['source']=str(scratch)
 config_path.write_text(json.dumps(config));config_path.chmod(0o600)
 compose=['docker','compose','-f',str(config_path)]
 mounted=False;started=False
 try:
  run(['sudo','mkdir','-p',str(scratch)])
  run(['sudo','mount','-t','tmpfs','-o',f'size=256m,mode=0700,uid={os.getuid()},gid={os.getgid()}','a7p6-smoke',str(scratch)]);mounted=True
  # New, separately named containers/anonymous PostgreSQL volume; no shared DB reset.
  started=True;run(compose+['up','-d','--no-build','--pull','never'])
  api=f'{project}-api-1'
  deadline=time.monotonic()+240
  while True:
   ready=run(['docker','inspect',api,'--format','{{.State.Health.Status}}'],capture_output=True).stdout.strip()
   if ready=='healthy':break
   assert time.monotonic()<deadline,'Fresh API did not become healthy'
   time.sleep(2)
  # Expanded Compose config includes the original network's concrete name;
  # rebinding it is mandatory before starting a second stack.
  for service in ['postgres','redis']:
   expected=json.loads(run(['docker','inspect',f'{project}-{service}-1'],capture_output=True).stdout)[0]['NetworkSettings']['Networks'][project+'_default']['IPAddress']
   actual=run(['docker','exec',api,'python','-c',f"import socket;print(socket.gethostbyname('{service}'))"],capture_output=True).stdout.strip()
   assert actual==expected,(service,actual,expected)
  report['separate_network_verified']=True
  run(compose+['exec','-T','api','python','manage.py','maintain_import_jobs','--operation','recovery'])
  deadline=time.monotonic()+90
  while True:
   preflight=subprocess.run(compose+['exec','-T','api','python','manage.py','verify_import_runtime','--preflight'],cwd=ROOT,text=True,capture_output=True)
   if preflight.returncode==0:break
   assert time.monotonic()<deadline,preflight.stderr
   time.sleep(2)
  report['preflight']='ready'
  # Use the exact delivered provisioning script, with its output under this
  # temporary source layout so the main environment's human accounts stay intact.
  seed=private/'ops/a7-p5/seed-delivery.py';seed.parent.mkdir(parents=True)
  shutil.copy2(ROOT/'ops/a7-p5/seed-delivery.py',seed)
  run(['python3',str(seed)],env={**os.environ,'A7P6_API_CONTAINER':api})
  fixture=json.loads((seed.parent/'.runtime-delivery.json').read_text())
  auth=fixture['personas']['creator_planner']['access']
  # The provisioned demonstration already has activities, so safe replacement
  # correctly refuses it. Use an actual API-created empty draft for import.
  def json_request(url, data, method='POST'):
   request=urllib.request.Request(url,data=json.dumps(data).encode(),method=method,headers={'Authorization':'Bearer '+auth,'Content-Type':'application/json'})
   with opener.open(request,timeout=30) as response:return json.load(response)
  created=json_request('http://127.0.0.1:18010/api/v1/projects/',{'project_code':'A7SMOKE-'+uuid4().hex[:12],'project_name':'Fresh release native MPP','employer':'Acceptance','start_date':'2026-01-01'})
  pid=created.get('project_id') or created['id']
  json_request(f'http://127.0.0.1:18010/api/v1/projects/{pid}/kickoff-charter/',{k:'Fresh installation '+k for k in ['justification','success_criteria','constraints','assumptions','key_stakeholders_summary','pm_authority']},method='PUT')
  report['fresh_project_created_via_api']=True
  boundary='A7'+uuid4().hex
  content=[]
  for key,value in [('replace','false'),('request_id',str(uuid4())),('intent','new')]:
   content += [f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode()]
  content += [f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="plan.mpp"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode(),(ROOT/'real-data/plan.mpp').read_bytes(),f'\r\n--{boundary}--\r\n'.encode()]
  base=f'http://127.0.0.1:18010/api/v1/projects/{pid}/import/msp/'
  request=urllib.request.Request(base,data=b''.join(content),headers={'Authorization':'Bearer '+auth,'Content-Type':'multipart/form-data; boundary='+boundary})
  with opener.open(request,timeout=90) as response:
   assert response.status==202
   task=json.load(response)['task_id']
  deadline=time.monotonic()+180
  while True:
   request=urllib.request.Request(base+'status/'+task+'/',headers={'Authorization':'Bearer '+auth})
   with opener.open(request,timeout=10) as response:result=json.load(response)
   if result['status'] in ['done','failed']:break
   assert time.monotonic()<deadline,result['status']
   time.sleep(1)
  assert result['status']=='done',result
  code=f"import json;from projects.models import WBS,Activity,ActivityRelation,ProjectKickoffCharter;from schedule.models import BaselineSchedule;print(json.dumps([WBS.objects.filter(project_id='{pid}',is_deleted=False).count(),Activity.objects.filter(project_id='{pid}',is_deleted=False).count(),ActivityRelation.objects.filter(predecessor__project_id='{pid}',is_deleted=False).count(),BaselineSchedule.objects.filter(project_id='{pid}').count(),ProjectKickoffCharter.objects.filter(project_id='{pid}').count()]))"
  counts=json.loads(run(compose+['exec','-T','api','python','manage.py','shell','-c',code],capture_output=True).stdout.strip().splitlines()[-1])
  assert counts==[6,72,72,1,1],counts
  report.update(status='pass',counts={'wbs':6,'activities':72,'relations':72,'working_baselines':1,'charters':1},human_personas_provisioned=5,native_mpp_job=task,api_image_digest=run(['docker','inspect',api,'--format','{{.Image}}'],capture_output=True).stdout.strip())
 finally:
  if started:subprocess.run(compose+['down','-v','--remove-orphans'],cwd=ROOT,check=False)
  if mounted:run(['sudo','umount',str(scratch)])
  if scratch.exists():run(['sudo','rmdir',str(scratch)])
  report['disposable_stack_removed']=not bool(run(['docker','ps','-aq','--filter',f'label=com.docker.compose.project={project}'],capture_output=True).stdout.strip())
  (E/'fresh-start.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'counts':report.get('counts'),'disposable_stack_removed':report['disposable_stack_removed']}))
