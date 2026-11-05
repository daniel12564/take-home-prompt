from django.conf import settings
from rest_framework import serializers

from activity.models import ActivityEvent
from activity.services import periods

WEEK_START_MESSAGES = {
    periods.NOT_A_MONDAY: 'week_start must be a Monday.',
    periods.BEFORE_DATA_START: 'week_start is before the first week with data ({first}).',
    periods.NOT_COMPLETE: 'week_start must be a complete week before the reference date ({reference}).',
}


class WeekParamsSerializer(serializers.Serializer):
    '''Validates the optional `week_start` shared by every dashboard endpoint.'''

    week_start = serializers.DateField(required=False)

    def validate_week_start(self, value):
        reason = periods.week_start_rejection(
            value, settings.DASHBOARD_REFERENCE_DATE, settings.DASHBOARD_DATA_START_DATE
        )
        if reason:
            raise serializers.ValidationError(
                WEEK_START_MESSAGES[reason].format(
                    first=periods.first_week_start(settings.DASHBOARD_DATA_START_DATE).isoformat(),
                    reference=settings.DASHBOARD_REFERENCE_DATE.isoformat(),
                )
            )
        return value

    def validate(self, attrs):
        attrs.setdefault('week_start', periods.default_week_start(settings.DASHBOARD_REFERENCE_DATE))
        return attrs


class ActivitySummaryParamsSerializer(WeekParamsSerializer):
    '''Validates the query string; needs `account` in the context.'''

    location = serializers.CharField(required=False, allow_blank=True)

    def validate_location(self, value):
        if value and value not in ActivityEvent.objects.location_names(self.context['account']):
            raise serializers.ValidationError('Unknown location for this account.')
        return value or None

    def validate(self, attrs):
        attrs = super().validate(attrs)
        attrs.setdefault('location', None)
        return attrs
