from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("", views.docs, name="docs"),
    path("groups/", views.groups, name="groups"),
    path("groups/<slug:group_slug>/", views.single_group, name="single_group"),
    path("events/", views.events, name="events"),
    path("events/<slug:event_slug>/", views.single_event, name="single_event"),
]
