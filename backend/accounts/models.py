from django.db import models
from django.db.models import Count
from django.utils.timezone import now


class AccountQuerySet(models.QuerySet):
    def with_location_count(self):
        '''Annotate all-time distinct Locations; Locations live on the events, not a table.'''
        return self.annotate(location_count=Count('events__location', distinct=True))


class Account(models.Model):
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100)
    timezone = models.CharField(max_length=64)
    created_at = models.DateTimeField(default=now)

    objects = AccountQuerySet.as_manager()

    class Meta:
        db_table = 'accounts'
        ordering = ['id']

    def __str__(self):
        return self.name
