"""Stable error codes for MSP/MPP schedule import (language-independent)."""
from __future__ import annotations


class MppImportError(Exception):
    """Typed failure during MPP validation or conversion."""

    def __init__(self, code: str, message: str = ''):
        self.code = code
        self.message = message or code
        super().__init__(self.message)


INVALID_FILE_TYPE = 'invalid_file_type'
FILE_TOO_LARGE = 'file_too_large'
MPP_CORRUPT = 'mpp_corrupt'
MPP_PASSWORD_PROTECTED = 'mpp_password_protected'
MPP_UNSUPPORTED = 'mpp_unsupported'
MSP_INVALID_XML = 'msp_invalid_xml'
PROCESSING_TIMEOUT = 'processing_timeout'
CONVERSION_FAILED = 'conversion_failed'
IMPORT_FAILED = 'import_failed'

OLE_MAGIC = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
