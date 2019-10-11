import uuid

from django.db import models


class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Preference(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="preferences")
    preference_name = models.CharField(max_length=30, blank=False, null=False)
    value = models.TextField(max_length=100, blank=True, null=True)