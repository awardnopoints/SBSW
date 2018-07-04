from django import forms

class Predictions(forms.Form):
	
	start = forms.CharField(label = "Start Stop")
	end = forms.Charfield(label = "End Stop")
