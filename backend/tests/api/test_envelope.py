from django.test import override_settings
from django.urls import path
from rest_framework import serializers
from rest_framework.test import APIClient
from rest_framework.views import APIView


class _InvalidInputView(APIView):
    def get(self, request):
        raise serializers.ValidationError({'week_start': ['Must be a Monday.']})


class _BoomView(APIView):
    def get(self, request):
        raise RuntimeError('boom')


urlpatterns = [
    path('api/v1/_invalid/', _InvalidInputView.as_view()),
    path('api/v1/_boom/', _BoomView.as_view()),
]


def test_health_endpoint_returns_success_envelope():
    response = APIClient().get('/api/v1/health/')

    assert response.status_code == 200
    assert response.json() == {'success': True, 'data': {'status': 'ok'}}


def test_unknown_route_returns_not_found_envelope():
    response = APIClient().get('/api/v1/does-not-exist/')

    assert response.status_code == 404
    body = response.json()
    assert body['success'] is False
    assert body['error_code'] == 'NOT_FOUND'
    assert set(body) == {'success', 'message', 'errors', 'error_code'}


@override_settings(ROOT_URLCONF='tests.api.test_envelope')
def test_validation_failure_returns_validation_error_envelope():
    response = APIClient().get('/api/v1/_invalid/')

    assert response.status_code == 400
    assert response.json() == {
        'success': False,
        'message': 'Validation failed.',
        'errors': {'week_start': ['Must be a Monday.']},
        'error_code': 'VALIDATION_ERROR',
    }


@override_settings(ROOT_URLCONF='tests.api.test_envelope', DEBUG=True)
def test_unhandled_exception_returns_internal_error_envelope_even_with_debug():
    response = APIClient(raise_request_exception=False).get('/api/v1/_boom/')

    assert response.status_code == 500
    assert response.json() == {
        'success': False,
        'message': 'Internal server error.',
        'errors': {},
        'error_code': 'INTERNAL_ERROR',
    }
