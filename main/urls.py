from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = 'Open Cult administration'
app_name = 'main'

urlpatterns = [
    # /
    path('', views.index, name='index'),

    # /login/
    path('login/', views.login, name='login'),

    # /auth/
    path('auth/', views.token_post, name='auth'),

    # /logout/
    path('logout/', views.logout, name='logout'),

    # /about/
    path('about/', views.about, name='about'),

    # /new/
    path('new/', views.new_cult, name='new_cult'),

    # e.g. /some-username/
    path('@<username>/', views.profile, name='profile'),

    # e.g. /some-cult-slug/new/
    path('<slug:cult_slug>/new/', views.new_event, name='new_event'),

    # e.g. /some-cult-slug/edit/
    path('<slug:cult_slug>/edit/', views.edit_cult, name='edit_cult'),

    # e.g. /some-cult-slug/some-event-slug/
    path('<slug:cult_slug>/<slug:event_slug>/', views.event, name='event'),

    # e.g. /some-cult-slug/
    path('<slug:cult_slug>/', views.cult, name='cult'),
]
