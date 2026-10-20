"""Upload validator unit tests."""
import io

import pytest
from rest_framework.exceptions import ValidationError

from common.validators import (
    MSG_FILE_TOO_LARGE,
    MSG_INVALID_TYPE,
    validate_msp_upload,
    validate_xlsx_upload,
    validate_p6_upload,
    validate_document_upload,
    validate_upload,
)


class _FakeUpload:
    def __init__(self, name, content=b'hello', content_type='application/octet-stream', size=None):
        self.name = name
        self.content_type = content_type
        self._original = content
        self._pos = 0
        self.size = size if size is not None else len(content)

    def read(self, n=-1):
        if n == -1:
            data = self._original[self._pos :]
            self._pos = len(self._original)
            return data
        data = self._original[self._pos : self._pos + n]
        self._pos += len(data)
        return data

    def tell(self):
        return self._pos

    def seek(self, pos):
        self._pos = pos


def test_rejects_oversized_file():
    upload = _FakeUpload('data.xml', size=51 * 1024 * 1024)
    with pytest.raises(ValidationError) as exc:
        validate_msp_upload(upload)
    assert str(MSG_FILE_TOO_LARGE) in str(exc.value.detail)


def test_rejects_invalid_extension():
    upload = _FakeUpload('data.txt')
    with pytest.raises(ValidationError) as exc:
        validate_msp_upload(upload)
    assert str(MSG_INVALID_TYPE) in str(exc.value.detail)


def test_accepts_xml_extension():
    upload = _FakeUpload('schedule.xml', content=b'<?xml version="1.0"?><root/>')
    validate_msp_upload(upload)


def test_accepts_mpp_with_ole_magic():
    ole = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'project-bytes'
    upload = _FakeUpload('schedule.mpp', content=ole, content_type='application/x-ole-storage')
    validate_msp_upload(upload)


def test_rejects_mpp_without_ole_magic():
    upload = _FakeUpload('fake.mpp', content=b'not-ole-content')
    with pytest.raises(ValidationError) as exc:
        validate_msp_upload(upload)
    assert str(MSG_INVALID_TYPE) in str(exc.value.detail)


def test_rejects_oversized_mpp():
    ole = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'x'
    upload = _FakeUpload('big.mpp', content=ole, size=51 * 1024 * 1024)
    with pytest.raises(ValidationError) as exc:
        validate_msp_upload(upload)
    assert str(MSG_FILE_TOO_LARGE) in str(exc.value.detail)


def test_accepts_xlsx_extension():
    upload = _FakeUpload('budget.xlsx', content=b'PK\x03\x04')
    validate_xlsx_upload(upload)


def test_rejects_missing_file():
    with pytest.raises(ValidationError) as exc:
        validate_msp_upload(None)
    assert 'required' in str(exc.value.detail)


def test_accepts_p6_upload():
    upload = _FakeUpload('export.xer', content=b'ERM\t1\n')
    validate_p6_upload(upload)


def test_accepts_document_upload_with_expected_mime():
    upload = _FakeUpload('report.pdf', content=b'%PDF-1.4', content_type='application/pdf')
    validate_document_upload(upload)


def test_rejects_document_upload_with_mismatched_mime():
    upload = _FakeUpload('report.pdf', content=b'Not a PDF', content_type='text/plain')
    with pytest.raises(ValidationError) as exc:
        validate_document_upload(upload)
    assert str(MSG_INVALID_TYPE) in str(exc.value.detail)


def test_validate_upload_with_no_expected_mimes():
    upload = _FakeUpload('test.xyz', content=b'data')
    # Should pass because we don't expect any specific mime
    validate_upload(upload, allowed_extensions={'.xyz'}, expected_mimes=None)


class _ErrorUpload:
    def __init__(self, name):
        self.name = name
        self.size = 100

    def tell(self):
        raise ValueError("Simulated error during mime detection")

def test_mime_detection_exception_handling():
    upload = _ErrorUpload('test.xml')
    # It should fall back to content_type which is not present, returning None.
    # validate_msp_upload will still accept it if extension matches and detected mime is None
    validate_msp_upload(upload)
