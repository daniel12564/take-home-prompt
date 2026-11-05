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
    result = build(*(rows_for(f'Site {n:02d}', call_received=0) for n in range(30)))

    assert len(result) == 30
