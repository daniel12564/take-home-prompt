from django.db import models


class ActivityEventQuerySet(models.QuerySet):
    def location_names(self, account):
        '''All-time distinct Location names of an Account, sorted.'''
        return list(
            self.filter(account=account)
            .order_by('location')
            .values_list('location', flat=True)
            .distinct()
        )
