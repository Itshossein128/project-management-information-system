"""Identical operations from two connections produce one receipt (feature 037, T065)."""
import threading
from uuid import uuid4

import pytest

from sub_reports.models import DisciplineSubReport, OfflineOperationReceipt
from sub_reports.services.offline_sync import dispatch_operations

pytestmark = pytest.mark.django_db(transaction=True)


def test_concurrent_identical_replay_commits_once(project, user):
    user.is_superuser = True
    user.save(update_fields=['is_superuser'])
    operation = {
        'operation_id': str(uuid4()), 'local_report_id': str(uuid4()),
        'scope': {'kind': 'unit', 'unit': 'buildings', 'report_date': '2026-10-26', 'report_id': None},
        'action': 'create_report', 'target': {'kind': 'header'}, 'base_revision': None, 'depends_on': [],
        'payload': {'form_code': 'ONCE'},
    }
    body = {'contract_version': 2, 'operations': [operation]}
    barrier = threading.Barrier(2)
    results = [None, None]
    errors = []

    def worker(index):
        from django.db import connection
        connection.close()
        try:
            barrier.wait(timeout=10)
            results[index] = dispatch_operations(project=project, actor=user, body=body)
        except Exception as exc:
            errors.append(exc)
        finally:
            connection.close()

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    assert errors == [], errors
    assert DisciplineSubReport.objects.filter(project=project, form_code='ONCE').count() == 1
    assert OfflineOperationReceipt.objects.filter(project=project, actor=user, operation_id=operation['operation_id']).count() == 1
    report_ids = {item['results'][0]['target']['report_id'] for item in results}
    assert len(report_ids) == 1
