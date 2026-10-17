import pytest
from uuid import uuid4
from django.utils import timezone
from audit.models import AuditLog
from master_data.models import ProjectMember, ProjectMemberPermissionOverride
from projects.models import ProjectArchiveRestore
from .archive_restore_helpers import actor, archived_project, client_for, base
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db
SAFE={'id','project_id','project_name','archive_cycle_id','request_id','actor','restored_at','reason','from_status','to_status'}


def test_history_scope_snapshots_and_safe_projection():
    owner=actor(admin=True);admin=actor(admin=True);p=archived_project(owner);c=client_for(admin)
    assert c.get(base(p)+'restore-history/').json()['results']==[]
    receipt=c.post(base(p)+'restore/',body(confirmation(c,p)),format='json').json()['receipt']
    viewer=actor();member=ProjectMember.objects.create(project=p,user=viewer,status='active')
    ProjectMemberPermissionOverride.objects.create(member=member,permission_codename='view_project',is_granted=True)
    assert client_for(viewer).get(base(p)+'restore-history/').status_code==200
    assert client_for(viewer).get(base(p)+'restore-preview/').status_code==403
    assert client_for(actor()).get(base(p)+'restore-history/').status_code in (403,404)
    p.project_name='Renamed now';p.save(update_fields=['project_name'])
    admin.delete()
    r=client_for(owner).get(base(p)+'restore-history/')
    assert r.status_code==200 and r['Cache-Control']=='no-store'
    assert r.json()['results']==[receipt] and set(receipt)==SAFE
    assert receipt['actor']['display_name']=='Restore administrator'
    assert receipt['reason'] and receipt['restored_at'] and receipt['from_status']=='archived' and receipt['to_status']=='active'
    assert receipt['project_name']!='Renamed now'


def test_history_pagination_order_and_no_generic_audit_disclosure():
    u=actor(admin=True);p=archived_project(u);c=client_for(u);now=timezone.now()
    ids=[]
    for _ in range(102):
        audit=AuditLog.objects.create(project=p,actor=u,http_method='POST',path='/restore/',changes={'secret':'must not leak'})
        row=ProjectArchiveRestore.objects.create(project=p,actor=u,actor_snapshot={'id':str(u.pk),'display_name':'A'},project_snapshot={'project_name':p.project_name},archive_cycle_id=uuid4(),request_id=uuid4(),request_fingerprint='a'*64,confirmation_version=1,reason='Correction',from_status='archived',to_status='completed',restored_at=now,audit_log=audit)
        ids.append(str(row.pk))
    from django.db import connection
    from django.test.utils import CaptureQueriesContext
    with CaptureQueriesContext(connection) as queries:
        first=c.get(base(p)+'restore-history/').json()
    receipt_queries=[q['sql'] for q in queries.captured_queries if 'projects_projectarchiverestore' in q['sql']]
    assert len(receipt_queries)==2  # COUNT + bounded page SELECT; no per-row actor or audit fetches
    assert first['count']==102 and len(first['results'])==50 and first['next'] and first['previous'] is None
    maximum=c.get(base(p)+'restore-history/?page_size=999').json()
    assert len(maximum['results'])==100
    second=c.get(base(p)+'restore-history/?page=2&page_size=100').json()
    assert len(second['results'])==2 and second['previous'] and second['next'] is None
    assert [r['id'] for r in maximum['results']+second['results']]==sorted(ids,reverse=True)
    assert all(set(r)==SAFE for r in maximum['results'])
