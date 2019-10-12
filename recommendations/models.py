import uuid

from django.db import models


class RealEstate(models.Model):
    url = models.URLField(null=False)


class Session(models.Model):
    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    STATUS = (
        (PENDING, 'Pending to be processed'),
        (IN_PROGRESS, 'The session is being processed'),
        (COMPLETED, 'The session has been processed')
    )
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default=PENDING)
    recommendations = models.ManyToManyField(RealEstate)


class Preference(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="preferences")
    preference_name = models.CharField(max_length=30, blank=False, null=False)
    value = models.TextField(max_length=100, blank=True, null=True)
    is_mandatory = models.BooleanField(null=False, default=False)