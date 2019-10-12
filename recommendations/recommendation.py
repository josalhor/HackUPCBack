# -*- coding: utf-8 -*-
import random
import os
from typing import List
from django.db import transaction

from guatajaus.celery import app
from recommendations import models
from recommendations.scraping_api import request_location_segments, real_estate_location

N_OPTIONS = 10


def get_coordinates_location(location):
    code_api = os.environ['GEOCODE_API']
    import geocoder
    js = geocoder.mapquest(location, key=code_api).json
    return js['lat'], js['lng']


def fetch_options(preferences: List[models.Preference]) -> List[models.RealEstate]:
    segments = request_location_segments("lleida-capital")
    real_estates = real_estate_location(segments, 3)
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
    print(preferences)
    return random.sample(available_options, n)  # TODO

NUM_PARAM = 5

def vector_user(preferences: List[models.Preference]):
    vector = [None] * NUM_PARAM
    for pref in preferences:
        name = getattr(pref, 'preference_name')
        value = getattr(pref, 'value')
        if name == 'location':
            lat, lng = get_coordinates_location(value)
            vector[0] = lat
            vector[1] = lng
        elif name == 'm2':
            vector[2] = float(value) # discretize choice
        elif name == 'bedrooms':
            vector[3] = float(value)
        elif name == 'bathroom':
            vector[4] = float(value)
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
    return vector

def get_recommendation(user_vector, matrix_houses, real_estates):
    user_vector = np.asarray(user_vector)
    new_matrix = []
    for line in matrix_houses:
        line = np.asarray(line)
        new_matrix.append(line)
    matrix_houses = np.asarray(new_matrix)
    #TODO: Modify space to get rational recommendation
    distances = euclidean_distances(matrix_houses, user_vector)
    distances = distances.tolist()
    distances = list(zip(distances, real_estates))
    ordered = distances.sort(key=(lambda x: x[0]))
    return list(map(lambda x: x[1], ordered))

@app.task
def update_recommendations(session_id: int):
    session = models.Session.objects.get(session_id=session_id)
    session.status = models.Session.IN_PROGRESS
    session.save()

    available_options = fetch_options(session.preferences)
    recommendations = get_n_best_options(N_OPTIONS, session.preferences,
                                         available_options)
    session.recommendations.add(*recommendations)
    session.status = models.Session.COMPLETED
    session.save()
