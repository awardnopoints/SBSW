from django import forms

class Predictions(forms.Form):
	
	start = forms.CharField()
	end = forms.Charfield()
