import pytest
from django.conf import settings

from activity.services import rules

RULES = settings.DASHBOARD_RULES


@pytest.mark.parametrize(
    'baseline, expected',
    [
        (0, 3),
        (1, 3),
        (3, 3),
        (4, 3),
        (10, 4.743),
        (40, 12),
    ],
)
def test_tolerance_is_the_largest_of_the_absolute_relative_and_square_root_allowances(
    baseline, expected
):
    assert rules.tolerance(baseline, RULES) == pytest.approx(expected, abs=0.001)


def test_a_small_swing_from_three_to_one_is_noise_not_a_verdict():
    assert rules.status(1, 3, 8, RULES) == 'typical'


def test_nothing_against_a_baseline_of_nothing_is_typical():
    assert rules.status(0, 0, 8, RULES) == 'typical'


def test_a_metric_that_appears_from_a_zero_baseline_is_above():
    assert rules.status(3, 0, 8, RULES) == 'above'


def test_a_metric_that_vanishes_from_a_normal_baseline_is_below():
    assert rules.status(0, 5, 8, RULES) == 'below'


@pytest.mark.parametrize(
    'current, expected',
    [(2, 'typical'), (1, 'below'), (6, 'typical'), (7, 'above')],
)
def test_baseline_of_four_flags_at_one_or_less_and_at_seven_or_more(current, expected):
    assert rules.status(current, 4, 8, RULES) == expected


@pytest.mark.parametrize(
    'current, expected',
    [(29, 'typical'), (28, 'below'), (51, 'typical'), (52, 'above')],
)
def test_baseline_of_forty_flags_at_twenty_eight_or_less_and_at_fifty_two_or_more(
    current, expected
):
    assert rules.status(current, 40, 8, RULES) == expected


@pytest.mark.parametrize(
    'weeks_used, expected',
    [(0, 'insufficient_data'), (3, 'insufficient_data'), (4, 'below')],
)
def test_fewer_than_four_weeks_in_the_window_give_no_verdict(weeks_used, expected):
    assert rules.status(0, 10, weeks_used, RULES) == expected


def test_a_scope_with_no_activity_is_insufficient_whatever_the_zero_baseline_says():
    assert rules.status(0, 0, 8, RULES, has_activity=False) == 'insufficient_data'


def test_dropping_from_five_to_zero_is_critical():
    assert rules.severity(0, 5, RULES) == 'critical'


def test_appearing_from_nothing_to_three_is_only_a_warning():
    assert rules.severity(3, 0, RULES) == 'warning'


def test_zero_against_a_baseline_below_three_is_not_critical_on_its_own():
    assert rules.severity(0, 2, RULES) == 'warning'


@pytest.mark.parametrize(
    'current, baseline, expected',
    [(1, 10, 'warning'), (0, 10, 'critical'), (19, 10, 'warning'), (20, 10, 'critical')],
)
def test_a_deviation_of_twice_the_tolerance_is_critical(current, baseline, expected):
    assert rules.severity(current, baseline, RULES) == expected


def test_delta_is_the_difference_and_delta_pct_has_one_decimal():
    assert rules.delta(51, 42) == 9
    assert rules.delta_pct(51, 42) == 21.4


def test_delta_pct_of_a_drop_is_negative():
    assert rules.delta(1, 8) == -7
    assert rules.delta_pct(1, 8) == -87.5


def test_delta_pct_is_undefined_against_a_zero_baseline():
    assert rules.delta(3, 0) == 3
    assert rules.delta_pct(3, 0) is None
