from django.contrib import admin
from django.urls import path

from . import views

admin.site.site_header = "Open Cult administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    # /new/
    path("new/", views.new_cult, name="new_cult"),
    # e.g. /@some-username/edit/
    path("@<username>/edit/", views.edit_profile, name="edit_profile"),
    # e.g. /@some-username/
    path("@<username>/", views.profile, name="profile"),
    # e.g. /membership/some-cult-slug/delete/
    path(
        "membership/<slug:cult_slug>/delete/",
        views.delete_membership,
        name="delete_membership",
    ),
    # e.g. /membership/some-cult-slug/
    path("membership/<slug:cult_slug>/", views.membership, name="membership"),
    # e.g. /attendance/some-cult-slug/some-event-slug/delete/
    path(
        "attendance/<slug:cult_slug>/<slug:event_slug>/delete/",
        views.delete_attendance,
        name="delete_attendance",
    ),
    # e.g. /attendance/some-cult-slug/some-event-slug/
    path(
        "attendance/<slug:cult_slug>/<slug:event_slug>/",
        views.attendance,
        name="attendance",
    ),
    path("<slug:cult_slug>/new/", views.new_event, name="new_event"),
    path("<slug:cult_slug>/edit/", views.edit_cult, name="edit_cult"),
    path("<slug:cult_slug>/leader/", views.cult_leader, name="cult_leader"),
    path(
        "<slug:cult_slug>/announcement/",
        views.cult_announcement,
        name="cult_announcement",
    ),
    path(
        "<slug:cult_slug>/<slug:event_slug>/edit/", views.edit_event, name="edit_event"
    ),
    path("<slug:cult_slug>/<slug:event_slug>/comment/", views.comment, name="comment"),
    path("<slug:cult_slug>/<slug:event_slug>/", views.event, name="event"),
    path("<slug:cult_slug>/", views.cult, name="cult"),
]
