from django.contrib import admin
from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    # /api/
    path('', views.docs, name='docs'),

    # /api/cults/
    path('cults/', views.cults, name='cults'),

    # eg. /api/cults/some-cult-name/
    path('cults/<slug:cult_slug>/', views.single_cult, name='single_cult'),

    # /api/events/
    path('events/', views.events, name='events'),

    # eg. /api/events/some-event-name/
    path('events/<slug:event_slug>/', views.single_event, name='single_event'),
]
