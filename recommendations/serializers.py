from rest_framework import serializers

from recommendations import models


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Session
        fields = '__all__'


class SessionSerializer(serializers.ModelSerializer):
    preferences = PreferenceSerializer(read_only=True)

    class Meta:
        model = models.Session
        fields = '__all__'
