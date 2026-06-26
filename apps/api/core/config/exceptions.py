from rest_framework.exceptions import Throttled
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, Throttled) and response is not None:
        wait = exc.wait
        response.data = {
            'detail': 'Request was throttled.',
            'code': 'throttled',
            'retry_after': int(wait) if wait is not None else None,
        }
        if wait is not None:
            response['Retry-After'] = str(int(wait))
    return response
