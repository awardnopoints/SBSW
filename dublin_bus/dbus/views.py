from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
#from django.db.models import Q
from dbus.models import Stopsv2
from dbus.models import Trip_avg
from dbus.models import BusStopsSequence
from dbus.forms import Predictions
from sklearn.externals import joblib
import os
import zipfile
import sys

def unzip_files(route):
        for aspect in ('hangtime','traveltime'):
                if os.path.exists('dbus/predictive_models/{}_{}_rfr.sav'.format(route, aspect)):
                        print('Model {}, {} found'.format(route, aspect))
                else:
                        print('Model {}, {} not found'.format(route, aspect))
                        if os.path.exists('dbus/predictive_models/{}_{}_rfr.zip'.format(route, aspect)) :
                                print('Zip found, unzipping.')
                                zip_ref = zipfile.ZipFile('dbus/predictive_models/{}_{}_rfr.zip'.format(route, aspect))
                                zip_ref.extractall('dbus/predictive_models')
                                zip_ref.close()
                                print('Unzipped')
                        else:
                                sys.exit('Error: No model exists for: {}, {}'.format(route, aspect))

def load_models(route):
        h_model = joblib.load('dbus/predictive_models/{}_hangtime_rfr.sav'.format(route))
        t_model = joblib.load('dbus/predictive_models/{}_traveltime_rfr.sav'.format(route))
        return (h_model, t_model)

unzip_files('46A')
h_model, t_model = load_models('46A')

def home(request):

        if request.method == "POST":

                form = Predictions(request.POST)
                if form.is_valid():
                        stops = Stopsv2.objects.all()
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        form = Predictions()
                        day = 0
                        hour = 10.0
                        minute = 15
                        route = "46A"

                        #result = predictions(start, end, route, hour, day, minute) #etc )
                        result = predictions_model(start, end, route, day, hour)

                        context = {
                                "stops": stops,
                                "result": result,
                                "form": form
                                }

                return render(request, 'dbus/result.html', context)

        else:

                stops = Stopsv2.objects.all()
                form = Predictions()
                context = {
                        "stops": stops,
                        "form": form
                        }


                return render(request, 'dbus/index.html', context)


def predictions_model(start, end, route, day, hour):
        total = 0
        # stop_id, route_number, route_direction, sequence
        stops = BusStopsSequence.objects.filter(route_number=route)
        start_stop = stops.filter(stop_id=start)
        end_stop = stops.filter(stop_id=end)
        #print(len(start_stop),len(end_stop))

        if len(start_stop) == 0 or len(end_stop) == 0:
                return False
        if len(start_stop) > 1 or len(end_stop) > 1:
                resolved = False
                for s in start_stop:
                        if resolved:
                                break
                        for e in end_stop:
                                if s.sequence < e.sequence and s.route_direction == e.route_direction:
                                        start_stop, end_stop = s, e
                                        resolved = True
                                        break
                if not resolved:
                        return False
        
        input_list = []
        start_stop = start_stop.first()
        end_stop = end_stop.first()
        #print('Start stop sequence is', start_stop.sequence)
        #print('End stop sequence is', end_stop.sequence)
        #print('Number of stops before query:', len(stops))
        stops = stops.filter(route_direction=start_stop.route_direction
                                ).filter(sequence__gte=start_stop.sequence
                                ).filter(sequence__lt=end_stop.sequence
                                )
        #print('Number of stops after query:',len(stops))
        #print('Iteration begins')
        for stop in stops:
                #print(stop.stop_id)
                input_list.append((hour, day, stop.stop_id))
        #print(input_list)
        t_predictions = t_model.predict(input_list)
        print('traveltimes:', t_predictions)
        total += t_predictions.sum()
        input_list.append((hour, day, end_stop.stop_id))
        h_predictions = h_model.predict(input_list)
        total += h_predictions.sum()
        print(total)
        return total
        
        

def predictions(start, end, route, hour, day, minute):
	
        total = 0


        if minute >= 30:
                minute = 45
        else:
                minute = 15

        fh = open("/home/student/analytics/routes/%s.txt"  % route)

        start_stop = False

        start_stretch = 0

        for line in fh:
		
                line = str(int(line))

                if int(line) == int(start):

                        start_stop = True
                        start_stretch = line

                elif start_stop == True and int(line) != int(end):
                      
                        
                        att = Trip_avg.objects.all().filter(hour=hour, minute=minute, day_of_week=day, end_stop=str(line), start_stop = start_stretch)

                        print(att)

                        total += (int(att[0].avg_time_taken) + int(att[0].avg_hang))

                        start_stretch = line



                elif start_stop == True and int(line) == int(end):
			
                        att = Trip_avg.objects.all().filter(hour=hour, minute=minute, day_of_week=day, end_stop=end, start_stop=start_stretch)
                        total += (int(att[0].avg_time_taken) + int(att[0].avg_hang))
                        break

        return total

