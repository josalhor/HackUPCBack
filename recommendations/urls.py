from django.urls import path

from recommendations import views

urlpatterns = [
    path("session/", views.SessionList.as_view()),
    path("session/<uuid:session_id>/", views.SessionDetail.as_view()),
    path("session/<uuid:session_id>/preferences/", views.PreferencesList.as_view())
]
