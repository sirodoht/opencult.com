from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from main.models import Comment, Group, CustomUser, Event


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "description", "city"]


class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "slug", "description", "city"]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "details", "date", "time", "venue", "address", "maps_url"]


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
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


class AddGroupLeaderForm(forms.Form):
    username = forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]


class GroupAnnouncementForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
