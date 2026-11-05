'''Plain-language explanations of Findings (ADR-0002). Pure functions over plain data.

One template per (kind, scope); nothing else produces explanation text.
'''

# event type -> (singular noun, plural noun, past verb, present verb)
WORDS = {
    'call_received': ('call', 'calls', 'received', 'receives'),
    'lead_created': ('lead', 'leads', 'created', 'creates'),
    'appointment_set': ('appointment', 'appointments', 'set', 'sets'),
}


def number(value):
    '''A count or Baseline as plain text: no trailing zero, never scientific notation.'''
    return f'{value:.1f}'.removesuffix('.0')


def location_metric(location, event_type, current, baseline):
    '''Explanation of a per-Location Metric Finding.'''
    singular, plural, past, present = WORDS[event_type]
    noun = singular if current == 1 else plural
    return (
        f'{location} {past} {current} {noun} this week; '
        f'it typically {present} about {number(baseline)}.'
    )


def no_activity(location):
    '''Explanation of a No-activity Finding.'''
    return f'{location} recorded no calls, leads or appointments this week; it is normally active.'


def metric_names(event_types):
    '''Plural Metric names as a sentence subject: 'Calls, leads and appointments'.'''
    names = [WORDS[event_type][1] for event_type in event_types]
    if len(names) == 1:
        return names[0].capitalize()
    head = ', '.join(names[:-1])
    return f'{head} and {names[-1]}'.capitalize()


def location_count(affected_by_metric, total_locations):
    ''''15 of 15', or '14 to 15 of 15' when the merged Metrics affected different numbers.'''
    fewest, most = min(affected_by_metric.values()), max(affected_by_metric.values())
    affected = str(most) if fewest == most else f'{fewest} to {most}'
    return f'{affected} of {total_locations}'


WEEKDAYS = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
MONTHS = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')


def day_name(day):
    '''A local day as 'Wed 3 Jun', in English whatever the server locale.'''
    return f'{WEEKDAYS[day.weekday()]} {day.day} {MONTHS[day.month - 1]}'


def account_wide(event_types, direction, affected_by_metric, total_locations, current, baseline, day):
    '''Explanation of an Account-wide Finding.

    `current` and `baseline` describe the first Metric of `event_types`, over the Locations
    affected on it.
    '''
    singular, plural, _, _ = WORDS[event_types[0]]
    noun = singular if current == 1 else plural
    text = (
        f'{metric_names(event_types)} were far {direction} typical at '
        f'{location_count(affected_by_metric, total_locations)} locations '
        f'({current} {noun} vs about {number(baseline)}).'
    )
    if day is not None:
        text += f" Most of this week's events happened on {day_name(day)}."
    return text
