'''Database entry point for the dashboard payloads.'''

from collections import Counter

from . import periods
from ..models import ActivityEvent

INSUFFICIENT_DATA = 'insufficient_data'


def activity_summary(account, week_start, location):
    '''Activity Summary payload: weekly counts per Metric; Baseline and Status are not computed yet.'''
    week = periods.week_containing(week_start, account.timezone)
    totals = Counter()
    for row in ActivityEvent.objects.weekly_counts(account, [week.start], location):
        totals[row['event_type']] += row['count']
    return {
        'account_id': account.id,
        'week_start': week.start.isoformat(),
        'week_end': week.end.isoformat(),
        'location': location,
        'baseline_weeks_used': 0,
        'metrics': [
            {
                'event_type': event_type,
                'current': totals[event_type],
                'baseline': None,
                'delta': None,
                'delta_pct': None,
                'status': INSUFFICIENT_DATA,
            }
            for event_type in ActivityEvent.EventType.values
        ],
    }
