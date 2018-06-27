from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
import json
from django.utils.safestring import SafeString

def home(request):
	
	#stop_names = Stopsv2.objects.values('stop_name')
	#stop_lat = Stopsv2.objects.values('latitude')
	#stop_long = Stopsv2.objects.values('longitude')
	stop_all = Stopsv2.objects.all()	

	#json = {}

	#for item in stop_all:

		#json[item.stop_name] = {'lat' : item.latitude, 'long' : item.longitude}

	#args = {}
	#args.update(csrf(request))
	#response = requests.post('https://137.43.49.47', data=json)
	#args['contents'] = response.json()

	return render(request, 'dbus/index.html', {"contents" : stop_all})
