from rest_framework.test import APIClient


def test_account_list_returns_every_account_with_its_location_count(dashboard_fixture):
    response = APIClient().get('/api/v1/accounts/')

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    assert body['data'] == [
        {
            'id': dashboard_fixture.account_a.id,
            'name': 'Account A',
            'timezone': 'America/Chicago',
            'location_count': 3,
        },
        {
            'id': dashboard_fixture.account_b.id,
            'name': 'Account B',
            'timezone': 'UTC',
            'location_count': 0,
        },
    ]


def test_account_locations_returns_sorted_distinct_names(dashboard_fixture):
    response = APIClient().get(f'/api/v1/accounts/{dashboard_fixture.account_a.id}/locations/')

    assert response.status_code == 200
    assert response.json() == {'success': True, 'data': ['East', 'North', 'South']}


def test_account_locations_is_empty_for_an_account_without_events(dashboard_fixture):
    response = APIClient().get(f'/api/v1/accounts/{dashboard_fixture.account_b.id}/locations/')

    assert response.status_code == 200
    assert response.json() == {'success': True, 'data': []}


def test_account_locations_for_unknown_account_returns_not_found_envelope(dashboard_fixture):
    response = APIClient().get('/api/v1/accounts/999999/locations/')

    assert response.status_code == 404
    body = response.json()
    assert body['success'] is False
    assert body['error_code'] == 'NOT_FOUND'
    assert set(body) == {'success', 'message', 'errors', 'error_code'}
