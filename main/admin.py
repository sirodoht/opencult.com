from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from main.forms import CustomUserChangeForm, CustomUserCreationForm
from main.models import Attendance, Comment, Group, CustomUser, Event, Membership


# User
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username"]


admin.site.register(CustomUser, CustomUserAdmin)


# Group
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "city")


admin.site.register(Group, GroupAdmin)


# Event
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "date", "time", "venue")


admin.site.register(Event, EventAdmin)


# Membership
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "date_joined")


admin.site.register(Membership, MembershipAdmin)


# Attendance
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "date_rsvped")


admin.site.register(Attendance, AttendanceAdmin)


# Comment
class CommentAdmin(admin.ModelAdmin):
    list_display = ("date_posted", "body", "author", "event")


admin.site.register(Comment, CommentAdmin)
