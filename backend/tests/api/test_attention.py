from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from rest_framework.test import APIClient

from activity.models import ActivityEvent
from tests.conftest import build_events


def attention(account_id, **params):
    return APIClient().get(f'/api/v1/accounts/{account_id}/dashboard/attention/', params)


def summary(account_id, **params):
    return APIClient().get(f'/api/v1/accounts/{account_id}/dashboard/activity-summary/', params)


def test_default_week_lists_south_going_silent_then_north_calls_above_typical(dashboard_fixture):
    response = attention(dashboard_fixture.account_a.id)

    assert response.status_code == 200
    body = response.json()
    assert body['success'] is True
    data = body['data']
    assert data['week_start'] == '2026-07-20'
    assert data['week_end'] == '2026-07-26'
    assert [
        (f['location'], f['kind'], f['severity'], f['direction']) for f in data['findings']
    ] == [
        ('South', 'no_activity', 'critical', 'below'),
        ('North', 'metric', 'warning', 'above'),
    ]


def test_findings_carry_the_agreed_shape_with_the_account_wide_fields_null(dashboard_fixture):
    findings = attention(dashboard_fixture.account_a.id).json()['data']['findings']

    assert findings == [
        {
            'scope': 'location',
            'location': 'South',
            'kind': 'no_activity',
            'event_types': ['call_received', 'lead_created', 'appointment_set'],
            'direction': 'below',
            'severity': 'critical',
            'current': 0,
            'baseline': None,
            'delta_pct': None,
            'affected_locations': None,
            'total_locations': None,
            'concentrated_on': None,
            'affected_by_metric': None,
            'explanation': (
                'South recorded no calls, leads or appointments this week; it is normally active.'
            ),
        },
        {
            'scope': 'location',
            'location': 'North',
            'kind': 'metric',
            'event_types': ['call_received'],
            'direction': 'above',
            'severity': 'warning',
            'current': 11,
            'baseline': 5.0,
            'delta_pct': 120.0,
            'affected_locations': None,
            'total_locations': None,
            'concentrated_on': None,
            'affected_by_metric': None,
            'explanation': 'North received 11 calls this week; it typically receives about 5.',
        },
    ]


def test_an_account_with_no_activity_returns_an_empty_list_and_says_why(dashboard_fixture):
    data = attention(dashboard_fixture.account_b.id).json()['data']

    assert data['findings'] == []
    assert data['insufficient_reason'] == 'no_events'


def test_an_account_with_findings_has_no_insufficient_reason(dashboard_fixture):
    data = attention(dashboard_fixture.account_a.id).json()['data']

    assert data['insufficient_reason'] is None


def test_a_week_with_nothing_to_report_is_an_empty_list_without_a_reason(dashboard_fixture):
    data = attention(dashboard_fixture.account_a.id, week_start='2026-07-13').json()['data']

    assert data['findings'] == []
    assert data['insufficient_reason'] is None


def test_a_week_with_too_little_history_returns_no_findings_and_says_so(dashboard_fixture):
    account = dashboard_fixture.account_a
    ActivityEvent.objects.bulk_create(
        event
        for week_start in [date(2026, 2, 2) + timedelta(weeks=n) for n in range(4)]
        for event in build_events(account, 'North', 'call_received', week_start, 5)
    )

    short = attention(account.id, week_start='2026-02-23').json()['data']
    enough = attention(account.id, week_start='2026-03-02').json()['data']

    assert short['findings'] == []
    assert short['insufficient_reason'] == 'short_history'
    assert enough['insufficient_reason'] is None


def assert_same_error_as_summary(account_id, **params):
    response = attention(account_id, **params)
    expected = APIClient().get(
        f'/api/v1/accounts/{account_id}/dashboard/activity-summary/', params
    )

    assert response.status_code == 400
    assert response.json() == expected.json()
    assert list(response.json()['errors']) == ['week_start']


def test_a_week_start_that_is_not_a_monday_is_rejected_like_the_summary(dashboard_fixture):
    assert_same_error_as_summary(dashboard_fixture.account_a.id, week_start='2026-07-21')


def test_a_week_start_before_the_data_start_is_rejected_like_the_summary(dashboard_fixture):
    assert_same_error_as_summary(dashboard_fixture.account_a.id, week_start='2026-01-26')


def test_the_in_progress_week_is_rejected_like_the_summary(dashboard_fixture):
    assert_same_error_as_summary(dashboard_fixture.account_a.id, week_start='2026-07-27')


def test_an_unparseable_week_start_is_rejected_like_the_summary(dashboard_fixture):
    assert_same_error_as_summary(dashboard_fixture.account_a.id, week_start='last-week')


def test_an_unknown_account_returns_the_not_found_envelope(dashboard_fixture):
    response = attention(999999)

    assert response.status_code == 404
    assert response.json()['error_code'] == 'NOT_FOUND'


def test_an_explicit_week_start_is_echoed(dashboard_fixture):
    data = attention(dashboard_fixture.account_a.id, week_start='2026-06-01').json()['data']

    assert data['week_start'] == '2026-06-01'
    assert data['week_end'] == '2026-06-07'


def test_the_location_parameter_is_ignored_because_the_list_is_always_the_whole_account(
    dashboard_fixture,
):
    whole = attention(dashboard_fixture.account_a.id).json()
    narrowed = attention(dashboard_fixture.account_a.id, location='East').json()

    assert narrowed == whole


def test_query_count_does_not_grow_with_the_number_of_locations(
    dashboard_fixture, django_assert_num_queries
):
    account = dashboard_fixture.account_a
    ActivityEvent.objects.bulk_create(
        ActivityEvent(
            account=account,
            location=f'Extra {index}',
            event_type=ActivityEvent.EventType.CALL_RECEIVED,
            occurred_at=datetime(2026, 7, 8, 10, 0, tzinfo=ZoneInfo(account.timezone)),
        )
        for index in range(20)
    )

    with django_assert_num_queries(2):
        response = attention(account.id)

    findings = response.json()['data']['findings']
    assert response.status_code == 200
    assert len([f for f in findings if f['kind'] == 'no_activity']) == 21


def test_week_6_where_every_location_has_4x_calls_is_one_account_wide_finding_and_no_location_cards(
    dashboard_fixture,
):
    data = attention(dashboard_fixture.account_a.id, week_start='2026-06-22').json()['data']

    assert len(data['findings']) == 1
    finding = data['findings'][0]
    assert finding['scope'] == 'account'
    assert finding['location'] is None
    assert finding['kind'] == 'metric'
    assert finding['event_types'] == ['call_received']
    assert finding['direction'] == 'above'
    assert finding['affected_locations'] == 3
    assert finding['total_locations'] == 3
    assert finding['affected_by_metric'] == {'call_received': 3}
    assert finding['concentrated_on'] is None
    assert [f for f in data['findings'] if f['scope'] == 'location'] == []


def test_an_account_wide_finding_reports_the_same_account_numbers_as_the_summary(dashboard_fixture):
    account_id = dashboard_fixture.account_a.id
    finding = attention(account_id, week_start='2026-06-22').json()['data']['findings'][0]
    calls = [
        metric
        for metric in summary(account_id, week_start='2026-06-22').json()['data']['metrics']
        if metric['event_type'] == 'call_received'
    ][0]

    assert (finding['current'], finding['baseline'], finding['delta_pct']) == (
        calls['current'],
        calls['baseline'],
        calls['delta_pct'],
    )


def test_an_account_wide_finding_costs_exactly_one_extra_query(
    dashboard_fixture, django_assert_num_queries
):
    with django_assert_num_queries(3):
        response = attention(dashboard_fixture.account_a.id, week_start='2026-06-22')

    assert response.json()['data']['findings'][0]['scope'] == 'account'


def test_the_default_week_is_unchanged_and_needs_no_extra_query(
    dashboard_fixture, django_assert_num_queries
):
    with django_assert_num_queries(2):
        data = attention(dashboard_fixture.account_a.id).json()['data']

    assert [(f['scope'], f['location']) for f in data['findings']] == [
        ('location', 'South'),
        ('location', 'North'),
    ]


def add_calls(account, moment, count):
    ActivityEvent.objects.bulk_create(
        ActivityEvent(
            account=account,
            location='North',
            event_type=ActivityEvent.EventType.CALL_RECEIVED,
            occurred_at=moment,
        )
        for _ in range(count)
    )


def test_a_week_whose_calls_piled_onto_one_local_day_names_that_day(dashboard_fixture):
    account = dashboard_fixture.account_a
    zone = ZoneInfo(account.timezone)
    # 23:30 on Wednesday 24 June in Chicago is already Thursday in UTC.
    add_calls(account, datetime(2026, 6, 24, 23, 30, tzinfo=zone), 200)

    finding = attention(account.id, week_start='2026-06-22').json()['data']['findings'][0]

    assert finding['scope'] == 'account'
    assert finding['concentrated_on'] == '2026-06-24'
    assert finding['explanation'].endswith("Most of this week's events happened on Wed 24 Jun.")


def test_an_evenly_spread_week_names_no_day(dashboard_fixture):
    finding = attention(dashboard_fixture.account_a.id, week_start='2026-06-22').json()['data'][
        'findings'
    ][0]

    assert finding['concentrated_on'] is None
    assert 'Most of this week' not in finding['explanation']
