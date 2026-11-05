from zoneinfo import ZoneInfo

from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncWeek

from .services import periods


class ActivityEventQuerySet(models.QuerySet):
    def location_names(self, account):
        '''All-time distinct Location names of an Account, sorted.'''
        return list(
            self.filter(account=account)
            .order_by('location')
            .values_list('location', flat=True)
            .distinct()
        )

    def weekly_counts(self, account, week_starts, location=None):
        '''Event counts per Location, Event Type and Reporting Week, in one grouped query.

        Weeks are truncated in the Account's timezone. Returns dicts with `location`,
        `event_type`, `week` (the Monday as a date) and `count`; combinations with no
        events are absent. `location` narrows the counts to one Location.
        '''
        zone = ZoneInfo(account.timezone)
        bounds = [periods.week_containing(start, account.timezone) for start in week_starts]
        events = self.filter(
            account=account,
            occurred_at__gte=min(week.starts_at for week in bounds),
            occurred_at__lt=max(week.ends_at for week in bounds),
        )
        if location is not None:
            events = events.filter(location=location)
        rows = (
            events.annotate(week=TruncWeek('occurred_at', tzinfo=zone))
            .values('location', 'event_type', 'week')
            .annotate(count=Count('id'))
        )
        wanted = {week.start for week in bounds}
        counts = [{**row, 'week': row['week'].date()} for row in rows]
        return [row for row in counts if row['week'] in wanted]

    def daily_counts(self, account, week_start):
        '''Event counts per Event Type and local day of one Reporting Week, in one grouped query.

        Days are truncated in the Account's timezone. Returns dicts with `event_type`, `day`
        (a date) and `count`; days with no events are absent.
        '''
        week = periods.week_containing(week_start, account.timezone)
        return list(
            self.filter(
                account=account, occurred_at__gte=week.starts_at, occurred_at__lt=week.ends_at
            )
            .annotate(day=TruncDate('occurred_at', tzinfo=ZoneInfo(account.timezone)))
            .values('event_type', 'day')
            .annotate(count=Count('id'))
        )
