from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

admin.site.site_header = "Open Cult administration"
app_name = "main"

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("main:password_change_done")
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(success_url=reverse_lazy("main:password_reset_done")), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy("main:password_reset_complete")),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("signup/", views.SignUp.as_view(), name="signup"),
    path("about/", views.about, name="about"),
    path("new/", views.new_group, name="new_group"),
    path("@<username>/edit/", views.edit_profile, name="edit_profile"),
    path("@<username>/", views.profile, name="profile"),
    path(
        "membership/<slug:group_slug>/delete/",
        views.delete_membership,
        name="delete_membership",
    ),
    path("membership/<slug:group_slug>/", views.membership, name="membership"),
    path(
        "attendance/<slug:group_slug>/<slug:event_slug>/delete/",
        views.delete_attendance,
        name="delete_attendance",
    ),
    path(
        "attendance/<slug:group_slug>/<slug:event_slug>/",
        views.attendance,
        name="attendance",
    ),
    path("<slug:group_slug>/new/", views.new_event, name="new_event"),
    path("<slug:group_slug>/edit/", views.edit_group, name="edit_group"),
    path("<slug:group_slug>/leader/", views.group_leader, name="group_leader"),
    path(
        "<slug:group_slug>/announcement/",
        views.group_announcement,
        name="group_announcement",
    ),
    path(
        "<slug:group_slug>/<slug:event_slug>/edit/", views.edit_event, name="edit_event"
    ),
    path("<slug:group_slug>/<slug:event_slug>/comment/", views.comment, name="comment"),
    path("<slug:group_slug>/<slug:event_slug>/", views.event, name="event"),
    path("<slug:group_slug>/", views.group, name="group"),
]
