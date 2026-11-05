from django.urls import path

from .views import AccountListView, AccountLocationListView

urlpatterns = [
    path('', AccountListView.as_view(), name='account-list'),
    path('<int:account_id>/locations/', AccountLocationListView.as_view(), name='account-locations'),
]
