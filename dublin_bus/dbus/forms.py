from django import forms
from django.forms import ModelForm
from dbus.models import Stopsv2
from django.contrib.auth.forms import UserCreationForm

class Predictions(forms.Form):

        start = forms.CharField()
        end = forms.CharField()
        route = forms.CharField() 

