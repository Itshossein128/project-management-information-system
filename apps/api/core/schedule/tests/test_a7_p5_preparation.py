"""Helper protocol, capacity, and process-group checks. Kernel containment is separate."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from schedule.services.import_process import (
    ProcessingBusy,
    acquire_slot,
    cleanup_execution_dir,
    decode_prepared,
    encode_prepared,
    kill_process_group,
    prepare_bytes,
    release_slot,
    scratch_root,
)
from schedule.services.mpp_convert import _fallback_allowed
from schedule.services.mpp_errors import PROCESSING_RESOURCE_LIMIT, PROCESSING_TIMEOUT, MppImportError
from schedule.services.msp_import import parse_msp_xml
from schedule.tests.test_msp_import import SAMPLE_MSP_XML


def test_prepared_json_round_trips_known_fields():
    parsed = parse_msp_xml(SAMPLE_MSP_XML)
    parsed.recognized_kind = 'xml'
    restored = decode_prepared(encode_prepared(parsed))
    assert restored.recognized_kind == 'xml'
    assert len(restored.tasks) == len(parsed.tasks)
    assert restored.tasks[0].name == parsed.tasks[0].name
    assert restored.tasks[0].predecessors == parsed.tasks[0].predecessors


def test_prepared_json_rejects_unknown_and_oversized_payloads(settings):
    settings.IMPORT_OUTPUT_LIMIT_BYTES = 40
    with pytest.raises(MppImportError) as exc:
        decode_prepared(b'{"version":1,"tasks":[]}' + b' ' * 80)
    assert exc.value.code == PROCESSING_RESOURCE_LIMIT
    with pytest.raises(MppImportError):
        decode_prepared(b'{"version":1,"tasks":[],"python":"import os"}')


def test_timeout_does_not_select_a_second_route():
    assert _fallback_allowed(MppImportError(PROCESSING_TIMEOUT, 'timed out')) is False
    assert _fallback_allowed(MppImportError(PROCESSING_RESOURCE_LIMIT, 'limited')) is False


@pytest.mark.django_db
def test_second_slot_claim_is_rejected_and_released():
    import uuid
    from datetime import timedelta

    from django.utils import timezone
    deadline = timezone.now() + timedelta(seconds=30)
    token = acquire_slot(family='preview', subject_id=uuid.uuid4(), deadline=deadline)
    try:
        with pytest.raises(ProcessingBusy):
            acquire_slot(family='preview', subject_id=uuid.uuid4(), deadline=deadline)
    finally:
        release_slot(token)


@pytest.mark.django_db
def test_denied_containment_writes_no_input(settings):
    settings.IMPORT_CONTAINMENT_REQUIRED = True
    settings.IMPORT_CGROUP_ROOT = '/tmp/a7p5-cgroup-missing'
    root = scratch_root()
    before = {path.name for path in root.iterdir()} if root.exists() else set()
    with pytest.raises(MppImportError) as exc:
        prepare_bytes(b'<Project>secret-marker</Project>', 'plan.xml', 'msp')
    assert exc.value.code == 'conversion_failed'
    after = {path.name for path in root.iterdir()}
    assert after == before


@pytest.mark.django_db
def test_subprocess_prepare_parses_xml_without_the_parent_jvm(settings):
    settings.IMPORT_PREPARE_INLINE = False
    settings.IMPORT_CONTAINMENT_REQUIRED = False
    parsed = prepare_bytes(SAMPLE_MSP_XML, 'plan.xml', 'msp')
    assert parsed.recognized_kind == 'xml'
    assert parsed.tasks


def test_child_process_group_is_reaped():
    proc = subprocess.Popen(['sleep', '30'], start_new_session=True)
    kill_process_group(proc, 0.2)
    assert proc.poll() is not None


def test_cleanup_rejects_symlinks_and_preserves_unrelated_names(tmp_path, settings):
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path)
    workspace = scratch_root() / '11111111-1111-1111-1111-111111111111'
    workspace.mkdir()
    (workspace / 'manifest.json').write_text('{}', encoding='utf-8')
    (workspace / 'notes.txt').write_text('keep', encoding='utf-8')
    assert cleanup_execution_dir(workspace) == 'preserved'
    assert (workspace / 'notes.txt').read_text(encoding='utf-8') == 'keep'
    link = scratch_root() / 'linked'
    link.symlink_to(workspace)
    assert cleanup_execution_dir(link) == 'rejected'
    assert link.is_symlink()


@pytest.mark.django_db
@pytest.mark.parametrize('name,family,expected',[
    ('bad.xml','msp','msp_invalid_xml'),
    ('password-protected.mpp','msp','mpp_password_protected'),
    ('truncated-ole.mpp','msp',('mpp_corrupt','mpp_unsupported')),
    ('renamed-not-mpp.mpp','msp','mpp_corrupt'),
    ('bad.xer','p6','validation_error'),
])
def test_actual_helper_preserves_stable_input_error_codes(name, family, expected, settings):
    settings.IMPORT_PREPARE_INLINE = False
    settings.IMPORT_CONTAINMENT_REQUIRED = False
    fixture=Path(__file__).parent/'fixtures/mpp'/name
    payload=fixture.read_bytes() if fixture.exists() else b'<not-project/>'
    with pytest.raises(MppImportError) as error:
        prepare_bytes(payload,name,family)
    assert error.value.code in (expected if isinstance(expected,tuple) else (expected,))
    assert not list(scratch_root().glob('*/manifest.json'))
