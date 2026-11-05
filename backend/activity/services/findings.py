'''Findings (ADR-0002). Pure functions over plain data: no database, no settings.

Every function that needs a rule constant takes the `DASHBOARD_RULES` dictionary as `rules`.
'''

from dataclasses import dataclass
from datetime import date
from typing import Literal

from . import baseline as baseline_service
from . import explanations, rules as rules_service

EVENT_TYPES = ('call_received', 'lead_created', 'appointment_set')


@dataclass(frozen=True)
class Finding:
    '''One detected deviation; `explanation` is rendered from the other fields, never the reverse.'''

    scope: Literal['account', 'location']
    location: str | None
    kind: Literal['metric', 'no_activity']
    event_types: tuple[str, ...]
    direction: Literal['above', 'below']
    severity: Literal['warning', 'critical']
    current: int
    baseline: float | None
    delta_pct: float | None
    affected_locations: int | None
    total_locations: int | None
    concentrated_on: date | None
    explanation: str


def location_metric_finding(location, event_type, current, baseline, status, rules):
    '''Finding for one (Location, Metric) whose Status is `above` or `below`.'''
    return Finding(
        scope='location',
        location=location,
        kind='metric',
        event_types=(event_type,),
        direction=status,
        severity=rules_service.severity(current, baseline, rules),
        current=current,
        baseline=float(baseline),
        delta_pct=rules_service.delta_pct(current, baseline),
        affected_locations=None,
        total_locations=None,
        concentrated_on=None,
        explanation=explanations.location_metric(location, event_type, current, baseline),
    )


def no_activity_finding(location):
    '''The single Finding of a Location that recorded nothing at all in the viewed week.'''
    return Finding(
        scope='location',
        location=location,
        kind='no_activity',
        event_types=EVENT_TYPES,
        direction='below',
        severity=rules_service.CRITICAL,
        current=0,
        baseline=None,
        delta_pct=None,
        affected_locations=None,
        total_locations=None,
        concentrated_on=None,
        explanation=explanations.no_activity(location),
    )


def order_key(finding):
    '''Sort key: critical before warning, then the larger deviation first.

    A Finding with no percentage (a No-activity Finding, or a Metric that rose from a zero
    Baseline) has no upper bound on its deviation and leads its tier. Location and Event Type
    break ties so the order is the same on every load.
    '''
    tier = 0 if finding.severity == rules_service.CRITICAL else 1
    size = float('inf') if finding.delta_pct is None else abs(finding.delta_pct)
    return (tier, -size, finding.location or '', finding.event_types)


NO_EVENTS = 'no_events'
SHORT_HISTORY = 'short_history'


def insufficient_reason(rows, window, rules):
    '''Why no Findings can be produced for these rows, or None when they can.'''
    if not rows:
        return NO_EVENTS
    if len(window) < rules['min_baseline_weeks']:
        return SHORT_HISTORY
    return None


def build(rows, week_start, window, rules):
    '''Ordered Findings of the Location universe in `rows` for the viewed week.

    `rows` carry `location`, `event_type`, `week` and `count`, as returned by `weekly_counts`
    for the Baseline Window and the viewed week; the Locations they mention are the universe.
    '''
    if len(window) < rules['min_baseline_weeks']:
        return []
    by_location = {}
    for row in rows:
        by_location.setdefault(row['location'], []).append(row)
    found = []
    for location, location_rows in by_location.items():
        if not any(row['week'] == week_start for row in location_rows):
            found.append(no_activity_finding(location))
            continue
        for event_type in EVENT_TYPES:
            current = baseline_service.weekly_totals(location_rows, [week_start], event_type)[0]
            typical = baseline_service.median(
                baseline_service.weekly_totals(location_rows, window, event_type)
            )
            status = rules_service.status(current, typical, len(window), rules)
            if status in (rules_service.ABOVE, rules_service.BELOW):
                found.append(
                    location_metric_finding(location, event_type, current, typical, status, rules)
                )
    return sorted(found, key=order_key)
