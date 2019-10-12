# -*- coding: utf-8 -*-
import random
from typing import List

from guatajaus.celery import app
from recommendations import models

N_OPTIONS = 10


def fetch_options(preferences: List[models.Preference]) -> List[models.RealEstate]:
    return []  # TODO


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
