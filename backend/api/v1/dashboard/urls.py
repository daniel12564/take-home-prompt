from django.urls import path

from .views import ActivitySummaryView

urlpatterns = [
    path('activity-summary/', ActivitySummaryView.as_view(), name='dashboard-activity-summary'),
]
