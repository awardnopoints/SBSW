from django import forms
from django.forms import ModelForm
from dbus.models import Stopsv2
from django.contrib.auth.forms import UserCreationForm

class Predictions(forms.Form):

        start = forms.CharField(help_text="Enter your start stop")
        end = forms.CharField(help_text="Enter your destination stop")
 

class BusForm(ModelForm):
        class Meta:
                model=Stopsv2
                fields=['stop_name']
                labels = {'stop_name': ('Start stop'), }
                help_texts = {'stop_name': ('Select your start bus stop'), }
                
form=BusForm()
