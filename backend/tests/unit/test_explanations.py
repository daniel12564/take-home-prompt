from datetime import date

from activity.services import explanations


def test_a_location_that_received_no_calls_says_what_it_typically_receives():
    text = explanations.location_metric('Site B', 'call_received', 0, 5.0)

    assert text == 'Site B received 0 calls this week; it typically receives about 5.'


def test_a_surge_in_leads_uses_the_lead_verb_and_a_fractional_baseline():
    text = explanations.location_metric('Site H', 'lead_created', 6, 2.5)

    assert text == 'Site H created 6 leads this week; it typically creates about 2.5.'


def test_a_count_of_one_is_singular():
    text = explanations.location_metric('Site C', 'appointment_set', 1, 6.0)

    assert text == 'Site C set 1 appointment this week; it typically sets about 6.'


def test_a_large_baseline_is_never_written_in_scientific_notation():
    text = explanations.location_metric('Site A', 'call_received', 0, 1234567.0)

    assert text == 'Site A received 0 calls this week; it typically receives about 1234567.'


def test_a_location_that_went_silent_has_its_own_explanation():
    text = explanations.no_activity('Site G')

    assert text == (
        'Site G recorded no calls, leads or appointments this week; it is normally active.'
    )


def test_an_account_wide_surge_in_one_metric_counts_the_affected_locations():
    text = explanations.account_wide(
        ('call_received',), 'above', {'call_received': 15}, 15, 529, 41.0, None
    )

    assert text == 'Calls were far above typical at 15 of 15 locations (529 calls vs about 41).'


def test_an_account_wide_drop_in_leads_names_the_metric_and_the_direction():
    text = explanations.account_wide(
        ('lead_created',), 'below', {'lead_created': 4}, 5, 3, 12.5, None
    )

    assert text == 'Leads were far below typical at 4 of 5 locations (3 leads vs about 12.5).'


def test_a_merged_account_wide_finding_lists_the_metrics_and_gives_a_range_when_counts_differ():
    text = explanations.account_wide(
        ('call_received', 'lead_created', 'appointment_set'),
        'above',
        {'call_received': 15, 'lead_created': 15, 'appointment_set': 14},
        15,
        529,
        41.0,
        None,
    )

    assert text == (
        'Calls, leads and appointments were far above typical at 14 to 15 of 15 locations '
        '(529 calls vs about 41).'
    )


def test_a_merged_account_wide_finding_with_equal_counts_gives_a_single_number():
    text = explanations.account_wide(
        ('call_received', 'appointment_set'),
        'above',
        {'call_received': 3, 'appointment_set': 3},
        4,
        60,
        20.0,
        None,
    )

    assert text == (
        'Calls and appointments were far above typical at 3 of 4 locations '
        '(60 calls vs about 20).'
    )


def test_a_count_of_one_in_an_account_wide_finding_is_singular():
    text = explanations.account_wide(
        ('appointment_set',), 'below', {'appointment_set': 3}, 3, 1, 9.0, None
    )

    assert text == (
        'Appointments were far below typical at 3 of 3 locations (1 appointment vs about 9).'
    )


def test_the_day_callout_names_the_day_without_a_leading_zero():
    text = explanations.account_wide(
        ('call_received', 'lead_created', 'appointment_set'),
        'above',
        {'call_received': 15, 'lead_created': 15, 'appointment_set': 14},
        15,
        529,
        41.0,
        date(2026, 6, 3),
    )

    assert text == (
        'Calls, leads and appointments were far above typical at 14 to 15 of 15 locations '
        "(529 calls vs about 41). Most of this week's events happened on Wed 3 Jun."
    )


def test_the_day_callout_works_for_a_two_digit_day_and_a_single_metric():
    text = explanations.account_wide(
        ('call_received',), 'above', {'call_received': 3}, 3, 60, 15.0, date(2026, 6, 14)
    )

    assert text == (
        'Calls were far above typical at 3 of 3 locations (60 calls vs about 15). '
        "Most of this week's events happened on Sun 14 Jun."
    )
