import threading,time
import pytest
from django.db import connection,close_old_connections,transaction
from rest_framework.test import APIClient
from decision_support.models import DecisionCase,DecisionRun
from decision_support.services.case_service import create_case,update_case
from decision_support.services.execution_service import create_run
from decision_support.tests.execution_records_fixtures import payload,METHODS

@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('action',list(METHODS)+['patch','delete'])
def test_actual_postgres_parent_wait(project,user,action):
    case=create_case(project.id,user,payload()); shared={}; started=threading.Event()
    def work():
        close_old_connections()
        try:
            with connection.cursor() as c:c.execute('SELECT pg_backend_pid()');shared['pid']=c.fetchone()[0]
            started.set()
            if action=='patch':shared['value']=update_case(case,user,{'title':'Targeted title'})
            elif action=='delete':
                client=APIClient();client.force_authenticate(user);shared['value']=client.delete(f'/api/v1/projects/{project.id}/decision-cases/{case.id}/')
            else:shared['value']=create_run(case,action,user)
        except BaseException as e:shared['error']=e
        finally:close_old_connections()
    waiting=False
    with transaction.atomic():
        locked=DecisionCase.objects.select_for_update().get(pk=case.pk)
        worker=threading.Thread(target=work);worker.start();assert started.wait(5)
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            with connection.cursor() as c:
                c.execute('SELECT pg_stat_clear_snapshot()')
                c.execute('SELECT wait_event_type,query FROM pg_stat_activity WHERE pid=%s',[shared['pid']]);row=c.fetchone()
            if row and row[0]=='Lock':waiting=True;shared['waiting_query']=row[1];break
            if 'value' in shared or 'error' in shared:break
            time.sleep(.01)
        locked.criteria=['Released cost','Released quality'];locked.save(update_fields=['criteria'])
    worker.join(5);assert not worker.is_alive();assert 'error' not in shared,shared.get('error')
    assert waiting,'Expected observed pg_stat_activity Lock wait on the authoritative parent'
    assert 'FOR UPDATE' in shared['waiting_query'].upper(),shared['waiting_query']
    if action=='patch':
        case.refresh_from_db();assert case.criteria==['Released cost','Released quality'];assert case.title=='Targeted title';assert case.dematel_matrix==[[0,None]]
    elif action=='delete':
        assert shared['value'].status_code==204;assert not DecisionCase.objects.filter(pk=case.pk).exists();assert not DecisionRun.objects.filter(case=case).exists()
    else:assert shared['value'].input_snapshot['criteria']==['Released cost','Released quality']

@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('method',METHODS)
@pytest.mark.parametrize('change',['selection','deleted'])
def test_execute_waits_then_rejects_released_ineligible_state(project,user,method,change):
    from django.http import Http404
    from config.exceptions import CodedValidationError
    case=create_case(project.id,user,payload()); shared={};started=threading.Event()
    def work():
        close_old_connections()
        try:
            with connection.cursor() as c:c.execute('SELECT pg_backend_pid()');shared['pid']=c.fetchone()[0]
            started.set();shared['run']=create_run(case,method,user)
        except BaseException as error:shared['error']=error
        finally:close_old_connections()
    waiting=False
    with transaction.atomic():
        locked=DecisionCase.objects.select_for_update().get(pk=case.pk)
        worker=threading.Thread(target=work);worker.start();assert started.wait(5)
        deadline=time.monotonic()+5
        while time.monotonic()<deadline:
            with connection.cursor() as c:
                c.execute('SELECT pg_stat_clear_snapshot()');c.execute('SELECT wait_event_type,query FROM pg_stat_activity WHERE pid=%s',[shared['pid']]);row=c.fetchone()
            if row and row[0]=='Lock' and 'FOR UPDATE' in row[1].upper():waiting=True;break
            if 'run' in shared or 'error' in shared:break
            time.sleep(.01)
        if change=='selection':locked.selected_methods=[];locked.save(update_fields=['selected_methods'])
        else:locked.soft_delete(user)
    worker.join(5);assert not worker.is_alive();assert waiting
    assert isinstance(shared.get('error'),CodedValidationError if change=='selection' else Http404),shared
    assert not DecisionRun.objects.filter(case_id=case.id).exists()
