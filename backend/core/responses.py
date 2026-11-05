from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, status_code=status.HTTP_200_OK):
    return Response({'success': True, 'data': data}, status=status_code)


def error_body(message, errors=None, error_code='ERROR'):
    return {
        'success': False,
        'message': message,
        'errors': errors if errors is not None else {},
        'error_code': error_code,
    }


def error_response(message, errors=None, error_code='ERROR', status_code=status.HTTP_400_BAD_REQUEST):
    return Response(error_body(message, errors, error_code), status=status_code)
