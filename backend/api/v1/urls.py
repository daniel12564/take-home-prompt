from django.urls import include, path

urlpatterns = [
    path('health/', include('api.v1.health.urls')),
    path('accounts/', include('api.v1.accounts.urls')),
    path('accounts/<int:account_id>/dashboard/', include('api.v1.dashboard.urls')),
]
