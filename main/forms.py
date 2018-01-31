from django import forms

from .models import Cult


class EmailForm(forms.Form):
    email = forms.EmailField(label='Your email address')


class CultForm(forms.ModelForm):
    class Meta:
        model = Cult
        fields = ['name', 'doctrine', 'city', 'country']
