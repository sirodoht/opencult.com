from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from main import models


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = models.CustomUser
        fields = ["username", "email"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = models.CustomUser
        fields = ["username", "email", "about"]


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ["name", "description", "city"]


class GroupChangeForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = ["name", "slug", "description", "city"]


class EventCreationForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = ["title", "details", "date", "time", "venue", "address", "maps_url"]


class EventChangeForm(forms.ModelForm):
    class Meta:
        model = models.Event
        fields = [
            "title",
            "slug",
            "details",
            "date",
            "time",
            "venue",
            "address",
            "maps_url",
        ]


class AddGroupOrganizerForm(forms.Form):
    username = forms.CharField()


class CommentCreationForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ["body"]


class GroupAnnouncementForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
