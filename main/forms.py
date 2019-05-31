from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from main.models import Comment, Cult, CustomUser, Event


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ("username", "email")


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ["name", "doctrine", "city"]


class EditCultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ["name", "slug", "doctrine", "city"]


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


class AddCultLeaderForm(forms.Form):
    username = forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]


class CultAnnouncementForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea)
