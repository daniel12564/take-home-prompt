'''Normality rules (ADR-0001). Pure functions over plain numbers: no database, no settings.

Every function takes the `DASHBOARD_RULES` dictionary as `rules`; no rule constant lives here.
'''

from math import sqrt


def tolerance(baseline, rules):
    '''How far a Metric may move from its Baseline before it is no longer typical.'''
    return max(
        rules['tolerance_abs_min'],
        rules['tolerance_rel'] * baseline,
        rules['tolerance_sqrt_factor'] * sqrt(baseline),
    )


TYPICAL = 'typical'
ABOVE = 'above'
BELOW = 'below'
INSUFFICIENT_DATA = 'insufficient_data'


def status(current, baseline, weeks_used, rules, has_activity=True):
    '''Status of a Metric's weekly count against its Baseline.

    `weeks_used` is how many weeks the Baseline Window holds; `has_activity` says whether the
    scope recorded any Activity Event in the window or the viewed week.
    '''
    if not has_activity or weeks_used < rules['min_baseline_weeks']:
        return INSUFFICIENT_DATA
    deviation = current - baseline
    if abs(deviation) < tolerance(baseline, rules):
        return TYPICAL
    return ABOVE if deviation > 0 else BELOW


WARNING = 'warning'
CRITICAL = 'critical'


def severity(current, baseline, rules):
    '''Severity of a Metric that is not typical.

    Critical at twice the Tolerance, or when the Metric fell to zero from a Baseline that
    clears the absolute allowance; warning otherwise.
    '''
    if current == 0 and baseline >= rules['tolerance_abs_min']:
        return CRITICAL
    if abs(current - baseline) >= rules['critical_tolerance_multiple'] * tolerance(baseline, rules):
        return CRITICAL
    return WARNING


def delta(current, baseline):
    '''Difference from the Baseline.'''
    return current - baseline


def delta_pct(current, baseline):
    '''Difference from the Baseline as a percentage with one decimal; None for a zero Baseline.'''
    if baseline == 0:
        return None
    return round((current - baseline) / baseline * 100, 1)
