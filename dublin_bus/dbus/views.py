from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
import json
from django.utils.safestring import SafeString

def home(request):
	
	stop_names = Stopsv2.objects.values('stop_name')
	stop_lat = Stopsv2.objects.values('latitude')
	stop_long = Stopsv2.objects.values('longitude')
	stop_all = Stopsv2.objects.all()	


	context = {'test' : "test"}

	"""
	json = {}	

	i = 0
	while i < len(stop_names):
		json[stop_names[i]['stop_name']] = {"lat" : stop_lat[i]['latitude'], "long" : stop_long[i]['longitude']}
		i+=1
	
	test = {"hello": 1 , "world" : 2}
"""

	return render(request, "dbus/index.html", context)

class Home(TemplateView):
	template_name = 'index.html'
