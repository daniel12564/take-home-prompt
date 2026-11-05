'''Database entry point for the dashboard payloads.'''

from . import periods


def activity_summary(account, week_start, location):
    '''Activity Summary payload; Metrics are not computed yet, only the resolved week is echoed.'''
    week = periods.week_containing(week_start, account.timezone)
    return {
        'account_id': account.id,
        'week_start': week.start.isoformat(),
        'week_end': week.end.isoformat(),
        'location': location,
        'metrics': [],
    }
