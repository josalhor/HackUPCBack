from rest_framework import generics
from recommendations import models, serializers


class SessionList(generics.ListCreateAPIView):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer


class SessionDetail(generics.RetrieveDestroyAPIView):
    lookup_field = 'session_id'
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer


class PreferencesList(generics.ListCreateAPIView):
    serializer_class = serializers.PreferenceSerializer

    def get_queryset(self):
        session_id = self.kwargs['session_id']
        return models.Preference.objects.filter(session__session_id=session_id)

    def perform_create(self, serializer):
        session_id = self.kwargs['session_id']
        serializer.save(session_id=session_id)
