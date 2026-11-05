from django.db import models

from .managers import ActivityEventQuerySet


class ActivityEvent(models.Model):
    class EventType(models.TextChoices):
        CALL_RECEIVED = 'call_received'
        LEAD_CREATED = 'lead_created'
        APPOINTMENT_SET = 'appointment_set'

    class Outcome(models.TextChoices):
        CONNECTED = 'connected'
        MISSED = 'missed'
        VOICEMAIL = 'voicemail'
        OPEN = 'open'
        CONVERTED = 'converted'
        COMPLETED = 'completed'
        NO_SHOW = 'no_show'

    account = models.ForeignKey(
        'accounts.Account', on_delete=models.PROTECT, related_name='events'
    )
    location = models.CharField(max_length=100)
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    occurred_at = models.DateTimeField()
    duration_seconds = models.IntegerField(null=True, blank=True)
    outcome = models.CharField(max_length=20, choices=Outcome.choices, null=True, blank=True)

    objects = ActivityEventQuerySet.as_manager()

    class Meta:
        db_table = 'activity_events'
        indexes = [
            models.Index(fields=['account', 'occurred_at'], name='ae_account_occurred_idx'),
            models.Index(
                fields=['account', 'location', 'event_type', 'occurred_at'],
                name='ae_account_loc_type_occ_idx',
            ),
        ]

    def __str__(self):
        return f'{self.event_type} @ {self.location} ({self.occurred_at:%Y-%m-%d %H:%M})'
