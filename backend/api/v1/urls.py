from django.urls import include, path

urlpatterns = [
    path('health/', include('api.v1.health.urls')),
]
