"""PostgreSQL regressions for receipt validation and concurrent collection writes."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal
from queue import Queue

import pytest
from django.contrib.auth import get_user_model
from django.db import close_old_connections, connection, transaction
from rest_framework.exceptions import ValidationError

from config.exceptions import CodedValidationError
from contracts.collection_service import add_collection, collections_total
from contracts.models import Contract, IPC, IPCCollection, IPCStatus
from projects.models import Project


@pytest.fixture
def collection_ipc(db):
    user = get_user_model().objects.create(username='collection_race', full_name='Finance')
    project = Project.objects.create(project_code='COLLECTION-RACE', project_name='Collections')
    contract = Contract.objects.create(project=project, contract_type='main', created_by=user)
    ipc = IPC.objects.create(
        project=project,
        contract=contract,
        ipc_number=1,
        status=IPCStatus.APPROVED,
        gross_amount=Decimal('100'),
        submitted_amount=Decimal('100'),
        approved_amount=Decimal('100'),
        net_amount=Decimal('100'),
        created_by=user,
    )
    return ipc, user


@pytest.mark.django_db
def test_collection_rechecks_persisted_status(collection_ipc):
    ipc, user = collection_ipc
    IPC.objects.filter(pk=ipc.pk).update(status=IPCStatus.PAID)

    with pytest.raises(CodedValidationError) as error:
        add_collection(ipc=ipc, amount=Decimal('70'), collected_at=date.today(), user=user)

    assert error.value.default_code == 'collection_requires_approved'
    assert not IPCCollection.objects.filter(ipc=ipc).exists()


@pytest.mark.django_db
def test_collection_rechecks_persisted_payable(collection_ipc):
    ipc, user = collection_ipc
    IPC.objects.filter(pk=ipc.pk).update(net_amount=Decimal('60'))

    with pytest.raises(ValidationError, match='collection_exceeds_payable'):
        add_collection(ipc=ipc, amount=Decimal('70'), collected_at=date.today(), user=user)

    assert not IPCCollection.objects.filter(ipc=ipc).exists()


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('amount, successes, failures, total', [
    ('70', 1, 1, '70'),
    ('50', 2, 0, '100'),
])
def test_concurrent_collections_obey_payable(collection_ipc, amount, successes, failures, total):
    if connection.vendor != 'postgresql':
        pytest.skip('Requires PostgreSQL row locks')
    ipc, user = collection_ipc
    ipc_id, user_id = ipc.pk, user.pk
    backend_pids = Queue()
    start = threading.Barrier(2)

    def worker():
        close_old_connections()
        try:
            actor = get_user_model().objects.get(pk=user_id)
            stale_ipc = IPC.objects.get(pk=ipc_id)
            with connection.cursor() as cursor:
                cursor.execute('SELECT pg_backend_pid()')
                backend_pids.put(cursor.fetchone()[0])
            start.wait(timeout=10)
            try:
                return add_collection(
                    ipc=stale_ipc,
                    amount=Decimal(amount),
                    collected_at=date.today(),
                    user=actor,
                )
            except ValidationError as error:
                return error
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=2) as pool:
        # Hold the parent row until both workers block. Without validation under
        # this lock, both read total=0 before their INSERT foreign-key checks wait.
        with transaction.atomic():
            IPC.objects.select_for_update().get(pk=ipc_id)
            futures = [pool.submit(worker) for _ in range(2)]
            pids = [backend_pids.get(timeout=10) for _ in range(2)]
            deadline = time.monotonic() + 10
            while True:
                with connection.cursor() as cursor:
                    cursor.execute(
                        'SELECT COUNT(DISTINCT pid) FROM pg_locks WHERE pid = ANY(%s) AND NOT granted',
                        [pids],
                    )
                    if cursor.fetchone()[0] == 2:
                        break
                assert time.monotonic() < deadline, 'Both collection workers must reach the row lock'
                time.sleep(0.01)
        results = [future.result(timeout=20) for future in futures]

    accepted = [result for result in results if isinstance(result, IPCCollection)]
    rejected = [result for result in results if isinstance(result, ValidationError)]
    assert len(accepted) == successes
    assert len(rejected) == failures
    assert all('collection_exceeds_payable' in str(error) for error in rejected)
    assert collections_total(ipc) == Decimal(total)
    assert IPCCollection.objects.filter(ipc_id=ipc_id).count() == successes
    ipc.refresh_from_db()
    assert ipc.status == IPCStatus.APPROVED
    assert ipc.gross_amount == Decimal('100')
    assert ipc.net_amount == Decimal('100')
    assert ipc.submitted_amount == Decimal('100')
    assert ipc.approved_amount == Decimal('100')
