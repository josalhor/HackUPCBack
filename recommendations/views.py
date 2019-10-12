from rest_framework import generics
from recommendations import models, serializers


class SessionList(generics.ListCreateAPIView):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer
