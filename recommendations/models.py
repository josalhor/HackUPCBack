from django.db import models


class RealEstate(models.Model):
    id = models.IntegerField(primary_key=True)
    promotion_id = models.IntegerField(null=True)
    rooms = models.IntegerField(null=True)
    bathrooms = models.IntegerField(null=True)
    surface = models.IntegerField(null=True)
    location = models.CharField(null=True, max_length=150)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)


class RealEstateImage(models.Model):
    real_estate_identifier = models.ForeignKey(RealEstate,
                                               on_delete=models.CASCADE)
    image = models.URLField(null=False)


class Session(models.Model):
    class Meta:
        get_latest_by = ('-creation_time')

    PENDING = 'pending'
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    STATUS = (
        (PENDING, 'Pending to be processed'),
        (IN_PROGRESS, 'The session is being processed'),
        (COMPLETED, 'The session has been processed')
    )
    session_id = models.CharField(max_length=40, primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS, default=PENDING)
    creation_time = models.DateTimeField(auto_now_add=True, blank=False,
                                         null=False)
    email = models.EmailField(blank=False, null=False)
    recommendations = models.ManyToManyField(RealEstate)


class Preference(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE,
                                related_name="preferences")
    preference_name = models.CharField(max_length=30, blank=False, null=False)
    value = models.TextField(max_length=100, blank=True, null=True)
    is_mandatory = models.BooleanField(null=False, default=False)