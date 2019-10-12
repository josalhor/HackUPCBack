# -*- coding: utf-8 -*-
import random
from typing import List

from guatajaus.celery import app
from recommendations import models
from recommendations.scraping_api import request_location_segments, real_estate_location

N_OPTIONS = 10


def fetch_options(preferences: List[models.Preference]) -> List[models.RealEstate]:
    segments = request_location_segments("lleida-capital")
    real_estates = real_estate_location(segments, 3)
    model_estate = []
    for real_estate in real_estates:
        obj, _ = models.RealEstate.objects.get_or_create(
            id=real_estate.id
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
