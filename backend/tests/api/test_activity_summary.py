from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework.test import APIClient

from activity.models import ActivityEvent
from tests.conftest import build_events


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


def metric_counts(data):
    return {metric['event_type']: metric['current'] for metric in data['metrics']}


def test_account_scope_sums_every_location_for_the_default_week(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id)

    data = response.json()['data']
    assert [metric['event_type'] for metric in data['metrics']] == [
        'call_received',
        'lead_created',
        'appointment_set',
    ]
    assert metric_counts(data) == {'call_received': 17, 'lead_created': 4, 'appointment_set': 2}


def metric_for(data, event_type):
    return next(metric for metric in data['metrics'] if metric['event_type'] == event_type)


def test_north_calls_are_above_its_baseline_in_the_default_week(dashboard_fixture):
    data = summary(dashboard_fixture.account_a.id, location='North').json()['data']

    calls = metric_for(data, 'call_received')
    assert calls['current'] == 12
    assert calls['baseline'] == 5
    assert calls['delta'] == 7
    assert calls['delta_pct'] == 140.0
    assert calls['status'] == 'above'
    assert data['baseline_weeks_used'] == 8


def test_account_baseline_is_the_median_of_weekly_sums_across_locations(dashboard_fixture):
    data = summary(dashboard_fixture.account_a.id).json()['data']

    calls = metric_for(data, 'call_received')
    assert calls['current'] == 17
    assert calls['baseline'] == 15
    assert calls['delta'] == 2
    assert calls['delta_pct'] == 13.3
    assert calls['status'] == 'typical'
    assert data['baseline_weeks_used'] == 8


def test_account_sums_and_baselines_hold_for_the_other_metrics(dashboard_fixture):
    data = summary(dashboard_fixture.account_a.id).json()['data']

    leads = metric_for(data, 'lead_created')
    assert (leads['current'], leads['baseline'], leads['status']) == (4, 6, 'typical')
    appointments = metric_for(data, 'appointment_set')
    assert (appointments['current'], appointments['baseline'], appointments['status']) == (
        2,
        3,
        'typical',
    )


def test_account_b_is_insufficient_data_on_every_metric(dashboard_fixture):
    data = summary(dashboard_fixture.account_b.id).json()['data']

    assert len(data['metrics']) == 3
    for metric in data['metrics']:
        assert metric['current'] == 0
        assert metric['status'] == 'insufficient_data'
        assert metric['baseline'] is None
        assert metric['delta'] is None
        assert metric['delta_pct'] is None
    assert data['baseline_weeks_used'] == 8


def test_location_without_any_event_in_the_window_or_week_is_insufficient_data(dashboard_fixture):
    ActivityEvent.objects.create(
        account=dashboard_fixture.account_a,
        location='Annex',
        event_type=ActivityEvent.EventType.CALL_RECEIVED,
        occurred_at=datetime(2026, 3, 3, 10, 0, tzinfo=ZoneInfo('America/Chicago')),
    )

    data = summary(dashboard_fixture.account_a.id, location='Annex').json()['data']

    assert {metric['status'] for metric in data['metrics']} == {'insufficient_data'}


def test_the_spike_week_does_not_change_the_baseline_of_later_weeks(dashboard_fixture):
    spike_week = dashboard_fixture.weeks[5]
    later_weeks = dashboard_fixture.weeks[6:]
    assert spike_week.isoformat() == '2026-06-22'

    spike = summary(dashboard_fixture.account_a.id, week_start=spike_week.isoformat()).json()['data']
    assert metric_for(spike, 'call_received')['current'] == 60
    assert metric_for(spike, 'call_received')['status'] == 'above'
    for week in later_weeks:
        data = summary(dashboard_fixture.account_a.id, week_start=week.isoformat()).json()['data']
        calls = metric_for(data, 'call_received')
        assert calls['baseline'] == 15, week
        if week != dashboard_fixture.default_week:
            assert calls['status'] == 'typical', week


def add_steady_history(account, week_starts):
    ActivityEvent.objects.bulk_create(
        event
        for week_start in week_starts
        for event in build_events(
            account, 'North', ActivityEvent.EventType.CALL_RECEIVED, week_start, 5
        )
    )


def test_baseline_weeks_used_is_smaller_near_the_start_of_the_data(dashboard_fixture):
    account = dashboard_fixture.account_a
    add_steady_history(account, [date(2026, 2, 2) + timedelta(weeks=n) for n in range(6)])

    second_week = summary(account.id, week_start='2026-02-09').json()['data']
    first_week = summary(account.id, week_start='2026-02-02').json()['data']

    assert second_week['baseline_weeks_used'] == 1
    assert first_week['baseline_weeks_used'] == 0


def test_fewer_than_four_weeks_in_the_window_give_no_verdict(dashboard_fixture):
    account = dashboard_fixture.account_a
    add_steady_history(account, [date(2026, 2, 2) + timedelta(weeks=n) for n in range(6)])

    three_weeks = summary(account.id, week_start='2026-02-23').json()['data']
    four_weeks = summary(account.id, week_start='2026-03-02').json()['data']

    assert three_weeks['baseline_weeks_used'] == 3
    assert metric_for(three_weeks, 'call_received')['status'] == 'insufficient_data'
    assert metric_for(three_weeks, 'call_received')['baseline'] is None
    assert four_weeks['baseline_weeks_used'] == 4
    calls = metric_for(four_weeks, 'call_received')
    assert (calls['current'], calls['baseline'], calls['status']) == (5, 5, 'typical')


def test_location_scope_counts_only_that_location(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, location='North')

    data = response.json()['data']
    assert data['location'] == 'North'
    assert metric_counts(data) == {'call_received': 12, 'lead_created': 2, 'appointment_set': 1}


def test_location_with_no_events_that_week_yields_zeros(dashboard_fixture):
    response = summary(dashboard_fixture.account_a.id, location='South')

    data = response.json()['data']
    assert metric_counts(data) == {'call_received': 0, 'lead_created': 0, 'appointment_set': 0}


def test_event_at_sunday_2330_in_the_account_timezone_counts_in_the_earlier_week(dashboard_fixture):
    ActivityEvent.objects.create(
        account=dashboard_fixture.account_a,
        location='East',
        event_type=ActivityEvent.EventType.CALL_RECEIVED,
        occurred_at=datetime(2026, 7, 19, 23, 30, tzinfo=ZoneInfo('America/Chicago')),
    )

    earlier = summary(dashboard_fixture.account_a.id, week_start='2026-07-13').json()['data']
    default = summary(dashboard_fixture.account_a.id).json()['data']

    assert metric_counts(earlier)['call_received'] == 16
    assert metric_counts(default)['call_received'] == 17


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


def add_locations(account, count):
    ActivityEvent.objects.bulk_create(
        ActivityEvent(
            account=account,
            location=f'Extra {index}',
            event_type=ActivityEvent.EventType.CALL_RECEIVED,
            occurred_at=datetime(2026, 7, 21, 10, 0, tzinfo=ZoneInfo(account.timezone)),
        )
        for index in range(count)
    )


def test_query_count_does_not_grow_with_the_number_of_locations(
    dashboard_fixture, django_assert_num_queries
):
    add_locations(dashboard_fixture.account_a, 20)

    with django_assert_num_queries(2):
        response = summary(dashboard_fixture.account_a.id)

    assert response.status_code == 200
    assert metric_counts(response.json()['data'])['call_received'] == 37


def test_location_scope_stays_within_a_fixed_query_budget(
    dashboard_fixture, django_assert_num_queries
):
    add_locations(dashboard_fixture.account_a, 20)

    with django_assert_num_queries(3):
        response = summary(dashboard_fixture.account_a.id, location='North')

    assert response.status_code == 200
