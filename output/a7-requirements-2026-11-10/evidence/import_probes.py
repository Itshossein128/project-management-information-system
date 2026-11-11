"""Read-only-to-product audit; runs against a dedicated ephemeral Django test DB.

These observations describe current behavior, not acceptance-test passes.
"""
import json
from pathlib import Path
import pytest
import importlib.util
_fixture_spec = importlib.util.spec_from_file_location('a7_root_fixtures', Path('/home/hossein/Desktop/projects/building-management/apps/api/core/conftest.py'))
_fixtures = importlib.util.module_from_spec(_fixture_spec)
_fixture_spec.loader.exec_module(_fixtures)
user = _fixtures.user
project_manager_role = _fixtures.project_manager_role
project = _fixtures.project
auth_client = _fixtures.auth_client
api_client = _fixtures.api_client
test_cache_backend = _fixtures.test_cache_backend

OUT = Path(__file__).parent

def xml_task(uid, code, name, summary=False, preds='', extra=''):
    return f'<Task><UID>{uid}</UID><Name>{name}</Name><OutlineLevel>{len(code.split("."))}</OutlineLevel><OutlineNumber>{code}</OutlineNumber><WBS>{code}</WBS><Summary>{int(summary)}</Summary>{preds}{extra}</Task>'

def xml(*tasks):
    return ('<?xml version="1.0" encoding="UTF-8"?><Project><Tasks>'+''.join(tasks)+'</Tasks></Project>').encode()

def pred(uid, lag=0):
    return f'<PredecessorLink><PredecessorUID>{uid}</PredecessorUID><Type>1</Type><LinkLag>{lag}</LinkLag></PredecessorLink>'

@pytest.mark.django_db
def test_observe_import_boundaries(project, user, auth_client, settings):
    from projects.models import Activity, ActivityRelation, WBS
    from schedule.models import BaselineSchedule, BaselineActivity
    from schedule.services.msp_import import execute_msp_import, parse_msp_family, parse_msp_xml, build_preview
    from schedule.services.p6_import import execute_p6_import, parse_p6_xer
    from django.core.files.uploadedfile import SimpleUploadedFile
    settings.CELERY_TASK_ALWAYS_EAGER = True
    observations = {}
    payload = xml(xml_task(1,'1','Root',True), xml_task(2,'1.1','A',preds=pred(3,4800),extra='<Duration>PT8H0M0S</Duration><Start>2026-01-03T08:00:00</Start><Finish>2026-01-01T17:00:00</Finish>'),xml_task(3,'1.2','Milestone',preds=pred(2),extra='<Duration>PT0H0M0S</Duration><Milestone>1</Milestone>'))
    first = execute_msp_import(project,payload,filename='audit.xml',user=user)
    observations['cyclic_invalid_dates_import'] = first
    observations['persisted_relations'] = list(ActivityRelation.objects.filter(predecessor__project=project).values('predecessor__activity_code','successor__activity_code','lag_days'))
    observations['persisted_activity_fields'] = list(Activity.objects.filter(project=project).values('activity_code','duration_days','is_milestone','working_calendar_id','planned_start','planned_finish'))
    first_baseline = BaselineSchedule.objects.get(project=project,is_current=True)
    first_baseline.is_locked=True
    first_baseline.save(update_fields=['is_locked'])
    first_rows = BaselineActivity.objects.filter(baseline=first_baseline).count()
    second = execute_msp_import(project,payload,filename='audit-repeat.xml',user=user)
    observations['repeat']={'result':second,'baseline_count':BaselineSchedule.objects.filter(project=project).count()}
    before_ids = list(Activity.all_objects.filter(project=project).values_list('id',flat=True))
    replacement=xml(xml_task(1,'1','Root',True),xml_task(4,'1.3','Replacement'))
    observations['replacement_result']=execute_msp_import(project,replacement,filename='audit-replace.xml',replace=True,user=user)
    observations['replacement_history']={'locked_baseline_exists':BaselineSchedule.objects.filter(pk=first_baseline.pk).exists(),'locked_baseline_rows_before':first_rows,'locked_baseline_rows_after':BaselineActivity.objects.filter(baseline=first_baseline).count(),'old_activities_including_deleted':Activity.all_objects.filter(pk__in=before_ids).count()}
    xer=b'ERMHDR\t18.8\t2024-01-01\tProject\n%T\tPROJWBS\n%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\tseq_num\n%R\t1\t\tP\tParent P\t1\n%R\t2\t\tQ\tParent Q\t2\n%R\t3\t1\tP-C\tChild of P\t3\n%T\tTASK\n%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt\n%R\t10\t3\tT10\tP activity\t0\n'
    observations['p6_zero_duration']=[{'code':t.wbs_code,'duration':t.duration_days} for t in parse_p6_xer(xer).tasks if not t.is_summary]
    observations['p6_result']=execute_p6_import(project,xer,filename='audit.xer',replace=True,user=user)
    pchild=WBS.objects.get(project=project,wbs_code='P-C')
    observations['p6_parent_mapping']={'expected':'P','actual':pchild.get_parent().wbs_code}
    
    real=Path('/home/hossein/Desktop/projects/building-management/real-data/plan.mpp')
    real_parsed=parse_msp_family(real.read_bytes(),filename=real.name)
    observations['real_mpp_import']=execute_msp_import(project,real.read_bytes(),filename=real.name,replace=True,user=user)
    observations['real_mpp_parsed_totals']={'summary_tasks':sum(t.is_summary for t in real_parsed.tasks),'leaf_activities':sum(not t.is_summary for t in real_parsed.tasks),'predecessor_links_in_parsed_source':sum(len(t.predecessors) for t in real_parsed.tasks)}
    from projects.lifecycle_service import archive
    archive(project,user)
    response=auth_client.post(f'/api/v1/projects/{project.id}/import/msp/',{'file':SimpleUploadedFile('archived.xml',replacement,content_type='application/xml')},format='multipart')
    observations['archived_project_import_http_status']=response.status_code
    observations['archived_project_import_response']=response.data
    try:
        real=Path('/home/hossein/Desktop/projects/building-management/real-data/plan.mpp')
        parsed=parse_msp_family(real.read_bytes(),filename=real.name)
        observations['real_mpp']={'parsed_tasks':len(parsed.tasks),'warnings':parsed.warnings,'leaf_activities':len(build_preview(parsed)['activities'])}
    except Exception as exc:
        observations['real_mpp']={'error_type':type(exc).__name__,'code':getattr(exc,'code',None),'message':str(exc)}
    (OUT/'import-probe-observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2,default=str))
    assert observations, 'Observations must have been recorded; this is not a product acceptance assertion.'
