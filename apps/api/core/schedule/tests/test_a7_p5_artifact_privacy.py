"""Workspace privacy and project-scoped status."""

import json
import uuid
from datetime import timedelta

import pytest
from django.core.cache import cache
from django.utils import timezone
from rest_framework.test import APIClient

from projects.models import ProjectStatus
from projects.services import create_project_with_creator
from schedule.models import ImportProcessingSlot, MspImportJob, MspImportStatus
from schedule.services.import_operations import admission_closed, mark_catchup_complete
from schedule.services.import_process import SCRATCH_UNFINISHED_KEY, reconcile_abandoned_scratch
from schedule.tests.test_msp_import import SAMPLE_MSP_XML


@pytest.fixture(autouse=True)
def _release_scratch_leader():
    cache.delete('a7p5-leader-scratch')
    cache.delete(SCRATCH_UNFINISHED_KEY)
    yield
    cache.delete('a7p5-leader-scratch')
    cache.delete(SCRATCH_UNFINISHED_KEY)


def _project(user, suffix):
    project = create_project_with_creator(
        creator=user,
        project_code=f'A7P5-PRIV-{suffix}',
        project_name=f'P5 privacy {suffix}',
        employer='P5',
        start_date='2026-01-01',
    )
    project.status = ProjectStatus.ACTIVE
    project.save(update_fields=['status', 'updated_at'])
    return project


@pytest.mark.django_db
def test_status_does_not_cross_projects(user, other_user):
    project = _project(user, 'ONE')
    other = _project(other_user, 'TWO')
    job = MspImportJob.objects.create(
        project=project,
        filename='plan.xml',
        file_data=SAMPLE_MSP_XML,
        status=MspImportStatus.FAILED,
        created_by=user,
        error_code='import_failed',
        error_message='The import was not completed. Upload the file again to retry.',
    )
    client = APIClient()
    client.force_authenticate(user=other_user)
    response = client.get(f'/api/v1/projects/{other.id}/import/msp/status/{job.id}/')
    assert response.status_code in {403, 404}
    assert 'plan.xml' not in response.content.decode()

@pytest.mark.django_db
def test_scratch_dry_run_preserves_expired_owned_workspace(tmp_path, settings):
    import json
    import uuid
    from datetime import timedelta
    from django.utils import timezone
    from schedule.services.import_process import reconcile_abandoned_scratch
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    token = uuid.uuid4()
    work = tmp_path / str(token)
    work.mkdir()
    manifest = {'token': str(token), 'deadline': (timezone.now()-timedelta(seconds=1)).isoformat()}
    (work/'manifest.json').write_text(json.dumps(manifest))
    (work/'input.bin').write_bytes(b'private-input')
    result = reconcile_abandoned_scratch(dry_run=True)
    assert str(token) in result['removed']
    assert (work/'input.bin').read_bytes() == b'private-input'


@pytest.mark.django_db
def test_scratch_item_budget_closes_admission(tmp_path, settings):
    import json
    import uuid
    from datetime import timedelta
    from django.utils import timezone
    from schedule.services.import_process import reconcile_abandoned_scratch
    from schedule.services.import_operations import admission_closed, mark_catchup_complete
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    mark_catchup_complete()
    token = str(uuid.uuid4());work = tmp_path/token;work.mkdir()
    (work/'manifest.json').write_text(json.dumps({'token':token,'deadline':(timezone.now()-timedelta(seconds=1)).isoformat()}))
    ticks=iter([0,0,11,11])
    result = reconcile_abandoned_scratch(monotonic=lambda:next(ticks,11))
    assert result['status']=='failed' and result['n']==1
    assert admission_closed()


@pytest.mark.django_db
def test_recovery_cannot_open_admission_after_unverified_scratch(user, settings, monkeypatch):
    from schedule.services.import_operations import run_maintenance, close_admission, admission_closed
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    close_admission()
    monkeypatch.setattr('schedule.services.import_process.reconcile_abandoned_scratch',
        lambda **kw: {'status':'failed','removed':[],'preserved':['owned-quarantine']})
    result=run_maintenance('recovery')
    assert result['status']=='failed' and admission_closed()


def _expired_workspace(root, token, payload):
    work = root / str(token)
    work.mkdir()
    manifest = {'token': str(token), 'deadline': (timezone.now() - timedelta(seconds=5)).isoformat()}
    (work / 'manifest.json').write_text(json.dumps(manifest))
    (work / 'input.bin').write_bytes(payload)
    return work


@pytest.mark.django_db
def test_expired_quarantine_is_kept_and_does_not_starve_later_cleanup(tmp_path, settings):
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    mark_catchup_complete()
    cache.delete(SCRATCH_UNFINISHED_KEY)
    quarantined = uuid.UUID('00000000-0000-4000-8000-000000000001')
    later = uuid.UUID('ffffffff-ffff-4fff-bfff-ffffffffffff')
    held = _expired_workspace(tmp_path, quarantined, b'secret-quarantine-bytes')
    _expired_workspace(tmp_path, later, b'later-cleanup')
    (tmp_path / 'notes.txt').write_text('keep')
    slot = ImportProcessingSlot.objects.get(slot_number=1)
    slot.execution_token = quarantined
    slot.quarantined = True
    slot.containment_id = 'cgroup:/outside/import-leaked'
    slot.owner_host = 'other-host'
    slot.reboot_id = 'other-boot'
    slot.save()

    result = reconcile_abandoned_scratch()

    assert result['status'] == 'failed'
    assert result['reason'] == 'unverified'
    assert result['unfinished'] == [str(quarantined)]
    assert str(later) in result['removed']
    assert held.joinpath('input.bin').read_bytes() == b'secret-quarantine-bytes'
    assert not (tmp_path / str(later)).exists()
    assert (tmp_path / 'notes.txt').read_text() == 'keep'
    assert 'secret-quarantine-bytes' not in json.dumps(result)
    slot.refresh_from_db()
    assert slot.quarantined is True
    assert slot.execution_token == quarantined
    assert admission_closed()

    again = reconcile_abandoned_scratch()
    assert again['status'] == 'failed'
    assert again['unfinished'] == [str(quarantined)]
    assert held.joinpath('input.bin').read_bytes() == b'secret-quarantine-bytes'
    slot.refresh_from_db()
    assert slot.quarantined is True and slot.execution_token == quarantined


@pytest.mark.django_db
def test_scratch_budget_retries_unfinished_work_before_new_arrivals(tmp_path, settings):
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    settings.IMPORT_MAINTENANCE_ITEM_SECONDS = 10
    mark_catchup_complete()
    cache.delete(SCRATCH_UNFINISHED_KEY)
    first = uuid.UUID('00000000-0000-4000-8000-00000000000a')
    second = uuid.UUID('00000000-0000-4000-8000-00000000000b')
    unfinished = uuid.UUID('ffffffff-ffff-4fff-8fff-ffffffffffff')
    for token in (first, second, unfinished):
        _expired_workspace(tmp_path, token, b'owned')
    calls = iter([0, 0, 1, 2, 2, 3, 4, 4, 100])

    result = reconcile_abandoned_scratch(monotonic=lambda: next(calls, 100))

    assert result['status'] == 'failed'
    assert result['reason'] == 'item_budget'
    assert result['n'] == 3
    assert result['bound_seconds'] == 60 + 480 + 10 * 3 + 1
    assert result['unfinished'] == [str(unfinished)]
    assert not (tmp_path / str(first)).exists()
    assert not (tmp_path / str(second)).exists()
    assert (tmp_path / str(unfinished) / 'input.bin').read_bytes() == b'owned'
    assert admission_closed()

    newcomer = uuid.UUID('00000000-0000-4000-8000-000000000001')
    _expired_workspace(tmp_path, newcomer, b'newcomer')
    follow = iter([0, 0, 1, 2, 2, 100])
    retried = reconcile_abandoned_scratch(monotonic=lambda: next(follow, 100))
    assert retried['removed'][0] == str(unfinished)
    assert not (tmp_path / str(unfinished)).exists()
    assert (tmp_path / str(newcomer) / 'input.bin').read_bytes() == b'newcomer'
    assert retried['unfinished'] == [str(newcomer)]
    assert admission_closed()


@pytest.mark.django_db
def test_repeat_scratch_removal_keeps_unrelated_files(tmp_path, settings):
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    cache.delete(SCRATCH_UNFINISHED_KEY)
    token = uuid.uuid4()
    _expired_workspace(tmp_path, token, b'owned-once')
    (tmp_path / 'notes.txt').write_text('keep')

    first = reconcile_abandoned_scratch()
    second = reconcile_abandoned_scratch()

    assert first['status'] == 'ok' and str(token) in first['removed']
    assert not (tmp_path / str(token)).exists()
    assert second['status'] == 'ok' and str(token) not in second['removed']
    assert second['unfinished'] == []
    assert (tmp_path / 'notes.txt').read_text() == 'keep'
    assert cache.get(SCRATCH_UNFINISHED_KEY) is None


@pytest.mark.django_db
def test_recovery_forwards_supplied_time_and_clock_to_scratch(tmp_path, settings):
    from schedule.services.import_operations import admission_closed, mark_catchup_complete, run_maintenance
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    settings.IMPORT_ADMISSION_REQUIRES_CATCHUP = True
    settings.IMPORT_MAINTENANCE_GAP_SECONDS = 0
    mark_catchup_complete()
    cache.delete(SCRATCH_UNFINISHED_KEY)
    future = timezone.now() + timedelta(hours=2)
    aged = _expired_workspace(tmp_path, uuid.uuid4(), b'aged-by-caller-clock')
    manifest = json.loads((aged / 'manifest.json').read_text())
    manifest['deadline'] = (timezone.now() + timedelta(minutes=30)).isoformat()
    (aged / 'manifest.json').write_text(json.dumps(manifest))

    aged_result = run_maintenance('recovery', now=future, monotonic=lambda: 0, sleeper=lambda _seconds: None)

    assert aged_result['status'] == 'ok'
    assert not aged.exists()
    held = _expired_workspace(tmp_path, uuid.uuid4(), b'still-owned')
    calls = iter([0, 0, 0, 50])
    blocked = run_maintenance('recovery', now=future, monotonic=lambda: next(calls, 50), sleeper=lambda _seconds: None)
    assert blocked['status'] == 'failed'
    assert blocked['reason'] == 'scratch_not_verified'
    assert blocked['scratch']['reason'] == 'item_budget'
    assert (held / 'input.bin').read_bytes() == b'still-owned'
    assert admission_closed()
