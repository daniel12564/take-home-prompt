'''Findings (ADR-0002). Pure functions over plain data: no database, no settings.

Every function that needs a rule constant takes the `DASHBOARD_RULES` dictionary as `rules`.
'''

from dataclasses import dataclass, replace
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
    affected_by_metric: dict[str, int] | None = None


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


def account_wide_finding(direction, members, total_locations):
    '''One Account-wide Finding for the per-Location Findings of one direction.

    `members` maps each rolled-up Event Type to its per-Location Findings. `current`, `baseline`
    and `delta_pct` describe the first Metric, summed over the Locations affected on it.
    '''
    event_types = tuple(event_type for event_type in EVENT_TYPES if event_type in members)
    affected_by_metric = {event_type: len(members[event_type]) for event_type in event_types}
    lead = members[event_types[0]]
    current = sum(finding.current for finding in lead)
    baseline = sum(finding.baseline for finding in lead)
    critical = any(
        finding.severity == rules_service.CRITICAL
        for findings_of_metric in members.values()
        for finding in findings_of_metric
    )
    return Finding(
        scope='account',
        location=None,
        kind='metric',
        event_types=event_types,
        direction=direction,
        severity=rules_service.CRITICAL if critical else rules_service.WARNING,
        current=current,
        baseline=baseline,
        delta_pct=rules_service.delta_pct(current, baseline),
        affected_locations=max(affected_by_metric.values()),
        total_locations=total_locations,
        concentrated_on=None,
        explanation=explanations.account_wide(
            event_types, direction, affected_by_metric, total_locations, current, baseline, None
        ),
        affected_by_metric=affected_by_metric,
    )


def roll_up(found, total_locations, rules):
    '''Replace the per-Location Findings that most Locations share with Account-wide Findings.

    A (Metric, direction) rolls up when at least `rollup_min_locations` Locations, and at least
    `rollup_min_share` of the `total_locations` universe, have it. Rolled-up Metrics of the same
    direction merge into one Account-wide Finding; everything else is kept.
    '''
    groups = {}
    for finding in found:
        if finding.kind == 'metric':
            groups.setdefault(finding.direction, {}).setdefault(finding.event_types[0], []).append(
                finding
            )
    rolled = {}
    for direction, members in groups.items():
        for event_type, group in members.items():
            if (
                len(group) >= rules['rollup_min_locations']
                and len(group) >= rules['rollup_min_share'] * total_locations
            ):
                rolled.setdefault(direction, {})[event_type] = group
    replaced = {id(finding) for members in rolled.values() for group in members.values() for finding in group}
    kept = [finding for finding in found if id(finding) not in replaced]
    return kept + [
        account_wide_finding(direction, members, total_locations)
        for direction, members in rolled.items()
    ]


def order_key(finding):
    '''Sort key: Account-wide Findings first, then critical before warning, then the larger deviation first.

    A Finding with no percentage (a No-activity Finding, or a Metric that rose from a zero
    Baseline) has no upper bound on its deviation and leads its tier. Location and Event Type
    break ties so the order is the same on every load.
    '''
    tier = 0 if finding.severity == rules_service.CRITICAL else 1
    size = float('inf') if finding.delta_pct is None else abs(finding.delta_pct)
    return (finding.scope != 'account', tier, -size, finding.location or '', finding.event_types)


def concentrated_day(day_rows, event_types, rules):
    '''The local day holding more than `one_day_concentration_share` of these Metrics' events, if any.

    `day_rows` carry `event_type`, `day` and `count`; only rows of `event_types` are pooled.
    '''
    per_day = {}
    for row in day_rows:
        if row['event_type'] in event_types:
            per_day[row['day']] = per_day.get(row['day'], 0) + row['count']
    if not per_day:
        return None
    day = max(per_day, key=per_day.get)
    if per_day[day] > rules['one_day_concentration_share'] * sum(per_day.values()):
        return day
    return None


def name_concentration(found, day_rows, rules):
    '''`found` with the day callout added to every Account-wide Finding whose week was concentrated.'''
    named = []
    for finding in found:
        day = concentrated_day(day_rows, finding.event_types, rules) if finding.scope == 'account' else None
        if day is None:
            named.append(finding)
            continue
        named.append(
            replace(
                finding,
                concentrated_on=day,
                explanation=explanations.account_wide(
                    finding.event_types,
                    finding.direction,
                    finding.affected_by_metric,
                    finding.total_locations,
                    finding.current,
                    finding.baseline,
                    day,
                ),
            )
        )
    return named


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
    return sorted(roll_up(found, len(by_location), rules), key=order_key)
