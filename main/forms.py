from django import forms

from .models import Cult, Event


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address')


class CultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ['name', 'doctrine', 'city', 'country']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'details', 'date', 'time', 'venue', 'address', 'maps_url']
