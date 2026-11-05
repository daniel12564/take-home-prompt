'''Database entry point for the dashboard payloads.'''

from dataclasses import asdict

from django.conf import settings

from . import baseline, findings, periods, rules
from ..models import ActivityEvent


def metric_summary(event_type, rows, week_start, window, has_activity):
    '''One Metric of the Activity Summary: count, Baseline, difference and Status.'''
    current = baseline.weekly_totals(rows, [week_start], event_type)[0]
    baseline_value = baseline.median(baseline.weekly_totals(rows, window, event_type))
    status = rules.status(
        current,
        baseline_value or 0,
        len(window),
        settings.DASHBOARD_RULES,
        has_activity=has_activity,
    )
    judged = status != rules.INSUFFICIENT_DATA
    return {
        'event_type': event_type,
        'current': current,
        'baseline': float(baseline_value) if judged else None,
        'delta': float(rules.delta(current, baseline_value)) if judged else None,
        'delta_pct': rules.delta_pct(current, baseline_value) if judged else None,
        'status': status,
    }


def baseline_window(account, week_start):
    '''The viewed Reporting Week of an Account and the Baseline Window before it.'''
    week = periods.week_containing(week_start, account.timezone)
    window = baseline.baseline_window(
        week.start,
        periods.first_week_start(settings.DASHBOARD_DATA_START_DATE),
        settings.DASHBOARD_RULES,
    )
    return week, window


def activity_summary(account, week_start, location):
    '''Activity Summary payload: each Metric's count, Baseline, delta and Status for the scope.'''
    week, window = baseline_window(account, week_start)
    rows = ActivityEvent.objects.weekly_counts(account, [*window, week.start], location)
    has_activity = bool(rows)
    return {
        'account_id': account.id,
        'week_start': week.start.isoformat(),
        'week_end': week.end.isoformat(),
        'location': location,
        'baseline_weeks_used': len(window),
        'metrics': [
            metric_summary(event_type, rows, week.start, window, has_activity)
            for event_type in ActivityEvent.EventType.values
        ],
    }


def attention(account, week_start):
    '''Attention List payload: the ordered Findings of the whole Account.

    The daily-grouped query for the one-day callout runs only when an Account-wide Finding exists.
    '''
    week, window = baseline_window(account, week_start)
    rows = ActivityEvent.objects.weekly_counts(account, [*window, week.start])
    found = findings.build(rows, week.start, window, settings.DASHBOARD_RULES)
    if any(finding.scope == 'account' for finding in found):
        found = findings.name_concentration(
            found, ActivityEvent.objects.daily_counts(account, week.start), settings.DASHBOARD_RULES
        )
    return {
        'account_id': account.id,
        'week_start': week.start.isoformat(),
        'week_end': week.end.isoformat(),
        'insufficient_reason': findings.insufficient_reason(rows, window, settings.DASHBOARD_RULES),
        'findings': [asdict(finding) for finding in found],
    }
