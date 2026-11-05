from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'industry', 'timezone', 'created_at')
    list_filter = ('industry', 'timezone')
    search_fields = ('name',)
