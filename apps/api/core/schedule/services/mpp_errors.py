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
PROCESSING_RESOURCE_LIMIT = 'processing_resource_limit'
PROCESSING_INTERRUPTED = 'processing_interrupted'
PROCESSING_BUSY = 'processing_busy'
INPUT_EXPIRED = 'input_expired'
CONVERSION_FAILED = 'conversion_failed'
IMPORT_FAILED = 'import_failed'

PUBLIC_MESSAGES = {
    INVALID_FILE_TYPE: 'File type is not allowed.',
    FILE_TOO_LARGE: 'File size must not exceed 50 MB.',
    MPP_CORRUPT: 'The Microsoft Project file is corrupt or unreadable.',
    MPP_PASSWORD_PROTECTED: 'This Microsoft Project file is password-protected. Remove the password or export unprotected XML.',
    MPP_UNSUPPORTED: 'This Microsoft Project file cannot be processed. Try exporting to XML from Microsoft Project.',
    MSP_INVALID_XML: 'Invalid or suspicious XML file',
    'validation_error': 'Invalid XER file',
    PROCESSING_TIMEOUT: 'Processing the file timed out. Try again or export XML.',
    PROCESSING_RESOURCE_LIMIT: 'Processing exceeded the available limit. Try again or export XML.',
    PROCESSING_INTERRUPTED: 'Processing was interrupted. Upload the file again to retry.',
    PROCESSING_BUSY: 'Schedule processing is busy. Wait and try again.',
    INPUT_EXPIRED: 'The uploaded file is no longer available. Upload it again to retry.',
    CONVERSION_FAILED: 'Could not process the Microsoft Project file. Try again or export to XML.',
    IMPORT_FAILED: 'The import was not completed. Upload the file again to retry.',
}

OLE_MAGIC = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
