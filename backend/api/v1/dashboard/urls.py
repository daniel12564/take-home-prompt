from django.urls import path

from .views import ActivitySummaryView, AttentionView

urlpatterns = [
    path('activity-summary/', ActivitySummaryView.as_view(), name='dashboard-activity-summary'),
    path('attention/', AttentionView.as_view(), name='dashboard-attention'),
]
