from dataclasses import FrozenInstanceError
from datetime import date, timedelta

import pytest
from django.conf import settings

from activity.services import findings

RULES = settings.DASHBOARD_RULES
WEEK = date(2026, 7, 20)
WINDOW = [WEEK - timedelta(weeks=back) for back in range(8, 0, -1)]
STEADY = {'call_received': 5, 'lead_created': 2, 'appointment_set': 1}


def rows_for(location, **overrides):
    '''Weekly-count rows of one Location: steady in the window, `overrides` in the viewed week.

    An override of 0 leaves that Metric out of the viewed week, as `weekly_counts` does.
    '''
    volumes = {**STEADY, **overrides}
    return [
        {'location': location, 'event_type': event_type, 'week': week, 'count': count}
        for week in WINDOW
        for event_type, count in STEADY.items()
    ] + [
        {'location': location, 'event_type': event_type, 'week': WEEK, 'count': count}
        for event_type, count in volumes.items()
        if count
    ]


def build(*rows):
    return findings.build([row for group in rows for row in group], WEEK, WINDOW, RULES)


def test_a_metric_that_dropped_to_zero_is_one_critical_finding_for_that_location():
    result = build(rows_for('Site B', call_received=0))

    assert len(result) == 1
    finding = result[0]
    assert finding.scope == 'location'
    assert finding.location == 'Site B'
    assert finding.kind == 'metric'
    assert finding.event_types == ('call_received',)
    assert finding.direction == 'below'
    assert finding.severity == 'critical'
    assert finding.current == 0
    assert finding.baseline == 5
    assert finding.delta_pct == -100.0
    assert finding.affected_locations is None
    assert finding.total_locations is None
    assert finding.concentrated_on is None
    assert finding.explanation == 'Site B received 0 calls this week; it typically receives about 5.'


def test_a_finding_is_immutable():
    finding = build(rows_for('Site B', call_received=0))[0]

    with pytest.raises(FrozenInstanceError):
        finding.severity = 'warning'


def test_a_location_within_tolerance_on_every_metric_has_no_findings():
    assert build(rows_for('Site A', call_received=4)) == []


def test_a_surge_is_a_warning_in_the_above_direction():
    result = build(rows_for('Site H', call_received=9))

    assert [(f.direction, f.severity, f.current, f.baseline, f.delta_pct) for f in result] == [
        ('above', 'warning', 9, 5, 80.0)
    ]
    assert result[0].explanation == 'Site H received 9 calls this week; it typically receives about 5.'


def test_a_location_with_no_events_in_the_viewed_week_gets_one_critical_no_activity_finding():
    result = build(rows_for('Site G', call_received=0, lead_created=0, appointment_set=0))

    assert len(result) == 1
    finding = result[0]
    assert finding.scope == 'location'
    assert finding.location == 'Site G'
    assert finding.kind == 'no_activity'
    assert finding.event_types == ('call_received', 'lead_created', 'appointment_set')
    assert finding.direction == 'below'
    assert finding.severity == 'critical'
    assert finding.current == 0
    assert finding.baseline is None
    assert finding.delta_pct is None
    assert finding.explanation == (
        'Site G recorded no calls, leads or appointments this week; it is normally active.'
    )


def test_a_location_with_events_this_week_is_never_a_no_activity_finding():
    result = build(rows_for('Site B', call_received=0, lead_created=0, appointment_set=1))

    assert [(f.kind, f.event_types) for f in result] == [('metric', ('call_received',))]


def test_a_window_shorter_than_the_minimum_gives_no_findings_at_all():
    short = WINDOW[-3:]
    rows = [row for row in rows_for('Site G', call_received=0, lead_created=0, appointment_set=0)]

    assert findings.build(rows, WEEK, short, RULES) == []


def test_a_location_that_only_appeared_this_week_is_judged_against_a_zero_baseline():
    rows = [
        {'location': 'New', 'event_type': 'call_received', 'week': WEEK, 'count': 4},
        *rows_for('Old'),
    ]

    result = findings.build(rows, WEEK, WINDOW, RULES)

    assert [(f.location, f.direction, f.severity, f.baseline, f.delta_pct) for f in result] == [
        ('New', 'above', 'warning', 0, None)
    ]
    assert result[0].explanation == 'New received 4 calls this week; it typically receives about 0.'


def test_critical_findings_come_before_warnings_then_the_biggest_deviation_first():
    result = build(
        rows_for('A', call_received=9),
        rows_for('B', lead_created=6),
        rows_for('C', call_received=0),
        rows_for('D', call_received=0, lead_created=0, appointment_set=0),
        rows_for('E', call_received=20),
    )

    assert [(f.location, f.severity, f.delta_pct) for f in result] == [
        ('D', 'critical', None),
        ('E', 'critical', 300.0),
        ('C', 'critical', -100.0),
        ('B', 'warning', 200.0),
        ('A', 'warning', 80.0),
    ]


def test_equally_serious_findings_keep_a_stable_order():
    first = build(rows_for('B', call_received=0), rows_for('A', call_received=0))
    second = build(rows_for('A', call_received=0), rows_for('B', call_received=0))

    assert [f.location for f in first] == ['A', 'B']
    assert [f.location for f in second] == ['A', 'B']


def test_there_is_no_cap_on_the_number_of_findings():
    silent = {'call_received': 0, 'lead_created': 0, 'appointment_set': 0}
    result = build(*(rows_for(f'Site {n:02d}', **silent) for n in range(30)))

    assert len(result) == 30


def locations(count, surging, **overrides):
    '''`count` Locations, the first `surging` of which have `overrides` in the viewed week.'''
    return [
        rows_for(f'Site {index:02d}', **(overrides if index < surging else {}))
        for index in range(count)
    ]


def test_three_of_five_locations_above_on_calls_roll_up_into_one_account_wide_finding():
    result = build(*locations(5, 3, call_received=20))

    assert len(result) == 1
    finding = result[0]
    assert finding.scope == 'account'
    assert finding.location is None
    assert finding.kind == 'metric'
    assert finding.event_types == ('call_received',)
    assert finding.direction == 'above'
    assert finding.severity == 'critical'
    assert finding.current == 70
    assert finding.baseline == 25
    assert finding.delta_pct == 180.0
    assert finding.affected_locations == 3
    assert finding.total_locations == 5
    assert finding.affected_by_metric == {'call_received': 3}
    assert finding.concentrated_on is None
    assert finding.explanation == (
        'Calls were far above typical at 3 of 5 locations (70 calls vs about 25).'
    )


def test_two_of_five_locations_do_not_roll_up():
    result = build(*locations(5, 2, call_received=20))

    assert [(f.scope, f.location) for f in result] == [
        ('location', 'Site 00'),
        ('location', 'Site 01'),
    ]


def test_three_of_ten_locations_do_not_roll_up_because_they_are_under_half():
    result = build(*locations(10, 3, call_received=20))

    assert [(f.scope, f.location) for f in result] == [
        ('location', 'Site 00'),
        ('location', 'Site 01'),
        ('location', 'Site 02'),
    ]


def test_exactly_half_of_the_universe_rolls_up():
    result = build(*locations(6, 3, call_received=20))

    assert [(f.scope, f.affected_locations, f.total_locations) for f in result] == [
        ('account', 3, 6)
    ]


def test_accounts_with_one_or_two_locations_never_roll_up():
    for count in (1, 2):
        result = build(*locations(count, count, call_received=20))

        assert [(f.scope, f.location) for f in result] == [
            ('location', f'Site {index:02d}') for index in range(count)
        ]


def test_a_universe_of_three_rolls_up_when_all_three_agree():
    result = build(*locations(3, 3, call_received=20))

    assert [(f.scope, f.affected_locations, f.total_locations) for f in result] == [
        ('account', 3, 3)
    ]


def test_locations_that_moved_the_other_way_and_silent_locations_survive_the_rollup():
    result = build(
        *locations(4, 4, call_received=20),
        rows_for('Down', call_received=0),
        rows_for('Silent', call_received=0, lead_created=0, appointment_set=0),
    )

    assert [(f.scope, f.location, f.kind, f.direction) for f in result] == [
        ('account', None, 'metric', 'above'),
        ('location', 'Silent', 'no_activity', 'below'),
        ('location', 'Down', 'metric', 'below'),
    ]
    assert result[0].affected_locations == 4
    assert result[0].total_locations == 6


def test_same_direction_metrics_merge_into_one_finding_with_per_metric_counts():
    result = build(
        rows_for('A', call_received=20, lead_created=8),
        rows_for('B', call_received=20, lead_created=8),
        rows_for('C', call_received=20, lead_created=8),
        rows_for('D', call_received=20, lead_created=8),
        rows_for('E'),
    )

    assert len(result) == 1
    finding = result[0]
    assert finding.scope == 'account'
    assert finding.event_types == ('call_received', 'lead_created')
    assert finding.affected_by_metric == {'call_received': 4, 'lead_created': 4}
    assert finding.affected_locations == 4
    assert finding.total_locations == 5
    assert finding.current == 85
    assert finding.baseline == 25
    assert finding.explanation == (
        'Calls and leads were far above typical at 4 of 5 locations (85 calls vs about 25).'
    )


def test_a_merged_finding_reports_the_most_and_the_fewest_affected_locations():
    result = build(
        rows_for('A', call_received=20, lead_created=8),
        rows_for('B', call_received=20, lead_created=8),
        rows_for('C', call_received=20, lead_created=8),
        rows_for('D', call_received=20),
    )

    assert [f.scope for f in result] == ['account']
    assert result[0].affected_by_metric == {'call_received': 4, 'lead_created': 3}
    assert result[0].affected_locations == 4
    assert result[0].explanation.startswith(
        'Calls and leads were far above typical at 3 to 4 of 4 locations'
    )


def test_opposite_directions_stay_separate_account_wide_findings():
    result = build(
        *(rows_for(f'Site {n}', call_received=0, lead_created=9) for n in range(3)),
    )

    assert [(f.event_types, f.direction) for f in result] == [
        (('lead_created',), 'above'),
        (('call_received',), 'below'),
    ]


def test_a_metric_that_does_not_roll_up_stays_per_location_beside_the_account_wide_one():
    result = build(
        *locations(5, 3, call_received=20),
        rows_for('Odd', lead_created=9),
    )

    assert [(f.scope, f.location, f.event_types) for f in result][0] == (
        'account',
        None,
        ('call_received',),
    )
    assert [(f.scope, f.location, f.event_types) for f in result][1:] == [
        ('location', 'Odd', ('lead_created',)),
    ]


def day_rows(event_type, **counts):
    '''Daily-count rows of one Metric for the viewed week, keyed by day of the month in June.'''
    return [
        {'event_type': event_type, 'day': date(2026, 6, int(day.removeprefix('d'))), 'count': count}
        for day, count in counts.items()
    ]


def test_more_than_sixty_percent_of_a_metrics_events_on_one_day_is_named_in_the_finding():
    found = build(*locations(3, 3, call_received=20))

    result = findings.name_concentration(found, day_rows('call_received', d3=40, d4=10, d5=10), RULES)

    assert result[0].concentrated_on == date(2026, 6, 3)
    assert result[0].explanation == (
        'Calls were far above typical at 3 of 3 locations (60 calls vs about 15). '
        "Most of this week's events happened on Wed 3 Jun."
    )
    assert result[0].current == 60
    assert result[0].affected_locations == 3


def test_exactly_sixty_percent_on_one_day_is_not_a_concentration():
    found = build(*locations(3, 3, call_received=20))

    result = findings.name_concentration(found, day_rows('call_received', d3=36, d4=24), RULES)

    assert result == found
    assert result[0].concentrated_on is None


def test_only_the_events_of_the_findings_own_metrics_count_toward_the_concentration():
    found = build(*locations(3, 3, call_received=20))
    rows = day_rows('call_received', d3=10, d4=10, d5=10) + day_rows('lead_created', d3=500)

    assert findings.name_concentration(found, rows, RULES) == found


def test_a_merged_finding_pools_the_events_of_all_its_metrics():
    found = build(*locations(3, 3, call_received=20, lead_created=8))
    rows = day_rows('call_received', d3=30, d4=30) + day_rows('lead_created', d3=24)

    result = findings.name_concentration(found, rows, RULES)

    assert result[0].event_types == ('call_received', 'lead_created')
    assert result[0].concentrated_on == date(2026, 6, 3)


def test_per_location_findings_never_get_a_day_callout():
    found = build(rows_for('Site B', call_received=0))

    assert findings.name_concentration(found, day_rows('call_received', d3=99), RULES) == found
