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
