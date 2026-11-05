'''Baseline arithmetic. Pure functions over plain data: no database, no settings.

Every function that needs a rule constant takes the `DASHBOARD_RULES` dictionary as `rules`.
'''

from datetime import timedelta


def baseline_window(week_start, first_week_start, rules):
    '''Mondays of the complete weeks before `week_start` that form its Baseline Window, oldest first.

    At most `baseline_weeks` weeks, clipped at the first week of data.
    '''
    weeks = (week_start - timedelta(weeks=back) for back in range(rules['baseline_weeks'], 0, -1))
    return [week for week in weeks if week >= first_week_start]


def median(values):
    '''Median of weekly values; None when there are none.'''
    ordered = sorted(values)
    if not ordered:
        return None
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def weekly_totals(rows, weeks, event_type):
    '''Per-week sums of one Metric across `rows`, in `weeks` order; weeks with no events are 0.

    `rows` carry `event_type`, `week` and `count`, as returned by `weekly_counts`. Over the rows
    of every Location this is the Account scope; over one Location's rows it is that Location.
    '''
    totals = dict.fromkeys(weeks, 0)
    for entry in rows:
        if entry['event_type'] == event_type and entry['week'] in totals:
            totals[entry['week']] += entry['count']
    return list(totals.values())
