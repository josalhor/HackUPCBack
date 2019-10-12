from django.urls import path

from recommendations import views

urlpatterns = [
    path("session/", views.SessionList.as_view())
]
