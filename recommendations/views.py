from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework_bulk import ListBulkCreateDestroyAPIView

from recommendations import models, serializers, typeform
from recommendations.recommendation import update_recommendations


@csrf_exempt
@api_view(http_method_names=['POST'])
def typeform_webhook_endpoint(request):
    with transaction.atomic():
        json_data = request.data
        print(json_data)
        answers_data = json_data['form_response']['answers']
        identifier = json_data['form_response']['form_id']
        answers = typeform.parse_answers(answers_data)
        email = answers.pop('email')
        session = models.Session.objects.create(session_id=identifier,
                                                email=email)

        for answer, value in answers.items():
            models.Preference.objects.create(preference_name=answer,
                                             value=value, session=session)

        update_recommendations(session.session_id)
    return HttpResponse('Created correctly')


class LatestSessionList(generics.RetrieveAPIView):
    serializer_class = serializers.SessionSerializer

    def get_object(self):
        email = self.request.query_params['email']
        return models.Session.objects.filter(email=email).latest()


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
