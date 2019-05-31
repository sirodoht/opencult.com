from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from main.forms import CustomUserChangeForm, CustomUserCreationForm
from main.models import Attendance, Comment, Group, CustomUser, Event, Membership


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username", "about"]


admin.site.register(CustomUser, CustomUserAdmin)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "city")


admin.site.register(Group, GroupAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "group", "date", "time", "venue")


admin.site.register(Event, EventAdmin)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "role", "date_joined")


admin.site.register(Membership, MembershipAdmin)


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "date_rsvped")


admin.site.register(Attendance, AttendanceAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("date_posted", "body", "author", "event")


admin.site.register(Comment, CommentAdmin)
