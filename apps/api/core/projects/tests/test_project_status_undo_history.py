import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from projects.tests.status_undo_helpers import *
from projects.models import ProjectStatusUndo
from projects import status_undo_service as service
pytestmark=pytest.mark.django_db
SAFE={'id','project_id','project_name','operation','source_event_id','request_id','actor','performed_at','reason','from_status','to_status','source_event'}
SOURCE={'id','kind','from_status','to_status','occurred_at','actor','project_name'}

def apply(user,p):
    view=service.preview(p,user,'resume')
    return service.undo(p,user,'resume',request_id=uuid4(),confirmation_token=view['confirmation_token'],reason='Mistaken suspension')


def test_safe_projection_never_serializes_internal_snapshot_extensions():
    user=actor(admin=True);p=source_project(user);apply(user,p);receipt=p.status_undos.get()
    receipt.actor_snapshot['email']='PRIVATE';receipt.source_snapshot['internal']='PRIVATE';receipt.source_snapshot['actor']['phone']='PRIVATE'
    receipt.save(update_fields=['actor_snapshot','source_snapshot'])
    result=service.receipt_data(receipt)
    assert set(result['actor'])=={'id','display_name'} and set(result['source_event'])==SOURCE
    assert set(result['source_event']['actor'])=={'id','display_name'} and 'PRIVATE' not in str(result)


def test_history_view_only_scope_and_original_undo_snapshots_survive_rename_account_deletion():
    owner=actor(admin=True);undoer=actor(admin=True);p=source_project(owner);original=p.suspension_event
    result=apply(undoer,p);receipt=result['receipt']
    viewer=actor();member(viewer,p,'view_project');c=client_for(viewer)
    response=c.get(base(p)+'status-undo-history/');assert response.status_code==200,getattr(response,'data',response.content)
    assert response.data['results']==[receipt] and set(receipt)==SAFE
    assert receipt['source_event']['actor']['id']==str(owner.pk) and receipt['actor']['id']==str(undoer.pk)
    assert receipt['source_event']['occurred_at']==original.created_at.isoformat() and receipt['source_event']['from_status']=='active' and receipt['from_status']=='suspended'
    assert c.get(base(p)+'resume-preview/').status_code==403
    assert client_for(actor()).get(base(p)+'status-undo-history/').status_code==403
    p.project_name='Renamed after correction';p.save(update_fields=['project_name']);undoer.delete()
    response=c.get(base(p)+'status-undo-history/');assert response['Cache-Control']=='no-store' and response.data['results']==[receipt]
    assert receipt['project_name']!='Renamed after correction'
    source_id=original.pk;p.delete();original.refresh_from_db();assert original.pk==source_id and original.project_id is None


def test_history_order_pagination_and_query_bound_over_100_tied_times():
    user=actor(admin=True);p=ready_project(user);ids=[]
    for _ in range(103):
        p=lifecycle.suspend(p,user);result=apply(user,p);ids.append(result['receipt']['id']);p.refresh_from_db()
    ProjectStatusUndo.objects.filter(project=p).update(performed_at=timezone.now())
    c=client_for(user)
    with CaptureQueriesContext(connection) as queries:response=c.get(base(p)+'status-undo-history/')
    assert response.status_code==200,getattr(response,'data',response.content)
    receipt_queries=[q['sql'] for q in queries.captured_queries if 'projects_projectstatusundo' in q['sql']]
    assert len(receipt_queries)==2
    first=response.data;assert first['count']==103 and len(first['results'])==50 and first['next'] and not first['previous']
    maximum=c.get(base(p)+'status-undo-history/?page_size=999').data
    last=c.get(base(p)+'status-undo-history/?page=2&page_size=100').data
    assert len(maximum['results'])==100 and len(last['results'])==3
    assert [r['id'] for r in maximum['results']+last['results']]==sorted(ids,reverse=True)
    for query in ['page_size=0','page_size=-1','per_page=0']:
        bounded=c.get(base(p)+'status-undo-history/?'+query);assert bounded.status_code==200 and len(bounded.data['results'])<=100
