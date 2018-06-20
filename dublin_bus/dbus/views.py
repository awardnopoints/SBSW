from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView

def home(request):
	template = loader.get_template('dbus/index.html')
	return HttpResponse(template)

class Home(TemplateView):
	template_name = 'index.html'
