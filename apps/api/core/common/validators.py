"""Reusable server-side upload validation."""
from __future__ import annotations

import os
from typing import Iterable

from rest_framework.exceptions import ValidationError

MSG_FILE_TOO_LARGE = 'حجم فایل نباید از 50 مگابایت تجاوز کند'
MSG_INVALID_TYPE = 'نوع فایل مجاز نیست'

DOCUMENT_EXTENSIONS = frozenset(
    {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.zip'}
)

DOCUMENT_MIMES: dict[str, frozenset[str]] = {
    '.pdf': frozenset({'application/pdf'}),
    '.doc': frozenset({'application/msword'}),
    '.docx': frozenset(
        {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/zip',
        }
    ),
    '.xls': frozenset({'application/vnd.ms-excel'}),
    '.xlsx': frozenset(
        {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/zip',
        }
    ),
    '.jpg': frozenset({'image/jpeg'}),
    '.jpeg': frozenset({'image/jpeg'}),
    '.png': frozenset({'image/png'}),
    '.zip': frozenset({'application/zip', 'application/x-zip-compressed'}),
}

MSP_MIMES = frozenset({'text/xml', 'application/xml'})

XLSX_MIMES = frozenset(
    {
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/zip',
    }
)


def _extension(filename: str) -> str:
    return os.path.splitext(filename or '')[1].lower()


def _detect_mime(file_obj) -> str | None:
    """Detect MIME type from file bytes; falls back to content_type header."""
    try:
        import magic

        pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
        head = file_obj.read(2048)
        if hasattr(file_obj, 'seek'):
            file_obj.seek(pos)
        if head:
            return magic.from_buffer(head, mime=True)
    except Exception:
        pass
    return getattr(file_obj, 'content_type', None) or None


def validate_upload(
    file,
    allowed_extensions: Iterable[str],
    max_size_mb: int = 50,
    expected_mimes: frozenset[str] | dict[str, frozenset[str]] | None = None,
) -> None:
    """Validate uploaded file size, extension, and MIME type.

    Raises ValidationError with Persian messages on failure.
    """
    if file is None:
        raise ValidationError({'file': 'file is required'})

    allowed = {ext.lower() if ext.startswith('.') else f'.{ext.lower()}' for ext in allowed_extensions}
    ext = _extension(getattr(file, 'name', '') or '')
    if ext not in allowed:
        raise ValidationError({'file': MSG_INVALID_TYPE})

    max_bytes = max_size_mb * 1024 * 1024
    size = getattr(file, 'size', None)
    if size is not None and size > max_bytes:
        raise ValidationError({'file': MSG_FILE_TOO_LARGE})

    detected = _detect_mime(file)
    if expected_mimes is None:
        return

    if isinstance(expected_mimes, dict):
        allowed_mimes = expected_mimes.get(ext, frozenset())
    else:
        allowed_mimes = expected_mimes

    if allowed_mimes and detected and detected not in ('application/octet-stream',):
        if detected not in allowed_mimes:
            raise ValidationError({'file': MSG_INVALID_TYPE})


def validate_msp_upload(file) -> None:
    validate_upload(file, allowed_extensions={'.xml'}, expected_mimes=MSP_MIMES)


def validate_p6_upload(file) -> None:
    validate_upload(file, allowed_extensions={'.xer'}, expected_mimes={'text/plain', 'application/octet-stream'})


def validate_document_upload(file) -> None:
    validate_upload(
        file,
        allowed_extensions=DOCUMENT_EXTENSIONS,
        expected_mimes=DOCUMENT_MIMES,
    )


def validate_xlsx_upload(file) -> None:
    validate_upload(file, allowed_extensions={'.xlsx'}, expected_mimes=XLSX_MIMES)
