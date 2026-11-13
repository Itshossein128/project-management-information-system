"""Standalone preparation process. It has no database credentials in its environment."""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


def _fail(workspace: Path, code: str) -> None:
    payload = json.dumps({'code': code})
    (workspace / 'diagnostics.txt').write_text(payload, encoding='utf-8')
    raise SystemExit(1)


def _wait_for_release(workspace: Path, deadline: datetime, parent: int) -> None:
    release = workspace / 'release'
    while not release.is_file():
        if datetime.now(deadline.tzinfo) >= deadline:
            _fail(workspace, 'processing_timeout')
        if os.getppid() != parent:
            os._exit(1)
        time.sleep(0.05)


def main(argv: list[str]) -> None:
    os.environ['IMPORT_HELPER'] = '1'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    workspace = Path(argv[1]).resolve().parent
    parent = os.getppid()
    if sys.platform == 'linux':
        import ctypes
        import signal
        ctypes.CDLL(None).prctl(1, signal.SIGKILL)
        if os.getppid() != parent:
            os._exit(1)
    manifest = json.loads(Path(argv[1]).read_text(encoding='utf-8'))
    deadline = datetime.fromisoformat(manifest['deadline'])
    _wait_for_release(workspace, deadline, parent)
    import django
    django.setup()
    from django.utils import timezone

    if timezone.is_naive(deadline):
        deadline = timezone.make_aware(deadline, timezone.get_current_timezone())
    if timezone.now() >= deadline:
        _fail(workspace, 'processing_timeout')
    source = workspace / 'input.bin'
    if source.is_symlink() or not source.is_file():
        _fail(workspace, 'conversion_failed')
    file_bytes = source.read_bytes()
    # Private acceptance controls are forwarded only by an isolated phase parent.
    fault_dir = os.environ.get('A7_P5_FAULT_DIR')
    if fault_dir and os.environ.get('A7_P5_ISOLATED') == '1':
        arm = Path(fault_dir) / 'arm-helper'
        if arm.is_file():
            control = arm.read_text().strip()
            arm.unlink()
            (Path(fault_dir) / 'reached-helper').write_text(json.dumps({'pid': os.getpid(), 'parent': parent, 'mode': control}))
            if control == 'memory':
                chunks = []
                while True:
                    chunks.append(bytearray(32 * 1024 * 1024))
            if control == 'pids':
                import subprocess
                while True:
                    subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(150)'])
            if control == 'output':
                (workspace / 'prepared.json').write_bytes(b'x' * (129 * 1024 * 1024))
                return
            if control == 'disk':
                with source.open('ab') as target:
                    while True:
                        target.write(b'x' * (16 * 1024 * 1024))
            if control == 'sleep':
                time.sleep(120)
            if control == 'kill-parent':
                import signal
                os.kill(parent, signal.SIGKILL)
                time.sleep(10)
            if control == 'cli':
                # Exercise the existing ImportError fallback in a fresh helper.
                sys.modules['jpype'] = None

    try:
        if manifest.get('mode') == 'convert':
            from schedule.services.mpp_convert import convert_mpp_to_mspdi
            xml = convert_mpp_to_mspdi(file_bytes)
            output = workspace / 'output.xml'
            if len(xml) > int(os.environ.get('IMPORT_OUTPUT_LIMIT_BYTES', str(128 * 1024 * 1024))):
                _fail(workspace, 'processing_resource_limit')
            output.write_bytes(xml)
            return
        from schedule.services.import_process import encode_prepared
        if manifest.get('family') == 'p6':
            from schedule.services.p6_import import parse_p6_xer
            parsed = parse_p6_xer(file_bytes)
        else:
            from schedule.services.msp_import import parse_msp_family
            parsed = parse_msp_family(file_bytes, filename=manifest.get('filename') or '')
        (workspace / 'prepared.json').write_bytes(encode_prepared(parsed))
    except SystemExit:
        raise
    except Exception as exc:
        code = getattr(exc, 'code', '')
        if code not in {
            'processing_timeout', 'processing_resource_limit', 'conversion_failed',
            'mpp_corrupt', 'mpp_password_protected', 'mpp_unsupported', 'msp_invalid_xml',
            'invalid_file_type', 'file_too_large', 'validation_error',
        }:
            if isinstance(exc, ValueError):
                code = 'msp_invalid_xml' if manifest.get('family') != 'p6' else 'validation_error'
            else:
                code = 'conversion_failed'
        _fail(workspace, code)


if __name__ == '__main__':
    main(sys.argv)
