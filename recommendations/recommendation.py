# -*- coding: utf-8 -*-
from guatajaus.celery import app
from recommendations import models
import time


@app.task
def update_recommendations(session_id):
    # TODO
    session = models.Session.objects.get(session_id=session_id)
    session.status = models.Session.COMPLETED
    time.sleep(10)
    session.save()