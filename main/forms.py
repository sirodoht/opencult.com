from django import forms
from django.contrib.auth.models import User

from .models import Cult, Event


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address')


class CultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ['name', 'doctrine', 'city']


class EditCultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ['name', 'slug', 'doctrine', 'city']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'details', 'date', 'time', 'venue', 'address', 'maps_url']


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'slug', 'details', 'date', 'time', 'venue', 'address', 'maps_url']


class UserForm(forms.ModelForm):
    about = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ['username']
