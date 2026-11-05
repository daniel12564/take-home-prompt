from django.contrib import admin

from .models import ActivityEvent


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'location', 'event_type', 'occurred_at', 'outcome')
    list_filter = ('event_type', 'outcome', 'account')
    list_select_related = ('account',)
    raw_id_fields = ('account',)
    date_hierarchy = 'occurred_at'
