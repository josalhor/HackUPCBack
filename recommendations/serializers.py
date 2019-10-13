from rest_framework import serializers
from rest_framework_bulk import BulkSerializerMixin

from recommendations import models


class PreferenceSerializer(serializers.ModelSerializer, BulkSerializerMixin):
    class Meta:
        model = models.Preference
        read_only_fields = ('session_id',)
        fields = ('preference_name', 'value')

class RealEstateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RealEstateImage
        fields = ('image',)

class RealEstateSerializer(serializers.ModelSerializer):
    images = RealEstateImageSerializer(read_only=True, many=True)
    class Meta:
        model = models.RealEstate
        fields = ('id', 'promotion_id', 'rooms', 'bathrooms', 'surface',
        'location', 'latitude', 'longitude', 'images')


class SessionSerializer(serializers.ModelSerializer):
    preferences = PreferenceSerializer(read_only=True, many=True)
    recommendations = RealEstateSerializer(read_only=True, many=True)

    class Meta:
        model = models.Session
        fields = ('session_id', 'status', 'recommendations', 'email',
                  'preferences')
        read_only_fields = ('creation_time',)
