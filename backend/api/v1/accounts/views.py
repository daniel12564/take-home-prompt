from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from accounts.models import Account
from activity.models import ActivityEvent
from core.responses import success_response

from .serializers import AccountSerializer


class AccountListView(APIView):
    def get(self, request):
        accounts = Account.objects.with_location_count().order_by('id')
        return success_response(AccountSerializer(accounts, many=True).data)


class AccountLocationListView(APIView):
    def get(self, request, account_id):
        account = get_object_or_404(Account, pk=account_id)
        return success_response(ActivityEvent.objects.location_names(account))
