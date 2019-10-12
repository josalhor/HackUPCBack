from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework_bulk import ListBulkCreateDestroyAPIView

from recommendations import models, serializers
from recommendations.recommendation import update_recommendations


@csrf_exempt
@api_view(http_method_names=['POST'])
def typeform_webhook_endpoint(request, *args, **kwargs):
    json_data = request.data
    # TODO parse form data
    print(json_data)

    return JsonResponse(json_data)


class SessionList(generics.ListCreateAPIView):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer


class SessionDetail(generics.RetrieveDestroyAPIView):
    lookup_field = 'session_id'
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer


class PreferencesList(ListBulkCreateDestroyAPIView):
    serializer_class = serializers.PreferenceSerializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return models.Preference.objects.filter(session__session_id=session_id)

    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        serializer.save(session_id=session_id)
        update_recommendations(session_id)
