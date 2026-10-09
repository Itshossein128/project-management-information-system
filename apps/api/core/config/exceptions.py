from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.views import exception_handler
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _lazy

from common.i18n import localize_api_payload


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = 'conflict'
    default_detail = _lazy('Conflict.')

    def __init__(self, detail=None, code=None):
        if code is not None:
            self.default_code = code
        super().__init__(detail=detail, code=code)


class CodedValidationError(ValidationError):
    """ValidationError that preserves a stable machine-readable code."""

    def __init__(self, detail=None, code='validation_error'):
        self.default_code = code
        super().__init__(detail=detail, code=code)


def _extract_message(data) -> str:
    if isinstance(data, dict):
        if 'detail' in data:
            detail = data['detail']
            if isinstance(detail, list):
                return '; '.join(str(d) for d in detail)
            return str(detail)
        if 'non_field_errors' in data:
            return '; '.join(str(e) for e in data['non_field_errors'])
        messages = []
        for key, value in data.items():
            if isinstance(value, list):
                messages.append(f'{key}: {"; ".join(str(v) for v in value)}')
            else:
                messages.append(f'{key}: {value}')
        return '; '.join(messages) if messages else str(_('Validation error.'))
    if isinstance(data, list):
        return '; '.join(str(item) for item in data)
    return str(data)


def _collect_detail_codes(detail) -> list[str]:
    """Walk DRF error detail trees for ErrorDetail.code values."""
    codes: list[str] = []
    if detail is None:
        return codes
    code = getattr(detail, 'code', None)
    if code is not None:
        codes.append(str(code))
    if isinstance(detail, dict):
        if 'code' in detail and isinstance(detail['code'], str):
            codes.append(detail['code'])
        for value in detail.values():
            codes.extend(_collect_detail_codes(value))
    elif isinstance(detail, (list, tuple)):
        for item in detail:
            codes.extend(_collect_detail_codes(item))
    return codes


def _error_code(exc) -> str:
    if isinstance(exc, PermissionDenied):
        return 'permission_denied'
    if isinstance(exc, NotAuthenticated):
        return 'not_authenticated'
    if isinstance(exc, AuthenticationFailed):
        return 'authentication_failed'
    if isinstance(exc, NotFound):
        return 'not_found'
    if isinstance(exc, Throttled):
        return 'throttled'
    if isinstance(exc, ConflictError):
        code = getattr(exc, 'default_code', None)
        return str(code) if code else 'conflict'
    if isinstance(exc, ValidationError):
        code = getattr(exc, 'default_code', None)
        if code and code not in ('invalid', 'validation_error'):
            return str(code)
        # DRF re-wraps serializer ValidationError and resets default_code to
        # 'invalid'; prefer stable codes attached to ErrorDetail leaves.
        for candidate in _collect_detail_codes(getattr(exc, 'detail', None)):
            if candidate not in ('invalid', 'validation_error', 'null', 'blank', 'required'):
                return candidate
        return 'validation_error'
    code = getattr(exc, 'default_code', None)
    return str(code) if code else 'error'


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(response.data, dict) and 'error' in response.data:
        response.data = localize_api_payload(response.data)
        return response

    message = _extract_message(response.data)
    code = _error_code(exc)
    details = response.data if isinstance(response.data, dict) else {'detail': response.data}

    if isinstance(exc, Throttled):
        wait = exc.wait
        details = {**details, 'retry_after': int(wait) if wait is not None else None}
        if wait is not None:
            response['Retry-After'] = str(int(wait))

    response.data = localize_api_payload({
        'error': {
            'code': code,
            'message': message,
            'details': details,
        }
    })
    return response
