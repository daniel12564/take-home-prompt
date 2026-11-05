from rest_framework.test import APIClient


def summary(account_id, **params):
    return APIClient().get(f'/api/v1/accounts/{account_id}/dashboard/activity-summary/', params)


def test_omitted_week_start_resolves_to_the_default_week(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id)

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    data = body['data']
    assert data['account_id'] == dashboard_fixture.account_a.id
    assert data['week_start'] == '2026-07-20'
    assert data['week_end'] == '2026-07-26'
    assert data['location'] is None
    assert data['metrics'] == []


def test_explicit_week_start_and_location_are_echoed(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-06-01', location='North')

    assert response.status_code == 200
    data = response.json()['data']
    assert data['week_start'] == '2026-06-01'
    assert data['week_end'] == '2026-06-07'
    assert data['location'] == 'North'


def test_earliest_selectable_week_is_accepted(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-02-02')

    assert response.status_code == 200
    assert response.json()['data']['week_start'] == '2026-02-02'


def test_blank_location_means_the_whole_account(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, location='')

    assert response.status_code == 200
    assert response.json()['data']['location'] is None


def assert_validation_error(response, field):
    assert response.status_code == 400
    body = response.json()
    assert body['success'] is False
    assert body['error_code'] == 'VALIDATION_ERROR'
    assert list(body['errors']) == [field]
    assert body['errors'][field]


def test_week_start_that_is_not_a_monday_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-07-21')

    assert_validation_error(response, 'week_start')


def test_week_start_before_the_data_start_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-01-26')

    assert_validation_error(response, 'week_start')


def test_week_start_of_the_in_progress_week_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-07-27')

    assert_validation_error(response, 'week_start')


def test_week_start_in_the_future_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='2026-08-03')

    assert_validation_error(response, 'week_start')


def test_unparseable_week_start_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, week_start='last-week')

    assert_validation_error(response, 'week_start')


def test_location_the_account_does_not_have_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, location='Nowhere')

    assert_validation_error(response, 'location')


def test_every_invalid_field_is_named_in_one_response(dashboard_fixture):
    response = summary(
        dashboard_fixture.account_a.id, week_start='2026-07-27', location='Nowhere'
    )

    assert response.status_code == 400
    assert set(response.json()['errors']) == {'week_start', 'location'}


def test_location_of_another_account_is_rejected(dashboard_fixture):
    response = summary(dashboard_fixture.account_b.id, location='North')

    assert_validation_error(response, 'location')


def test_unknown_account_returns_not_found_envelope(dashboard_fixture):
    response = summary(999999)

    assert response.status_code == 404
    body = response.json()
    assert body['success'] is False
    assert body['error_code'] == 'NOT_FOUND'
