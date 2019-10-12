# -*- coding: utf-8 -*-
import random
import re
import os
from typing import List
from django.db import transaction
import numpy as np
from sklearn.metrics import euclidean_distances
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from guatajaus.celery import app
from recommendations import models
from recommendations.scraping_api import request_location_segments, real_estate_location, count_feature_photos
from .models import Preference, RealEstateImage

N_OPTIONS = 10


def get_coordinates_location(location):
    code_api = os.environ['GEOCODE_API']
    import geocoder
    js = geocoder.mapquest(location, key=code_api).json
    return js['lat'], js['lng']

NUMBER_PAGES = 10
def fetch_options(city: models.Preference) -> List[models.RealEstate]:
    segments = request_location_segments(f"{city.value}-capital")
    for k in range(1, NUMBER_PAGES + 1):
        real_estates = real_estate_location(segments, k)
        model_estate = []
        for real_estate in real_estates:

            locations = real_estate.locations
            if locations:
                locations = locations[-1]
            else:
                locations = ''
            with transaction.atomic():
                obj, _ = models.RealEstate.objects.get_or_create(
                    id=real_estate.id,
                    promotion_id=real_estate.promotionId,
                    rooms=real_estate.rooms,
                    bathrooms=real_estate.bathrooms,
                    surface=real_estate.surface,
                    location=locations,
                    latitude=real_estate.latitude,
                    longitude=real_estate.longitude
                )
                ks = models.RealEstate.objects.get(id=real_estate.id)
                for img in real_estate.multimedia:
                    _, _ = models.RealEstateImage.objects.get_or_create(
                        real_estate_identifier=obj,
                        image=img
                    )
                model_estate.append(obj)
    return model_estate


def get_n_best_options(n: int,
                       preferences: List[models.Preference],
                       available_options: List[models.RealEstate]) -> List[models.RealEstate]:
    vector = vector_user(preferences)
    matrix_houses = list(map(vector_house, available_options))
    recommendations = get_recommendation(vector, matrix_houses, available_options)
    return recommendations

NUM_PARAM = 7

def vector_user(preferences: List[models.Preference]):
    vector = [None] * NUM_PARAM
    for pref in preferences:
        name = getattr(pref, 'preference_name')
        value = getattr(pref, 'value')
        if name == 'city':
            lat, lng = get_coordinates_location(value)
            vector[0] = lat
            vector[1] = lng
        elif name == 'square_meters':
            values = list(map(int, re.findall(r'\d+', value)))
            vector[2] = sum(values) / len(values)
        elif name == 'bedrooms':
            vector[3] = int(value)
        elif name == 'bathrooms':
            vector[4] = int(value)
    
    vector[5] = 10 #Let's max these out now
    vector[6] = 10 #TODO: Adjust those from user input
    return vector

def get_attr_def(obj, attr, default):
    x = getattr(obj, attr)
    if x:
        return x
    return default

def vector_house(real_estate: models.RealEstate):
    vector = [None] * NUM_PARAM
    vector[0] = get_attr_def(real_estate, 'latitude', 0)
    vector[1] = get_attr_def(real_estate, 'longitude', 0)
    vector[2] = get_attr_def(real_estate, 'surface', 0)
    vector[3] = get_attr_def(real_estate, 'bathrooms', 0)
    vector[4] = get_attr_def(real_estate, 'rooms', 0)
    image_objects = RealEstateImage.objects.filter(real_estate_identifier=real_estate)
    image_objects = list(map(lambda x: x.image, image_objects))
    features, appliances = count_feature_photos(image_objects)
    vector[5] = features
    vector[6] = appliances
    return vector

STEPS = [
    ('scale', StandardScaler()),
]
PIPELINE = Pipeline(STEPS)

def list_to_np(ll):
    r = []
    for l in ll:
        r.append(np.asarray(l))
    return np.asarray(r)

def get_recommendation(user_vector, matrix_houses, real_estates):
    user_vector_matrixed = list_to_np([user_vector] + matrix_houses)
    user_vector = PIPELINE.fit_transform(user_vector_matrixed)[0]
    matrix_houses = list_to_np(matrix_houses)
    matrix_houses = PIPELINE.fit_transform(matrix_houses)
    #TODO: Modify space to get rational recommendation
    distances = euclidean_distances(matrix_houses, [user_vector])
    distances = distances.tolist()
    distances = list(zip(distances, real_estates))
    distances.sort(key=(lambda x: x[0]))
    return list(map(lambda x: x[1], distances))

@app.task
def update_recommendations(session_id: int):
    session = models.Session.objects.get(session_id=session_id)
    session.status = models.Session.IN_PROGRESS
    session.save()

    available_options = fetch_options(Preference.objects.get(session=session, preference_name='city'))
    recommendations = get_n_best_options(N_OPTIONS, Preference.objects.filter(session=session),
                                         available_options)
    session.recommendations.add(*recommendations)
    session.status = models.Session.COMPLETED
    session.save()
