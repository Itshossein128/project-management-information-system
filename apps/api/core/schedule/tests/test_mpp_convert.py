"""MPP → MSPDI conversion unit tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from schedule.services.mpp_convert import convert_mpp_to_mspdi, looks_like_ole_compound
from schedule.services.mpp_errors import (
    MPP_CORRUPT,
    MPP_PASSWORD_PROTECTED,
    OLE_MAGIC,
    MppImportError,
)

FIXTURES = Path(__file__).parent / 'fixtures' / 'mpp'


def test_looks_like_ole_compound():
    assert looks_like_ole_compound(OLE_MAGIC + b'xxxx')
    assert not looks_like_ole_compound(b'<?xml')
    assert not looks_like_ole_compound(b'')


def test_convert_rejects_non_ole():
    with pytest.raises(MppImportError) as exc:
        convert_mpp_to_mspdi(b'not ole')
    assert exc.value.code == MPP_CORRUPT


def test_convert_rejects_empty():
    with pytest.raises(MppImportError) as exc:
        convert_mpp_to_mspdi(b'')
    assert exc.value.code == MPP_CORRUPT


def test_convert_password_protected():
    path = FIXTURES / 'password-protected.mpp'
    if not path.is_file():
        pytest.skip('fixture missing')
    data = path.read_bytes()
    with pytest.raises(MppImportError) as exc:
        convert_mpp_to_mspdi(data)
    assert exc.value.code == MPP_PASSWORD_PROTECTED


def test_convert_valid_mpp_to_mspdi():
    path = FIXTURES / 'duration-test9.mpp'
    if not path.is_file():
        pytest.skip('fixture missing')
    xml = convert_mpp_to_mspdi(path.read_bytes())
    assert b'<Project' in xml
    assert b'<Tasks' in xml or b'<Task' in xml
