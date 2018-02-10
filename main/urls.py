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

    # e.g. /some-username/edit/
    path('@<username>/edit/', views.edit_profile, name='edit_profile'),

    # e.g. /some-username/
    path('@<username>/', views.profile, name='profile'),

    # e.g. /membership/some-cult-slug/delete/
    path('membership/<slug:cult_slug>/delete/', views.delete_membership, name='delete_membership'),

    # e.g. /membership/some-cult-slug/
    path('membership/<slug:cult_slug>/', views.membership, name='membership'),

    # e.g. /attendance/some-cult-slug/some-event-slug/delete/
    path('attendance/<slug:cult_slug>/<slug:event_slug>/delete/', views.delete_attendance, name='delete_attendance'),

    # e.g. /attendance/some-cult-slug/some-event-slug/
    path('attendance/<slug:cult_slug>/<slug:event_slug>/', views.attendance, name='attendance'),

    # e.g. /some-cult-slug/new/
    path('<slug:cult_slug>/new/', views.new_event, name='new_event'),

    # e.g. /some-cult-slug/edit/
    path('<slug:cult_slug>/edit/', views.edit_cult, name='edit_cult'),

    # e.g. /some-cult-slug/leader/
    path('<slug:cult_slug>/leader/', views.cult_leader, name='cult_leader'),

    # e.g. /some-cult-slug/announcement/
    path('<slug:cult_slug>/announcement/', views.cult_announcement, name='cult_announcement'),

    # e.g. /some-cult-slug/some-event-slug/edit/
    path('<slug:cult_slug>/<slug:event_slug>/edit/', views.edit_event, name='edit_event'),

    # e.g. /some-cult-slug/some-event-slug/comment/
    path('<slug:cult_slug>/<slug:event_slug>/comment/', views.comment, name='comment'),

    # e.g. /some-cult-slug/some-event-slug/
    path('<slug:cult_slug>/<slug:event_slug>/', views.event, name='event'),

    # e.g. /some-cult-slug/
    path('<slug:cult_slug>/', views.cult, name='cult'),
]
