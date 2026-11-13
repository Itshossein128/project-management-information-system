"""Actual kernel-control probes, isolated from shared application data."""
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest


def _root():
    value = os.environ.get('A7P5_CGROUP_HOST_ROOT', '')
    if not value or not os.access(value, os.W_OK):
        pytest.skip('requires the dedicated writable P5 delegation')
    return Path(value)


def test_owned_cgroup_controls_and_descendants_are_reaped(settings):
    from schedule.services.import_process import _arm_cgroup, _finish_cgroup, _pid_in_cgroup
    settings.IMPORT_CGROUP_ROOT = str(_root())
    proc = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'], start_new_session=True)
    group = None
    try:
        group = _arm_cgroup(uuid.uuid4(), proc.pid)
        assert _pid_in_cgroup(group, proc.pid)
        assert int((group / 'memory.max').read_text()) == settings.IMPORT_HELPER_MEMORY_BYTES
        assert (group / 'memory.swap.max').read_text().strip() == '0'
        assert (group / 'pids.max').read_text().strip() == str(settings.IMPORT_HELPER_PIDS)
        assert (group / 'cpu.max').read_text().strip() == '100000 100000'
        _finish_cgroup(group, proc)
        assert proc.poll() is not None
        assert not group.exists()
    finally:
        if proc.poll() is None:
            proc.kill(); proc.wait()
        if group is not None and group.exists():
            (group / 'cgroup.kill').write_text('1')
            group.rmdir()


def test_oom_is_detected_as_resource_failure(settings):
    from schedule.services.import_process import _arm_cgroup, _finish_cgroup, _resource_exhausted
    settings.IMPORT_CGROUP_ROOT = str(_root())
    settings.IMPORT_HELPER_MEMORY_BYTES = 32 * 1024 * 1024
    proc = subprocess.Popen([sys.executable, '-c', 'import sys; sys.stdin.readline(); x=bytearray(128*1024*1024)'], stdin=subprocess.PIPE, start_new_session=True)
    group = None
    try:
        group = _arm_cgroup(uuid.uuid4(), proc.pid)
        proc.stdin.write(b'go\n'); proc.stdin.flush()
        proc.wait(timeout=15)
        assert proc.returncode != 0
        assert _resource_exhausted(group)
    finally:
        if group is not None:
            _finish_cgroup(group, proc)
        elif proc.poll() is None:
            proc.kill(); proc.wait()


@pytest.mark.django_db
def test_pids_exhaustion_does_not_wait_for_inherited_pipes(tmp_path, settings, monkeypatch):
    import time
    from schedule.services.import_process import prepare_bytes
    from schedule.services.mpp_errors import MppImportError
    from schedule.tests.test_msp_import import SAMPLE_MSP_XML
    settings.IMPORT_CGROUP_ROOT = str(_root())
    settings.IMPORT_CONTAINMENT_REQUIRED = True
    settings.IMPORT_PREPARE_INLINE = False
    settings.IMPORT_SCRATCH_ROOT = str(tmp_path/'scratch')
    settings.IMPORT_HELPER_PIDS = 4
    settings.IMPORT_PREPARE_TIMEOUT_SECONDS = 4
    controls=tmp_path/'faults';controls.mkdir();(controls/'arm-helper').write_text('pids')
    monkeypatch.setenv('A7_P5_ISOLATED','1')
    monkeypatch.setenv('A7_P5_FAULT_DIR',str(controls))
    started=time.monotonic()
    with pytest.raises(MppImportError) as error:
        prepare_bytes(SAMPLE_MSP_XML,'plan.xml','msp')
    assert error.value.code=='processing_resource_limit'
    assert time.monotonic()-started<4
    import json
    helper_pid=json.loads((controls/'reached-helper').read_text())['pid']
    with pytest.raises(ProcessLookupError):os.kill(helper_pid,0)
    assert not list(Path(settings.IMPORT_SCRATCH_ROOT).glob('*/manifest.json'))
