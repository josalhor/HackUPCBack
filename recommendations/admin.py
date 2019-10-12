from django.contrib import admin
from .models import RealEstate, RealEstateImage

# Register your models here.
admin.site.register(RealEstate)
admin.site.register(RealEstateImage)