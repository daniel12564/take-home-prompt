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
