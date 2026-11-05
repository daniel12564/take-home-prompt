'''Reporting Week arithmetic. Pure functions over plain data: no database, no settings.'''

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ReportingWeek:
    '''A Monday-to-Sunday week; `starts_at`/`ends_at` are UTC bounds (end exclusive).'''

    start: date
    end: date
    starts_at: datetime
    ends_at: datetime


def _local_midnight_utc(day, tz_name):
    local = datetime.combine(day, time(0, 0), tzinfo=ZoneInfo(tz_name))
    return local.astimezone(timezone.utc)


def week_containing(moment, tz_name):
    '''Reporting Week of a date, or of an aware timestamp read in the Account's timezone.'''
    if isinstance(moment, datetime):
        moment = moment.astimezone(ZoneInfo(tz_name)).date()
    start = moment - timedelta(days=moment.weekday())
    next_start = start + timedelta(days=7)
    return ReportingWeek(
        start=start,
        end=start + timedelta(days=6),
        starts_at=_local_midnight_utc(start, tz_name),
        ends_at=_local_midnight_utc(next_start, tz_name),
    )


def default_week_start(reference_date):
    '''Monday of the last Reporting Week that ended before the Reference Date.'''
    return reference_date - timedelta(days=reference_date.weekday() + 7)


def first_week_start(data_start):
    '''First Monday on or after the first day of data.'''
    return data_start + timedelta(days=-data_start.weekday() % 7)


def selectable_week_starts(reference_date, data_start):
    '''Every selectable Monday, oldest first: first data Monday through the default week.'''
    last = default_week_start(reference_date)
    first = first_week_start(data_start)
    return [first + timedelta(weeks=index) for index in range((last - first).days // 7 + 1)]


NOT_A_MONDAY = 'not_a_monday'
BEFORE_DATA_START = 'before_data_start'
NOT_COMPLETE = 'not_complete'


def week_start_rejection(week_start, reference_date, data_start):
    '''Why a `week_start` cannot be selected, or None when it can.'''
    if week_start.weekday() != 0:
        return NOT_A_MONDAY
    if week_start < first_week_start(data_start):
        return BEFORE_DATA_START
    if week_start > default_week_start(reference_date):
        return NOT_COMPLETE
    return None


def is_valid_week_start(week_start, reference_date, data_start):
    return week_start_rejection(week_start, reference_date, data_start) is None
