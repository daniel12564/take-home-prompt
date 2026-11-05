from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import pytest

from accounts.models import Account
from activity.models import ActivityEvent

DEFAULT_WEEK = date(2026, 7, 20)
FIXTURE_WEEKS = [DEFAULT_WEEK - timedelta(weeks=9 - index) for index in range(10)]
SPIKE_WEEK = FIXTURE_WEEKS[5]
STEADY_VOLUMES = {
    ActivityEvent.EventType.CALL_RECEIVED: 5,
    ActivityEvent.EventType.LEAD_CREATED: 2,
    ActivityEvent.EventType.APPOINTMENT_SET: 1,
}
OUTCOMES = {
    ActivityEvent.EventType.CALL_RECEIVED: ActivityEvent.Outcome.CONNECTED,
    ActivityEvent.EventType.LEAD_CREATED: ActivityEvent.Outcome.OPEN,
    ActivityEvent.EventType.APPOINTMENT_SET: ActivityEvent.Outcome.COMPLETED,
}


@dataclass(frozen=True)
class DashboardFixture:
    account_a: Account
    account_b: Account
    default_week: date
    weeks: list


def build_events(account, location, event_type, week_start, count):
    zone = ZoneInfo(account.timezone)
    monday = datetime.combine(week_start, time(0, 0), tzinfo=zone)
    return [
        ActivityEvent(
            account=account,
            location=location,
            event_type=event_type,
            occurred_at=monday + timedelta(days=1 + index % 5, hours=9, minutes=index),
            outcome=OUTCOMES[event_type],
        )
        for index in range(count)
    ]


def build_dashboard_fixture():
    '''Handcrafted dataset shared by every API test.

    Account A (America/Chicago): North, South and East, ten Reporting Weeks ending at
    the default week, each Location steady at 5 calls, 2 leads and 1 appointment a
    week, plus three planted signals: South has no events in the default week, North
    has 11 calls in the default week, and every Location has 4x calls in week 6.
    Account B (UTC) has no Activity Events.
    '''
    account_a = Account.objects.create(
        name='Account A', industry='Testing', timezone='America/Chicago'
    )
    account_b = Account.objects.create(name='Account B', industry='Testing', timezone='UTC')

    events = []
    for location in ('North', 'South', 'East'):
        for week_start in FIXTURE_WEEKS:
            for event_type, volume in STEADY_VOLUMES.items():
                if location == 'South' and week_start == DEFAULT_WEEK:
                    continue
                if event_type == ActivityEvent.EventType.CALL_RECEIVED:
                    if location == 'North' and week_start == DEFAULT_WEEK:
                        volume = 11
                    if week_start == SPIKE_WEEK:
                        volume = volume * 4
                events.extend(build_events(account_a, location, event_type, week_start, volume))
    ActivityEvent.objects.bulk_create(events)

    return DashboardFixture(
        account_a=account_a,
        account_b=account_b,
        default_week=DEFAULT_WEEK,
        weeks=FIXTURE_WEEKS,
    )


@pytest.fixture
def dashboard_fixture(db):
    return build_dashboard_fixture()
