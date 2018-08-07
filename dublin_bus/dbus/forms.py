from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm

class Predictions(forms.Form):
	
	start = forms.CharField(label = "Start Stop")
	end = forms.CharField(label = "End Stop")

 

