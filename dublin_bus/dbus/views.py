from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
from dbus.models import Trip_avg
import json
from django.utils.safestring import SafeString

def home(request):
	
	stop_names = Stopsv2.objects.values('stop_name')
	stop_lat = Stopsv2.objects.values('latitude')
	stop_long = Stopsv2.objects.values('longitude')
	stop_all = Stopsv2.objects.all()	

	json = {}

	for item in stop_all:

		json[item.stop_name] = {'lat' : item.latitude, 'long' : item.longitude}

	#args = {}
	#args.update(csrf(request))
	#response = requests.post('https://137.43.49.47', data=json)
	#args['contents'] = response.json()

	return render(request, 'dbus/index.html', {"contents" : stop_all})



def prediction(start, end, route, hour, day, minute):

	if minute >= 30:
		minute = 45
	else:
		minute = 15	

	fh = open("/home/student/files/routes/%s.txt"  % route)

	start_stop = False

	end_stretch = 0

	for line in fh:

		if line == start:

			start_stop = True
			end_stretch = line

		elif start_stop == True and line != end:
			
			att = Trip_avg.objects.all().filter(hour=hour, minute=minute, day_of_week=day)
			
			
			total += (int(att.avg_time_taken) + int(att.avg_hang))

		elif line == end:

			break

	return total	
