import pytest
from uuid import uuid4
from django.db import IntegrityError
from projects.models import ProjectArchiveRestore
from .archive_restore_helpers import actor, archived_project, client_for, base
from .test_project_archive_restore import confirmation, body
pytestmark=pytest.mark.django_db


@pytest.mark.parametrize('language',['fa','en'])
def test_localized_actionable_errors_keep_machine_codes(monkeypatch,language):
    u=actor(admin=True);p=archived_project(u);c=client_for(u);c.defaults['HTTP_ACCEPT_LANGUAGE']=language
    preview=confirmation(c,p);payload=body(preview)
    cases=[]
    cases.append((c.post(base(p)+'restore/',{**payload,'reason':' '},format='json'),'reason_required',400))
    p.contract_amount=None;p.save(update_fields=['contract_amount'])
    preview=confirmation(c,p);payload=body(preview)
    cases.append((c.post(base(p)+'restore/',payload,format='json'),'activation_gates_failed',400))
    p.contract_amount=1000;p.save(update_fields=['contract_amount'])
    cases.append((c.post(base(p)+'restore/',payload,format='json'),'restore_context_changed',409))
    other=client_for(actor());other.defaults['HTTP_ACCEPT_LANGUAGE']=language
    cases.append((other.get(base(p)+'restore-preview/'),'permission_denied',403))
    preview=confirmation(c,p);payload=body(preview)
    def fail(*args,**kwargs):raise IntegrityError('injected rollback')
    monkeypatch.setattr(ProjectArchiveRestore.objects,'create',fail)
    cases.append((c.post(base(p)+'restore/',payload,format='json'),'restore_not_applied',503))
    for response,code,status in cases:
        assert response.status_code==status
        error=response.json()['error'];assert error['code']==code
        message=error['message'];assert len(message)>15
        assert any('\u0600'<=ch<='\u06ff' for ch in message)==(language=='fa'),message
    missing=c.get(f'/api/v1/projects/{uuid4()}/restore-preview/')
    assert missing.status_code==404
    assert c.get(base(p)+f'restore-attempts/{uuid4()}/').json()['outcome']=='not_recorded'
