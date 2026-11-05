import logging

from django.http import Http404, JsonResponse
from rest_framework import exceptions, status
from rest_framework.views import APIView

from .responses import error_body, error_response

logger = logging.getLogger(__name__)

ERROR_CODES = {
    exceptions.ParseError: 'PARSE_ERROR',
    exceptions.AuthenticationFailed: 'AUTHENTICATION_FAILED',
    exceptions.NotAuthenticated: 'NOT_AUTHENTICATED',
    exceptions.PermissionDenied: 'PERMISSION_DENIED',
    exceptions.NotFound: 'NOT_FOUND',
    exceptions.MethodNotAllowed: 'METHOD_NOT_ALLOWED',
    exceptions.NotAcceptable: 'NOT_ACCEPTABLE',
    exceptions.UnsupportedMediaType: 'UNSUPPORTED_MEDIA_TYPE',
    exceptions.Throttled: 'THROTTLED',
}


def _normalize_errors(detail):
    if isinstance(detail, dict):
        return {
            key: value if isinstance(value, (list, dict)) else [value]
            for key, value in detail.items()
        }
    if isinstance(detail, list):
        return {'non_field_errors': detail}
    return {'non_field_errors': [detail]}


def exception_handler(exc, context):
    """Global DRF exception handler returning the unified error envelope."""
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, exceptions.ValidationError):
        return error_response(
            'Validation failed.',
            errors=_normalize_errors(exc.detail),
            error_code='VALIDATION_ERROR',
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, exceptions.APIException):
        error_code = next(
            (code for klass, code in ERROR_CODES.items() if isinstance(exc, klass)),
            str(exc.default_code).upper(),
        )
        response = error_response(
            str(exc.detail),
            error_code=error_code,
            status_code=exc.status_code,
        )
        if getattr(exc, 'auth_header', None):
            response['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            response['Retry-After'] = '%d' % exc.wait
        return response

    logger.exception('Unhandled API exception', exc_info=exc)
    return None


class NotFoundView(APIView):
    """Catch-all for unknown routes; answers every method with the NOT_FOUND envelope."""

    def initial(self, request, *args, **kwargs):
        raise exceptions.NotFound('Not found.')


def server_error(request, *args, **kwargs):
    body = error_body('Internal server error.', error_code='SERVER_ERROR')
    return JsonResponse(body, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
