from django.shortcuts import get_object_or_404
from rest_framework.views import APIView

from accounts.models import Account
from activity.services import dashboard
from core.responses import success_response

from .serializers import ActivitySummaryParamsSerializer, WeekParamsSerializer


class ActivitySummaryView(APIView):
    def get(self, request, account_id):
        account = get_object_or_404(Account, pk=account_id)
        params = ActivitySummaryParamsSerializer(
            data=request.query_params, context={'account': account}
        )
        params.is_valid(raise_exception=True)
        return success_response(
            dashboard.activity_summary(
                account,
                params.validated_data['week_start'],
                params.validated_data['location'],
            )
        )


class AttentionView(APIView):
    def get(self, request, account_id):
        account = get_object_or_404(Account, pk=account_id)
        params = WeekParamsSerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        return success_response(dashboard.attention(account, params.validated_data['week_start']))
