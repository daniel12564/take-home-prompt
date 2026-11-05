from datetime import date

from django.conf import settings

from activity.services import baseline

RULES = settings.DASHBOARD_RULES
FIRST_WEEK = date(2026, 2, 2)


def test_window_is_the_eight_complete_weeks_before_the_viewed_week_oldest_first():
    window = baseline.baseline_window(date(2026, 7, 20), FIRST_WEEK, RULES)

    assert window == [
        date(2026, 5, 25),
        date(2026, 6, 1),
        date(2026, 6, 8),
        date(2026, 6, 15),
        date(2026, 6, 22),
        date(2026, 6, 29),
        date(2026, 7, 6),
        date(2026, 7, 13),
    ]


def test_window_is_clipped_at_the_first_week_of_data():
    window = baseline.baseline_window(date(2026, 2, 23), FIRST_WEEK, RULES)

    assert window == [date(2026, 2, 2), date(2026, 2, 9), date(2026, 2, 16)]


def test_the_first_week_of_data_has_an_empty_window():
    assert baseline.baseline_window(FIRST_WEEK, FIRST_WEEK, RULES) == []


def test_window_is_full_again_once_eight_weeks_of_data_exist():
    window = baseline.baseline_window(date(2026, 3, 30), FIRST_WEEK, RULES)

    assert len(window) == 8
    assert window[0] == FIRST_WEEK


def test_median_of_an_even_number_of_weeks_averages_the_middle_two():
    assert baseline.median([2, 9, 4, 3]) == 3.5


def test_median_of_an_odd_number_of_weeks_is_the_middle_one():
    assert baseline.median([7, 1, 4]) == 4


def test_median_of_no_weeks_is_undefined():
    assert baseline.median([]) is None


def test_one_week_ten_times_the_rest_does_not_move_the_baseline():
    steady = [4, 5, 4, 5, 4, 5, 4, 5]
    with_spike = [4, 5, 4, 50, 4, 5, 4, 5]

    assert baseline.median(with_spike) == baseline.median(steady) == 4.5


def row(week, count, event_type='call_received', location='North'):
    return {'location': location, 'event_type': event_type, 'week': week, 'count': count}


def test_weekly_totals_fill_weeks_without_events_with_zero():
    weeks = [date(2026, 7, 6), date(2026, 7, 13)]
    rows = [row(date(2026, 7, 13), 4)]

    assert baseline.weekly_totals(rows, weeks, 'call_received') == [0, 4]


def test_weekly_totals_ignore_other_event_types():
    weeks = [date(2026, 7, 6)]
    rows = [row(date(2026, 7, 6), 4), row(date(2026, 7, 6), 9, event_type='lead_created')]

    assert baseline.weekly_totals(rows, weeks, 'call_received') == [4]


def test_account_scope_sums_locations_week_by_week_before_taking_the_median():
    weeks = [date(2026, 7, 6), date(2026, 7, 13), date(2026, 7, 20)]
    rows = [
        row(weeks[0], 10, location='North'),
        row(weeks[1], 1, location='North'),
        row(weeks[1], 9, location='South'),
        row(weeks[2], 2, location='North'),
        row(weeks[2], 2, location='South'),
    ]

    totals = baseline.weekly_totals(rows, weeks, 'call_received')

    # weekly sums are 10, 10 and 4: the median is 10, while the sum of each Location's own
    # median (North 2 + South 2) would wrongly say 4
    assert totals == [10, 10, 4]
    assert baseline.median(totals) == 10


def test_march_second_is_the_first_week_whose_window_meets_the_minimum_weeks():
    def weeks_used(week_start):
        return len(baseline.baseline_window(week_start, FIRST_WEEK, RULES))

    assert weeks_used(date(2026, 2, 23)) < RULES['min_baseline_weeks']
    assert weeks_used(date(2026, 3, 2)) == RULES['min_baseline_weeks']
