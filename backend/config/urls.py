from django.contrib import admin
from django.urls import include, path, re_path

from core.exceptions import NotFoundView

# Plain DRF view as a catch-all so unknown routes get the unified error envelope
# even with DEBUG on (Django would otherwise render its HTML technical 404).
handler500 = 'core.exceptions.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls')),
    re_path(r'^.*$', NotFoundView.as_view()),
]
