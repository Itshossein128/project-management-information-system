"""Convert native Microsoft Project MPP bytes to MSPDI XML.

Uses MPXJ via JPype when available; otherwise a Java CLI classpath
configured by ``MPP_MPXJ_CLASSPATH`` / ``MPP_MPXJ_JAR_DIR``.
Never bypasses password protection.
"""
from __future__ import annotations

import logging
import os
import subprocess
import tempfile
import threading
from pathlib import Path

from django.conf import settings

from schedule.services.mpp_errors import (
    CONVERSION_FAILED,
    MPP_CORRUPT,
    MPP_PASSWORD_PROTECTED,
    MPP_UNSUPPORTED,
    OLE_MAGIC,
    PROCESSING_TIMEOUT,
    MppImportError,
)

logger = logging.getLogger(__name__)

_jvm_lock = threading.Lock()
_jvm_started = False


def _timeout_seconds() -> int:
    return int(getattr(settings, 'MPP_CONVERT_TIMEOUT_SECONDS', 60) or 60)


def looks_like_ole_compound(data: bytes) -> bool:
    return bool(data) and data.startswith(OLE_MAGIC)


def _map_exception_message(msg: str) -> MppImportError:
    lower = (msg or '').lower()
    if 'password' in lower:
        return MppImportError(
            MPP_PASSWORD_PROTECTED,
            'This Microsoft Project file is password-protected. Remove the password or export unprotected XML.',
        )
    if 'unsupported' in lower or 'cannot read' in lower or 'unrecognised' in lower or 'unrecognized' in lower:
        return MppImportError(
            MPP_UNSUPPORTED,
            'This Microsoft Project file cannot be processed. Try exporting to XML from Microsoft Project.',
        )
    if 'corrupt' in lower or 'invalid' in lower or 'truncated' in lower or 'not an ole' in lower:
        return MppImportError(
            MPP_CORRUPT,
            'The Microsoft Project file is corrupt or unreadable.',
        )
    return MppImportError(CONVERSION_FAILED, msg or 'MPP conversion failed.')


def _ensure_jvm() -> None:
    global _jvm_started
    if _jvm_started:
        return
    with _jvm_lock:
        if _jvm_started:
            return
        import jpype
        import mpxj  # noqa: F401 — registers jars on classpath

        if not jpype.isJVMStarted():
            jpype.startJVM()
        _jvm_started = True


def _convert_with_jpype(mpp_bytes: bytes) -> bytes:
    _ensure_jvm()
    import jpype

    # Prefer org.mpxj (mpxj>=14) then net.sf.mpxj (older)
    try:
        from org.mpxj.reader import UniversalProjectReader  # type: ignore
        from org.mpxj.mspdi import MSPDIWriter  # type: ignore
    except ImportError:
        from net.sf.mpxj.reader import UniversalProjectReader  # type: ignore
        from net.sf.mpxj.mspdi import MSPDIWriter  # type: ignore

    from java.io import ByteArrayInputStream, ByteArrayOutputStream  # type: ignore

    result_box: dict = {}
    error_box: dict = {}

    def worker():
        try:
            stream = ByteArrayInputStream(mpp_bytes)
            project = UniversalProjectReader().read(stream)
            if project is None:
                raise RuntimeError('Unsupported or unreadable MPP')
            out = ByteArrayOutputStream()
            writer = MSPDIWriter()
            writer.write(project, out)
            result_box['xml'] = bytes(out.toByteArray())
        except Exception as exc:  # noqa: BLE001 — bridge Java exceptions
            error_box['exc'] = exc

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(timeout=_timeout_seconds())
    if thread.is_alive():
        raise MppImportError(
            PROCESSING_TIMEOUT,
            'Processing the Microsoft Project file timed out. Try again or export to XML.',
        )
    if 'exc' in error_box:
        raise _map_exception_message(str(error_box['exc']))
    xml = result_box.get('xml')
    if not xml:
        raise MppImportError(MPP_CORRUPT, 'The Microsoft Project file is corrupt or unreadable.')
    return xml


def _classpath() -> str | None:
    env_cp = os.environ.get('MPP_MPXJ_CLASSPATH', '').strip()
    if env_cp:
        return env_cp
    jar_dir = os.environ.get('MPP_MPXJ_JAR_DIR', '').strip()
    if not jar_dir:
        # Dev convenience: /tmp/mpxj.jar + /tmp/mpxj-lib from local setup
        candidates = []
        if Path('/tmp/mpxj.jar').is_file():
            candidates.append('/tmp/mpxj.jar')
        lib = Path('/tmp/mpxj-lib')
        if lib.is_dir():
            candidates.extend(str(p) for p in sorted(lib.glob('*.jar')))
        if candidates:
            return ':'.join(candidates)
        return None
    jars = sorted(Path(jar_dir).glob('*.jar'))
    root_jar = Path(jar_dir) / 'mpxj.jar'
    parts = [str(root_jar)] if root_jar.is_file() else []
    parts.extend(str(j) for j in jars if j.name != 'mpxj.jar')
    return ':'.join(parts) if parts else None


def _convert_with_java_cli(mpp_bytes: bytes) -> bytes:
    cp = _classpath()
    if not cp:
        raise MppImportError(
            CONVERSION_FAILED,
            'MPP conversion is unavailable (MPXJ/JRE not configured).',
        )

    with tempfile.TemporaryDirectory(prefix='mpp-convert-') as tmp:
        in_path = Path(tmp) / 'input.mpp'
        out_path = Path(tmp) / 'output.xml'
        in_path.write_bytes(mpp_bytes)
        cmd = [
            'java',
            '-cp',
            cp,
            'net.sf.mpxj.sample.MpxjConvert',
            str(in_path),
            str(out_path),
        ]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=_timeout_seconds(),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise MppImportError(
                PROCESSING_TIMEOUT,
                'Processing the Microsoft Project file timed out. Try again or export to XML.',
            ) from exc
        except FileNotFoundError as exc:
            raise MppImportError(
                CONVERSION_FAILED,
                'Java runtime is required to process MPP files.',
            ) from exc

        combined = (proc.stdout or '') + '\n' + (proc.stderr or '')
        if proc.returncode != 0 or not out_path.is_file():
            raise _map_exception_message(combined.strip() or f'exit {proc.returncode}')
        data = out_path.read_bytes()
        if not data:
            raise MppImportError(MPP_CORRUPT, 'The Microsoft Project file is corrupt or unreadable.')
        return data


def convert_mpp_to_mspdi(mpp_bytes: bytes) -> bytes:
    """Convert MPP file bytes to MSPDI XML bytes.

    Raises:
        MppImportError: with a stable ``code`` for API mapping.
    """
    if not mpp_bytes:
        raise MppImportError(MPP_CORRUPT, 'The Microsoft Project file is corrupt or unreadable.')
    if not looks_like_ole_compound(mpp_bytes):
        raise MppImportError(
            MPP_CORRUPT,
            'The Microsoft Project file is corrupt or unreadable.',
        )

    # Prefer in-process JPype when packages are installed.
    try:
        import jpype  # noqa: F401
        import mpxj  # noqa: F401

        return _convert_with_jpype(mpp_bytes)
    except MppImportError:
        raise
    except ImportError:
        logger.info('mpxj/JPype not installed; trying Java CLI conversion')
    except Exception as exc:  # noqa: BLE001
        # Fall through to CLI if JVM path fails unexpectedly
        logger.warning('JPype MPP conversion failed: %s', exc)

    try:
        return _convert_with_java_cli(mpp_bytes)
    except MppImportError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise _map_exception_message(str(exc)) from exc
