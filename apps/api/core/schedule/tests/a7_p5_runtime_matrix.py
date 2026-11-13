"""Real acceptance scenarios. Requires private phase DB, worker and shared controls."""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.utils import timezone
from rest_framework.test import APIClient

from projects.models import Activity, ActivityRelation, Project, ProjectStatus, WBS
from projects.services import create_project_with_creator
from schedule.models import ImportProcessingSlot, MspImportJob, P6ImportJob
from schedule.services.import_operations import run_maintenance
from schedule.services.import_process import reconcile_abandoned_scratch, acquire_slot, release_slot
from schedule.tasks import run_msp_import_task, run_p6_import_task, purge_import_originals, reconcile_import_jobs

XML = b'''<Project xmlns="http://schemas.microsoft.com/project"><Tasks><Task><UID>1</UID><Name>Package</Name><OutlineLevel>1</OutlineLevel><OutlineNumber>1</OutlineNumber><WBS>1</WBS><Summary>1</Summary></Task><Task><UID>2</UID><Name>Work</Name><OutlineLevel>2</OutlineLevel><OutlineNumber>1.1</OutlineNumber><WBS>1.1</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration></Task></Tasks></Project>'''

XER = b'ERMHDR\t18.8\t2024-01-01\tProject\n%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\tseq_num\n%R\t1\t\t1\tProject Root\t1\n%R\t2\t1\t1.1\tPhase 1\t2\n%T\tTASK\n%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt\n%R\t100\t2\tA100\tExcavation\t40\n%T\tTASKPRED\n%F\ttask_id\tpred_task_id\tpred_type\tlag_hr_cnt\n'


class RuntimeMatrix:
    def __init__(self, prefix, reference):
        assert 'a7p5' in str(connection.settings_dict['NAME']) and os.environ.get('A7_P5_ISOLATED') == '1'
        assert not settings.CELERY_TASK_ALWAYS_EAGER and not settings.IMPORT_PREPARE_INLINE
        self.prefix = prefix
        self.reference = Path(reference or '/fixtures/plan.mpp')
        self.control = Path(os.environ['A7_P5_FAULT_DIR'])
        self.control.mkdir(mode=0o700, exist_ok=True)
        for path in self.control.glob('arm-*'):
            path.unlink()
        self.evidence = {}
        self.user = self._user()
        self.client = APIClient(); self.client.force_authenticate(self.user)

    def _user(self):
        from master_data.models import Permission, Role, RolePermission
        from permissions.constants import DEFAULT_ROLE_PERMISSIONS, PERMISSIONS
        role, _ = Role.objects.get_or_create(role_name='project_manager')
        for code, label in PERMISSIONS.items():
            Permission.objects.get_or_create(codename=code, defaults={'label': label})
        for code in DEFAULT_ROLE_PERMISSIONS['project_manager']:
            RolePermission.objects.get_or_create(role=role, permission_codename=code)
        key = uuid.uuid4().hex[:10]
        return get_user_model().objects.create_user(username='a7p5-'+key, mobile='+199'+str(int(key,16))[:11], full_name='A7P5 verification', password=uuid.uuid4().hex)

    def project(self):
        p = create_project_with_creator(creator=self.user, project_code=self.prefix+uuid.uuid4().hex[:10], project_name='A7P5 isolated acceptance', employer='A7P5', start_date='2026-01-01')
        p.status=ProjectStatus.ACTIVE;p.save(update_fields=['status','updated_at']);return p

    def counts(self,p):
        return [WBS.objects.filter(project=p,is_deleted=False).count(),Activity.objects.filter(project=p,is_deleted=False).count(),ActivityRelation.objects.filter(predecessor__project=p,is_deleted=False).count()]

    def post(self,p,body=XML,name='plan.xml',**fields):
        return self.client.post(f'/api/v1/projects/{p.id}/import/msp/',{'file':SimpleUploadedFile(name,body,content_type='application/octet-stream' if name.endswith('.mpp') else 'application/xml'),'replace':'false','intent':'new',**fields},format='multipart')

    def started(self,p,body=XML,name='plan.xml',**fields):
        response=self.post(p,body,name,**fields)
        assert response.status_code==202,(response.status_code,str(response.data)[:200])
        return MspImportJob.objects.get(pk=response.data['task_id'])

    def wait(self,job,terminal=True,timeout=100):
        until=time.monotonic()+timeout
        while time.monotonic()<until:
            job.refresh_from_db()
            if (job.status in ('done','failed'))==terminal:return job
            time.sleep(.1)
        raise AssertionError('job deadline '+str(job.id)+' '+job.status)

    def arm(self,stage,mode='pause'):
        reached=self.control/('reached-'+stage)
        reached.unlink(missing_ok=True)
        (self.control/('arm-'+stage)).write_text(mode)

    def reached(self,stage,timeout=35):
        until=time.monotonic()+timeout
        while time.monotonic()<until:
            path=self.control/('reached-'+stage)
            if path.exists():return json.loads(path.read_text())
            time.sleep(.05)
        raise AssertionError('stage not reached '+stage)

    def release(self,stage):
        (self.control/('arm-'+stage)).unlink(missing_ok=True)

    def healthy(self):
        p=self.project();j=self.wait(self.started(p));assert j.status=='done',(j.error_code,j.error_message)
        assert self.counts(p)[:2]==[1,1],self.counts(p)
        return str(j.id)

    def expire_interrupted(self,j):
        # Controlled timestamps accelerate only this disposable failed-worker case.
        MspImportJob.objects.filter(pk=j.pk,status='running').update(execution_deadline_at=timezone.now()-timedelta(seconds=1))
        for slot in ImportProcessingSlot.objects.exclude(execution_token=None):
            path=Path(settings.IMPORT_SCRATCH_ROOT)/str(slot.execution_token)/'manifest.json'
            if path.exists():
                data=json.loads(path.read_text());data['deadline']=(timezone.now()-timedelta(seconds=1)).isoformat();path.write_text(json.dumps(data))
        cleanup=reconcile_abandoned_scratch()
        result=reconcile_import_jobs.delay().get(timeout=30)
        return cleanup,result

    def valid_native(self):
        data=self.reference.read_bytes();before=hashlib.sha256(data).hexdigest();p=self.project()
        preview=self.client.post(f'/api/v1/projects/{p.id}/import/msp/preview/',{'file':SimpleUploadedFile('plan.mpp',data,content_type='application/octet-stream')},format='multipart')
        assert preview.status_code==200,preview.data
        assert self.counts(p)==[0,0,0]
        j=self.wait(self.started(p,data,'plan.mpp'));assert j.status=='done',(j.error_code,j.error_message)
        assert all(n>0 for n in self.counts(p)),self.counts(p)
        assert j.result['relations_created']==self.counts(p)[2]
        assert j.result['wbs_nodes_created']==self.counts(p)[0]
        assert j.result['activities_created']==self.counts(p)[1]
        assert hashlib.sha256(self.reference.read_bytes()).hexdigest()==before
        self.arm('helper','cli')
        cli_project=self.project();cli_job=self.wait(self.started(cli_project,data,'plan.mpp'))
        assert cli_job.status=='done',(cli_job.error_code,cli_job.error_message)
        assert self.counts(cli_project)==self.counts(p)
        p6=self.project()
        preview6=self.client.post(f'/api/v1/projects/{p6.id}/import/p6/preview/',{'file':SimpleUploadedFile('plan.xer',XER,content_type='application/octet-stream')},format='multipart')
        assert preview6.status_code==200,preview6.data
        start6=self.client.post(f'/api/v1/projects/{p6.id}/import/p6/',{'file':SimpleUploadedFile('plan.xer',XER,content_type='application/octet-stream'),'replace':'false','intent':'new'},format='multipart')
        assert start6.status_code==202,start6.data
        job6=self.wait(P6ImportJob.objects.get(pk=start6.data['task_id']))
        assert job6.status=='done' and self.counts(p6)[1]>0,job6.error_code
        return {'job':str(j.id),'counts':self.counts(p),'source_sha256':before,'result':j.result,'cli_fallback_job':str(cli_job.id),'cli_counts':self.counts(cli_project),'p6_job':str(job6.id),'p6_counts':self.counts(p6)}

    def unreadable(self):
        cases=[]
        samples=[('bad.xml',b'<not-project/>','msp_invalid_xml'),('readme.txt',b'not a schedule','invalid_file_type')]
        fixtures=Path(settings.BASE_DIR)/'schedule/tests/fixtures/mpp'
        for name in ['password-protected.mpp','truncated-ole.mpp','renamed-not-mpp.mpp']:
            samples.append((name,(fixtures/name).read_bytes(),None))
        for name,body,expected in samples:
            p=self.project();r=self.post(p,body,name)
            assert r.status_code==400,r.data
            assert not MspImportJob.objects.filter(project=p).exists() and self.counts(p)==[0,0,0]
            code=r.data['error']['code']
            if expected:assert code==expected,(name,code)
            if name=='password-protected.mpp':assert code=='mpp_password_protected',code
            cases.append({'fixture':name,'bytes':len(body),'http_status':r.status_code,'code':code})
        limit=50*1024*1024
        p=self.project();large=XML+b' '*(limit-len(XML))
        job=self.wait(self.started(p,large));assert job.status=='done',job.error_code
        rejected=self.post(self.project(),large+b' ')
        assert rejected.status_code==400 and rejected.data['error']['code']=='file_too_large',rejected.data
        return {'rejections':cases,'maximum_admitted_bytes':len(large),'maximum_job':str(job.id),'oversized_rejected':True,'healthy_follow_up':self.healthy()}

    def admitted_failure(self):
        p=self.project();self.arm('before_prepare');j=self.started(p,self.reference.read_bytes(),'plan.mpp');self.reached('before_prepare')
        from master_data.models import ProjectMember, MemberStatus
        ProjectMember.objects.filter(project=p, user=self.user).update(status=MemberStatus.SUSPENDED)
        self.release('before_prepare');self.wait(j);assert j.status=='failed' and self.counts(p)==[0,0,0]
        return {'job':str(j.id),'error_code':j.error_code,'healthy_follow_up':self.healthy()}

    def duplicate_delivery(self):
        cases=[]
        for family in ('msp','p6'):
            p=self.project();self.arm('before_prepare')
            model=MspImportJob if family=='msp' else P6ImportJob
            task=run_msp_import_task if family=='msp' else run_p6_import_task
            def post(project):
                if family=='msp':return self.post(project)
                return self.client.post(f'/api/v1/projects/{project.id}/import/p6/',{'file':SimpleUploadedFile('plan.xer',XER),'replace':'false','intent':'new'},format='multipart')
            response=post(p);assert response.status_code==202,response.data
            j=model.objects.get(pk=response.data['task_id']);self.reached('before_prepare')
            slot=acquire_slot(family='preview',subject_id=uuid.uuid4(),deadline=timezone.now()+timedelta(seconds=30))
            try:
                duplicate=post(p);assert duplicate.status_code==202 and duplicate.data['task_id']==str(j.id)
                busy=post(self.project());assert busy.status_code==503,busy.data
            finally:release_slot(slot)
            task.apply_async(args=[str(j.id)],queue=settings.IMPORT_EXECUTION_QUEUE)
            self.release('before_prepare');self.wait(j);assert j.status=='done'
            first=self.counts(p);anchor=j.completed_at
            task.apply_async(args=[str(j.id)],queue=settings.IMPORT_EXECUTION_QUEUE).get(timeout=30)
            j.refresh_from_db();assert self.counts(p)==first and j.completed_at==anchor
            cases.append({'family':family,'job':str(j.id),'committed_counts':first,'same_inflight_id':True,'immutable_completion':True})
        return {'cases':cases}

    def helper_failure(self,mode):
        p=self.project();self.arm('before_prepare');j=self.started(p);self.reached('before_prepare')
        self.arm('helper',mode);self.release('before_prepare');self.reached('helper')
        if mode=='kill-parent':
            time.sleep(2);cleanup,recovery=self.expire_interrupted(j)
        self.wait(j,timeout=100)
        assert j.status=='failed' and self.counts(p)==[0,0,0],(j.status,j.error_code,self.counts(p))
        expected={'memory':'processing_resource_limit','pids':'processing_resource_limit','output':'processing_resource_limit','disk':'processing_resource_limit','sleep':'processing_timeout','kill-parent':'processing_interrupted'}[mode]
        assert j.error_code==expected,j.error_code
        assert not list(Path(settings.IMPORT_SCRATCH_ROOT).glob('*/manifest.json'))
        return {'job':str(j.id),'error_code':j.error_code,'helper_mode':mode,'healthy_follow_up':self.healthy()}

    def resources(self):
        cases=[self.helper_failure(mode) for mode in ['memory','pids','output','disk']]
        synchronous=[]
        for preview in (True, False):
            project=self.project();self.arm('helper','output');started=time.monotonic()
            route=f'/api/v1/projects/{project.id}/import/msp/' + ('preview/' if preview else '')
            response=self.client.post(route,{'file':SimpleUploadedFile('plan.xml',XML,content_type='application/xml'),'replace':'false'},format='multipart')
            assert response.status_code==400 and response.data['error']['code']=='processing_resource_limit',response.data
            assert not MspImportJob.objects.filter(project=project).exists()
            synchronous.append({'path':'preview' if preview else 'start','elapsed_seconds':time.monotonic()-started,'code':'processing_resource_limit'})
        p=self.project()
        heavy=b'<Project xmlns="http://schemas.microsoft.com/project"><Tasks>'+b'<Task><UID>2</UID><Name>Heavy</Name><OutlineLevel>1</OutlineLevel><WBS>1</WBS><Summary>1</Summary></Task>'*20001+b'</Tasks></Project>'
        response=self.post(p,heavy)
        assert response.status_code==400 and response.data['error']['code']=='processing_resource_limit',response.data
        assert not MspImportJob.objects.filter(project=p).exists()
        return {'cases':cases,'synchronous':synchronous,'heavy_source_bytes':len(heavy),'heavy_input_rejected_without_job':True,'healthy_follow_up':self.healthy()}

    def drain_cohort(self, kind, identities):
        # Hold one actual PostgreSQL row lock, admit a later row after the
        # snapshot, and compete with the independently running maintainer.
        import threading
        from django.db import connections, transaction
        model, pk = identities[0]
        locked = threading.Event(); unlock = threading.Event()
        def hold():
            try:
                with transaction.atomic():
                    model.objects.select_for_update().get(pk=pk)
                    locked.set(); unlock.wait(15)
            finally:
                connections.close_all()
        thread=threading.Thread(target=hold);thread.start()
        assert locked.wait(5)
        stage='maintenance-'+kind;self.arm(stage)
        task=reconcile_import_jobs if kind=='recovery' else purge_import_originals
        result=task.delay();self.reached(stage)
        now=timezone.now()
        later=MspImportJob.objects.create(project=self.project(),created_by=self.user,status='pending' if kind=='recovery' else 'failed',file_data=XML,dispatch_deadline_at=now-timedelta(seconds=1),retention_anchor_at=now-timedelta(hours=169),retention_anchor_source='terminal',task_id=str(uuid.uuid4()))
        competing=run_maintenance(kind)
        assert competing['status']=='blocked',competing
        self.release(stage)
        time.sleep(.4);unlock.set();thread.join(5)
        drained=result.get(timeout=40)
        assert drained['status']=='ok' and drained['n']>=201,drained
        assert drained['elapsed_seconds']<drained['bound_seconds']
        assert str(pk) in drained['processed_ids']
        later.refresh_from_db()
        assert later.status=='pending' if kind=='recovery' else later.file_data is not None
        next_result=task.delay().get(timeout=30)
        later.refresh_from_db()
        assert later.status=='failed' if kind=='recovery' else later.file_data is None
        return {'drain':drained,'competing':competing,'later_cohort':next_result,'locked_row_revisited':True,'new_arrival_deferred':True}

    def worker_loss(self):
        cases=[]
        for family in ('msp','p6'):
            task=run_msp_import_task if family=='msp' else run_p6_import_task
            model=MspImportJob if family=='msp' else P6ImportJob
            for stage in ['before_apply','after_domain_write','after_commit','during_failure_recording']:
                p=self.project()
                if stage=='during_failure_recording':self.arm('before_prepare')
                else:self.arm(stage,'kill')
                if family=='msp':j=self.started(p)
                else:
                    response=self.client.post(f'/api/v1/projects/{p.id}/import/p6/',{'file':SimpleUploadedFile('plan.xer',XER),'replace':'false','intent':'new'},format='multipart')
                    assert response.status_code==202,response.data
                    j=model.objects.get(pk=response.data['task_id'])
                if stage=='during_failure_recording':
                    self.reached('before_prepare')
                    from master_data.models import ProjectMember,MemberStatus
                    ProjectMember.objects.filter(project=p,user=self.user).update(status=MemberStatus.SUSPENDED)
                    self.arm(stage,'kill');self.release('before_prepare')
                self.reached(stage);time.sleep(2);j.refresh_from_db()
                if stage=='after_commit':
                    assert j.status=='done' and self.counts(p)[1]>0
                    counts=self.counts(p);task.apply_async(args=[str(j.id)],queue=settings.IMPORT_EXECUTION_QUEUE).get(timeout=30)
                    assert self.counts(p)==counts
                else:
                    assert self.counts(p)==[0,0,0]
                    model.objects.filter(pk=j.pk,status='running').update(execution_deadline_at=timezone.now()-timedelta(seconds=1))
                    reconcile_import_jobs.delay().get(timeout=30);self.wait(j);assert j.status=='failed'
                cases.append({'family':family,'stage':stage,'job':str(j.id),'status':j.status,'counts':self.counts(p),'healthy_follow_up':self.healthy()})
        cases.append(self.helper_failure('kill-parent'))
        bulk=self.project();now=timezone.now();identities=[]
        for i in range(201):
            model=MspImportJob if i%2==0 else P6ImportJob
            row=model.objects.create(project=bulk,created_by=self.user,filename='aged.xml',status='running' if i%3==0 else 'pending',file_data=XML,queued_at=now-timedelta(minutes=10),dispatch_deadline_at=now-timedelta(minutes=5),execution_deadline_at=now-timedelta(seconds=1),execution_token=uuid.uuid4(),task_id=str(uuid.uuid4()))
            identities.append((model,row.pk))
        drained=self.drain_cohort('recovery',identities)
        for model,pk in identities:
            row=model.objects.get(pk=pk);assert row.status=='failed' and bytes(row.file_data)==XML
        assert self.counts(bulk)==[0,0,0]
        return {'cases':cases,'bulk_aged_jobs':201,'bulk_maintenance':drained,'clock_acceleration':'disposable aged-job fixtures; execution/manifest timestamps advanced only after confirmed SIGKILL'}

    def expiry(self):
        p=self.project();now=timezone.now();raw=b'a7p5-retained-source';digest=hashlib.sha256(raw).hexdigest()
        ids=[]
        for i in range(201):
            model=MspImportJob if i%2==0 else P6ImportJob
            j=model.objects.create(project=p,created_by=self.user,filename='retained.xml',status='failed',file_data=raw,source_sha256=digest,source_size=len(raw),completed_at=now-timedelta(hours=169),retention_anchor_at=now-timedelta(hours=169),retention_anchor_source='terminal',result={'marker':'kept'})
            ids.append((model,j.pk))
        active=MspImportJob.objects.create(project=p,created_by=self.user,status='pending',file_data=raw,dispatch_deadline_at=now+timedelta(minutes=5))
        unexpired=MspImportJob.objects.create(project=p,created_by=self.user,status='failed',file_data=raw,completed_at=now,retention_anchor_at=now,retention_anchor_source='terminal')
        result=self.drain_cohort('purge',ids)
        for model,id in ids:
            j=model.objects.get(pk=id);assert j.file_data is None and j.source_sha256==digest and j.result=={'marker':'kept'}
        for j in [active,unexpired]:j.refresh_from_db();assert bytes(j.file_data)==raw
        again=purge_import_originals.delay().get(timeout=30);assert again['status']=='ok'
        active.status='failed';active.completed_at=now;active.retention_anchor_at=now;active.retention_anchor_source='terminal';active.save()
        return {'expired_count':201,'both_families':True,'preserved_active_and_unexpired':True,'maintenance':result,'repeated':again}

    def cleanup(self):
        root=Path(settings.IMPORT_SCRATCH_ROOT);unrelated=root/'unrelated-a7p5.txt';unrelated.write_text('preserve')
        from schedule.services.import_process import hostname,reboot_id
        tokens=[]
        for _ in range(201):
            token=str(uuid.uuid4());tokens.append(token);workspace=root/token;workspace.mkdir(mode=0o700)
            (workspace/'manifest.json').write_text(json.dumps({'token':token,'deadline':(timezone.now()-timedelta(seconds=1)).isoformat(),'host':hostname(),'reboot_id':reboot_id()}))
            (workspace/'input.bin').write_bytes(b'disposable')
        try:
            started=time.monotonic();result=reconcile_abandoned_scratch();elapsed=time.monotonic()-started
            assert unrelated.read_text()=='preserve'
            assert all(not (root/token).exists() for token in tokens)
            assert not list(root.glob('*/manifest.json'))
            return {'result':result,'scratch_cohort':201,'elapsed_seconds':elapsed,'unrelated_preserved':True,'healthy_follow_up':self.healthy()}
        finally:unrelated.unlink(missing_ok=True)

    def _family_start(self, project, family, **fields):
        if family == 'msp':
            return self.post(project, **fields)
        payload = {'file': SimpleUploadedFile('plan.xer', XER, content_type='application/octet-stream'), 'replace': 'false', 'intent': 'new', **fields}
        return self.client.post(f'/api/v1/projects/{project.id}/import/p6/', payload, format='multipart')

    def request_intent(self):
        """Live intake linkage: retry needs a visible failed predecessor; new forbids one."""
        observed = []
        for family, model in (('msp', MspImportJob), ('p6', P6ImportJob)):
            project = self.project()
            predecessor = model.objects.create(
                project=project, created_by=self.user, filename='failed.xml', status='failed',
                error_code='import_failed', error_message='The import was not completed.',
                completed_at=timezone.now(), retention_anchor_at=timezone.now(), retention_anchor_source='terminal',
            )
            missing = self._family_start(project, family, intent='retry')
            forbidden = self._family_start(project, family, intent='new', retry_of=str(predecessor.pk))
            assert missing.status_code == 400 and missing.data['error']['code'] == 'import_failed', missing.data
            assert forbidden.status_code == 400 and forbidden.data['error']['code'] == 'import_failed', forbidden.data
            assert model.objects.filter(project=project).count() == 1
            accepted = self._family_start(project, family, intent='retry', retry_of=str(predecessor.pk))
            assert accepted.status_code == 202, accepted.data
            job = model.objects.get(pk=accepted.data['task_id'])
            assert job.pk != predecessor.pk and job.retry_of_id == predecessor.pk
            self.wait(job)
            assert job.status == 'done', (family, job.error_code, job.error_message)
            observed.append({'family': family, 'predecessor': str(predecessor.pk), 'retry_job': str(job.pk), 'missing_rejected': True, 'new_with_predecessor_rejected': True})
        return {'cases': observed}

    def maintenance_budget(self):
        from schedule.services.import_operations import admission_closed, mark_catchup_complete
        previous = settings.IMPORT_ADMISSION_REQUIRES_CATCHUP
        settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
        mark_catchup_complete()
        project = self.project()
        job = MspImportJob.objects.create(
            project=project, created_by=self.user, filename='budget.xml', status='pending',
            dispatch_deadline_at=timezone.now() - timedelta(minutes=1), task_id='a7p5-budget-observation',
        )
        calls = {'count': 0}

        def clock():
            calls['count'] += 1
            return 0 if calls['count'] < 3 else 100

        try:
            result = run_maintenance('recovery', now=timezone.now(), monotonic=clock, sleeper=lambda _seconds: None)
            closed = admission_closed()
            assert result['status'] == 'failed' and closed, result
            return {'job': str(job.id), 'status': result['status'], 'reason': result.get('reason'), 'n': result.get('n'), 'admission_closed': True}
        finally:
            mark_catchup_complete()
            settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = previous

    def scratch_quarantine(self):
        root = Path(settings.IMPORT_SCRATCH_ROOT)
        quarantined = uuid.UUID('00000000-0000-4000-8000-0000000000a7')
        later = uuid.UUID('ffffffff-ffff-4fff-bfff-0000000000a7')
        slot = ImportProcessingSlot.objects.get(slot_number=1)
        saved = {
            'execution_token': slot.execution_token, 'quarantined': slot.quarantined,
            'containment_id': slot.containment_id, 'owner_host': slot.owner_host,
            'reboot_id': slot.reboot_id, 'family': slot.family, 'subject_id': slot.subject_id,
            'deadline': slot.deadline,
        }
        held = root / str(quarantined)
        try:
            slot.execution_token = quarantined
            slot.quarantined = True
            slot.containment_id = 'cgroup:/outside/import-leaked'
            slot.owner_host = 'other-host'
            slot.reboot_id = 'other-boot'
            slot.family = ''
            slot.subject_id = None
            slot.deadline = timezone.now() - timedelta(seconds=5)
            slot.save()
            for token, payload in ((quarantined, b'quarantine-owned'), (later, b'later-owned')):
                work = root / str(token)
                work.mkdir(mode=0o700)
                (work / 'manifest.json').write_text(json.dumps({'token': str(token), 'deadline': (timezone.now() - timedelta(seconds=5)).isoformat()}))
                (work / 'input.bin').write_bytes(payload)
            result = reconcile_abandoned_scratch()
            assert result['status'] == 'failed' and result['reason'] == 'unverified', result
            assert result['unfinished'] == [str(quarantined)]
            assert (held / 'input.bin').read_bytes() == b'quarantine-owned'
            assert not (root / str(later)).exists()
            slot.refresh_from_db()
            assert slot.quarantined is True and slot.execution_token == quarantined
            return {'quarantined_token': str(quarantined), 'later_removed': True, 'slot_kept': True, 'unfinished': result['unfinished']}
        finally:
            try:
                for token in (quarantined, later):
                    work = root / str(token)
                    if work.is_dir() and not work.is_symlink():
                        for child in work.iterdir():
                            if child.is_file() and not child.is_symlink():
                                child.unlink()
                        work.rmdir()
            finally:
                ImportProcessingSlot.objects.filter(pk=slot.pk).update(**saved)
                # The failed quarantine pass closes restart admission. Reopen it
                # after the observation so the following healthy import can start.
                from schedule.services.import_operations import mark_catchup_complete
                mark_catchup_complete()

    def run(self):
        checks={'valid_native':self.valid_native,'unreadable':self.unreadable,'admitted_failure':self.admitted_failure,'duplicate_delivery':self.duplicate_delivery,'timeout':lambda:self.helper_failure('sleep'),'resource_limit':self.resources,'worker_loss':self.worker_loss,'expiry':self.expiry,'cleanup':self.cleanup,'request_intent':self.request_intent,'maintenance_budget':self.maintenance_budget,'scratch_quarantine':self.scratch_quarantine,'healthy_follow_up':lambda:{'job':self.healthy()}}
        for name,callback in checks.items():
            try:
                self.evidence[name]={'status':'pass','observed':callback()}
                print('A7P5_CASE '+name+' pass',flush=True)
            except Exception as exc:
                self.evidence[name]={'status':'fail','exception_type':type(exc).__name__,'reason':str(exc)[:300]}
                for path in self.control.glob('arm-*'):path.unlink()
                print('A7P5_CASE '+name+' fail '+type(exc).__name__+' '+str(exc)[:160],flush=True)
                break
        return self.evidence
