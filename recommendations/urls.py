from django.urls import path

from recommendations import views

urlpatterns = [
    path("typeform/", views.typeform_webhook_endpoint),
    path("session/", views.SessionList.as_view()),
    path("session/<str:session_id>/", views.SessionDetail.as_view()),
    path("session/<str:session_id>/preferences/", views.PreferencesList.as_view())
]
