from rest_framework.views import APIView

from core.responses import success_response


class HealthView(APIView):
    def get(self, request):
        return success_response({'status': 'ok'})
