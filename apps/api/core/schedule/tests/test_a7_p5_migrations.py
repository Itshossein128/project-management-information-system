"""Migration and historical-anchor checks for import operations."""

from __future__ import annotations

import hashlib
import importlib

import pytest
from django.apps import apps

from projects.services import create_project_with_creator
from schedule.models import ImportProcessingSlot, MspImportJob, MspImportStatus, P6ImportJob

backfill_import_operations = importlib.import_module(
    'schedule.migrations.0016_import_operations_lifecycle',
).backfill_import_operations


def _project(user):
    return create_project_with_creator(
        creator=user,
        project_code='A7P5-MIGRATION',
        project_name='P5 migration',
        employer='P5',
        start_date='2026-01-01',
    )


@pytest.mark.django_db
def test_slot_is_seeded_and_backfill_preserves_bytes(user):
    assert ImportProcessingSlot.objects.filter(slot_number=1).exists()
    project = _project(user)
    payload = b'historical-bytes'
    terminal = MspImportJob.objects.create(
        project=project,
        filename='old.xml',
        file_data=payload,
        status=MspImportStatus.DONE,
        result={'kept': True},
        created_by=user,
    )
    active = P6ImportJob.objects.create(
        project=project,
        filename='live.xer',
        file_data=b'active',
        status=MspImportStatus.PENDING,
        created_by=user,
    )
    empty = MspImportJob.objects.create(
        project=project,
        filename='gone.xml',
        file_data=None,
        status=MspImportStatus.FAILED,
        created_by=user,
    )
    MspImportJob.objects.filter(pk__in=[terminal.pk, empty.pk]).update(
        source_sha256=None, source_size=None, retention_anchor_at=None, retention_anchor_source='', completed_at=None,
    )
    P6ImportJob.objects.filter(pk=active.pk).update(
        source_sha256=None, source_size=None, retention_anchor_at=None, completed_at=None,
    )
    backfill_import_operations(apps, None)
    terminal.refresh_from_db()
    active.refresh_from_db()
    empty.refresh_from_db()
    assert terminal.source_sha256 == hashlib.sha256(payload).hexdigest()
    assert terminal.source_size == len(payload)
    assert bytes(terminal.file_data) == payload
    assert terminal.retention_anchor_source == 'legacy_backfill'
    assert terminal.retention_anchor_at is not None
    assert terminal.completed_at is None
    assert terminal.result == {'kept': True}
    assert active.retention_anchor_at is None
    assert active.source_sha256 == hashlib.sha256(b'active').hexdigest()
    assert empty.source_sha256 is None
    assert empty.retention_anchor_source == 'legacy_backfill'
    assert empty.file_data is None


@pytest.mark.django_db(transaction=True)
def test_actual_schema_roundtrip_preserves_originals_and_history(user):
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    before = [('schedule', '0015_periodreportfigure_version')]
    final = [('schedule', '0017_import_retry_related_name')]
    project = _project(user)
    project_id, actor_id = project.pk, user.pk
    original = b'historical-schema-roundtrip'
    identities = []
    try:
        executor = MigrationExecutor(connection)
        executor.migrate(before)
        historical = executor.loader.project_state(before).apps
        for family, outcome in [('MspImportJob','done'),('P6ImportJob','failed'),('MspImportJob','pending')]:
            model=historical.get_model('schedule',family)
            row=model.objects.create(project_id=project_id,created_by_id=actor_id,
                filename='historical.xml',file_data=original,status=outcome,result={'kept':True})
            identities.append((family,row.pk,outcome))
        executor=MigrationExecutor(connection);executor.migrate(final)
        upgraded=executor.loader.project_state(final).apps
        anchors=[]
        for family,pk,outcome in identities:
            row=upgraded.get_model('schedule',family).objects.get(pk=pk)
            assert bytes(row.file_data)==original and row.result=={'kept':True}
            assert row.project_id==project_id and row.created_by_id==actor_id
            assert row.source_sha256==hashlib.sha256(original).hexdigest()
            assert row.source_size==len(original) and row.completed_at is None
            if outcome=='pending':assert row.retention_anchor_at is None
            else:
                assert row.retention_anchor_source=='legacy_backfill'
                anchors.append(row.retention_anchor_at)
        assert len(set(anchors))==1
        executor=MigrationExecutor(connection);executor.migrate(before)
        downgraded=executor.loader.project_state(before).apps
        for family,pk,outcome in identities:
            row=downgraded.get_model('schedule',family).objects.get(pk=pk)
            assert bytes(row.file_data)==original and row.result=={'kept':True}
            assert row.status==outcome and row.created_by_id==actor_id
    finally:
        MigrationExecutor(connection).migrate(final)
    assert ImportProcessingSlot.objects.filter(slot_number=1).exists()
