from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin

from recommendations import models


class PreferenceSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    class Meta:
        model = models.Preference
        read_only_fields = ('session_id',)
        fields = ('preference_name', 'value')


class SessionSerializer(serializers.ModelSerializer):
    preferences = PreferenceSerializer(read_only=True, many=True)

    class Meta:
        model = models.Session
        fields = '__all__'
