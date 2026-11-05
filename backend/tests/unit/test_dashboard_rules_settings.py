from django.conf import settings


def test_every_rule_constant_lives_in_the_one_dashboard_rules_dictionary():
    assert settings.DASHBOARD_RULES == {
        'baseline_weeks': 8,
        'min_baseline_weeks': 4,
        'tolerance_abs_min': 3,
        'tolerance_rel': 0.30,
        'tolerance_sqrt_factor': 1.5,
        'critical_tolerance_multiple': 2,
        'rollup_min_locations': 3,
        'rollup_min_share': 0.5,
        'one_day_concentration_share': 0.6,
    }
