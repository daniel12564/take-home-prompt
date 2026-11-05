from datetime import date, datetime, timezone

from activity.services import periods

REFERENCE_DATE = date(2026, 7, 27)
DATA_START = date(2026, 2, 1)


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_week_in_chicago_spans_local_midnights_expressed_in_utc():
    week = periods.week_containing(date(2026, 7, 22), 'America/Chicago')

    assert week.start == date(2026, 7, 20)
    assert week.end == date(2026, 7, 26)
    assert week.starts_at == utc(2026, 7, 20, 5)
    assert week.ends_at == utc(2026, 7, 27, 5)


def test_week_in_phoenix_has_no_daylight_saving_shift():
    week = periods.week_containing(date(2026, 3, 12), 'America/Phoenix')

    assert week.start == date(2026, 3, 9)
    assert week.starts_at == utc(2026, 3, 9, 7)
    assert week.ends_at == utc(2026, 3, 16, 7)


def test_week_in_utc_starts_and_ends_at_utc_midnight():
    week = periods.week_containing(date(2026, 7, 26), 'UTC')

    assert week.start == date(2026, 7, 20)
    assert week.end == date(2026, 7, 26)
    assert week.starts_at == utc(2026, 7, 20)
    assert week.ends_at == utc(2026, 7, 27)


def test_week_crossing_daylight_saving_still_ends_at_local_midnight():
    week = periods.week_containing(date(2026, 3, 5), 'America/Chicago')

    assert week.starts_at == utc(2026, 3, 2, 6)
    assert week.ends_at == utc(2026, 3, 9, 5)


def test_sunday_2330_local_timestamp_belongs_to_the_earlier_week():
    # Sunday 2026-07-26 23:30 in Chicago (CDT, UTC-5) is already Monday 04:30 UTC.
    sunday_night = utc(2026, 7, 27, 4, 30)

    chicago = periods.week_containing(sunday_night, 'America/Chicago')
    utc_week = periods.week_containing(sunday_night, 'UTC')

    assert chicago.start == date(2026, 7, 20)
    assert chicago.starts_at <= sunday_night < chicago.ends_at
    assert utc_week.start == date(2026, 7, 27)


def test_monday_0030_local_timestamp_belongs_to_the_later_week():
    # Monday 2026-07-27 00:30 in Chicago is 05:30 UTC.
    week = periods.week_containing(utc(2026, 7, 27, 5, 30), 'America/Chicago')

    assert week.start == date(2026, 7, 27)


def test_default_week_is_the_last_complete_week_before_a_monday_reference_date():
    assert periods.default_week_start(REFERENCE_DATE) == date(2026, 7, 20)


def test_default_week_mid_week_excludes_the_in_progress_week():
    assert periods.default_week_start(date(2026, 7, 29)) == date(2026, 7, 20)
    assert periods.default_week_start(date(2026, 7, 26)) == date(2026, 7, 13)


def test_selectable_range_runs_from_first_monday_of_data_to_the_default_week():
    weeks = periods.selectable_week_starts(REFERENCE_DATE, DATA_START)

    assert weeks[0] == date(2026, 2, 2)
    assert weeks[-1] == date(2026, 7, 20)
    assert len(weeks) == 25
    assert all(week.weekday() == 0 for week in weeks)
    assert all((later - earlier).days == 7 for earlier, later in zip(weeks, weeks[1:]))


def test_selectable_range_starts_on_the_data_start_when_it_is_a_monday():
    assert periods.selectable_week_starts(REFERENCE_DATE, date(2026, 2, 2))[0] == date(2026, 2, 2)


def test_selectable_range_never_includes_the_in_progress_week():
    assert date(2026, 7, 27) not in periods.selectable_week_starts(REFERENCE_DATE, DATA_START)


def rejection(week_start):
    return periods.week_start_rejection(week_start, REFERENCE_DATE, DATA_START)


def test_range_endpoints_are_valid():
    assert rejection(date(2026, 2, 2)) is None
    assert rejection(date(2026, 7, 20)) is None
    assert periods.is_valid_week_start(date(2026, 7, 20), REFERENCE_DATE, DATA_START)


def test_a_date_that_is_not_a_monday_is_rejected():
    assert rejection(date(2026, 7, 21)) == periods.NOT_A_MONDAY
    assert rejection(date(2026, 7, 26)) == periods.NOT_A_MONDAY


def test_a_monday_before_the_first_data_week_is_rejected():
    assert rejection(date(2026, 1, 26)) == periods.BEFORE_DATA_START


def test_the_week_starting_on_the_reference_date_is_rejected_as_incomplete():
    assert rejection(date(2026, 7, 27)) == periods.NOT_COMPLETE
    assert not periods.is_valid_week_start(date(2026, 7, 27), REFERENCE_DATE, DATA_START)


def test_a_future_monday_is_rejected_as_incomplete():
    assert rejection(date(2026, 8, 3)) == periods.NOT_COMPLETE


def test_a_non_monday_before_the_data_start_reports_not_a_monday_first():
    assert rejection(date(2026, 1, 28)) == periods.NOT_A_MONDAY
