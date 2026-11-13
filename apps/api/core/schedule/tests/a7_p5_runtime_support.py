"""Isolated fault barriers for A.7-P5. Inactive unless a phase database is selected."""

from __future__ import annotations

import os
import signal
import json
import time
from pathlib import Path

from django.db import connection


class FaultRefused(RuntimeError):
    """Raised when a fault marker is set outside the phase database."""


class IsolatedFault(Exception):
    def __init__(self, name: str):
        self.name = name
        super().__init__(name)


def phase_database(name: str | None = None) -> bool:
    current = name if name is not None else str(connection.settings_dict.get('NAME', ''))
    return 'a7p5' in current and os.environ.get('A7_P5_ISOLATED') == '1'


def barrier(name: str) -> None:
    directory = os.environ.get('A7_P5_FAULT_DIR')
    if directory:
        marker_path = Path(directory) / ('arm-' + name)
        if marker_path.exists():
            if not phase_database():
                raise FaultRefused('runtime barrier refused outside isolated database')
            reached = Path(directory) / ('reached-' + name)
            reached.write_text(json.dumps({'pid': os.getpid(), 'host': os.uname().nodename, 'stage': name}))
            if marker_path.read_text().strip() == 'kill':
                marker_path.unlink()
                os.kill(os.getpid(), signal.SIGKILL)
            until = time.monotonic() + 150
            while marker_path.exists() and time.monotonic() < until:
                time.sleep(0.05)
            if marker_path.exists():
                raise IsolatedFault(name)
    marker = os.environ.get('A7_P5_FAULT', '')
    if not marker or marker != name:
        return
    if not phase_database():
        raise FaultRefused(f'fault barrier {name} refused outside the isolated phase database')
    raise IsolatedFault(name)
