# -*- coding: utf-8 -*-
import random
from typing import List
from django.db import transaction

from guatajaus.celery import app
from recommendations import models
from recommendations.scraping_api import request_location_segments, real_estate_location

N_OPTIONS = 10


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
    return random.sample(available_options, n)  # TODO


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
