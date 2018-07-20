from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
from dbus.models import Trip_avg
from dbus.models import BusStopsSequence
from dbus.models import DbusStopsv4
from dbus.forms import Predictions
from sklearn.externals import joblib
import os
import zipfile
import sys
from dbus.bus_realtime import *
import requests
import json

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
  
    routes=BusStopsSequence.objects.values('route_number').distinct()

    stops2 = BusStopsSequence.objects.all()
    inbound=stops2.values_list('stop_id').filter(route_direction="I")
    outbound=stops2.values_list('stop_id').filter(route_direction="O")
    
    stops = Stopsv2.objects.all()
    form = Predictions()
    context = {
        "routes": routes,
        "stops": stops,
        "form": form,
        "stops2":stops2,
        "inbound1": inbound,
        "outbound1": outbound
        }
    bingo = {
            "route_n": stops2,
            "route_distinct": BusStopsSequence.objects.values('route_number').distinct(),
            "stops3":BusStopsSequence.objects.all(),
            "inbound": stops2.values_list('stop_id'),
            "outbound": stops2.values_list('stop_id'),
            "stops":stops
            }
    routes2=BusStopsSequence.objects.values('stop_id', 'route_number', 'route_direction', 'sequence')

    return render(request, 'dbus/index.html', bingo)


def get_times(json_parsed, user_route):
        
    list=json_parsed['results']
    i=0
    length=len(list)
    while i < length:

        each = list[i]
        additional_info=each['additionalinformation']
        arrival_time = each['arrivaldatetime']
        departure_time = each['departuredatetime']
        departing_in = each['departureduetime']
        destination = each['destination']
        destination_local=each['destinationlocalized']
        direction = each['direction']
        arriving_in = each['duetime']
        low_floor=each['lowfloorstatus']
        monitored=each['monitored']
        operator=each['operator']
        origin = each['origin']
        origin_local=each['originlocalized']
        route=each['route']
        scheduled_arrival = each['scheduledarrivaldatetime']
        scheduled_departure = each['scheduleddeparturedatetime']
        timestamp = each['sourcetimestamp']
        i+=1

        times=""
        if (route==user_route):
            times+=departing_in
        return times

def predictions_model(start, end, route, day, hour):

        """
        Takes the route, stop, and time information and returns
        a travel time prediction based on that.
        """
        total = 0
 #       routes=BusStopsSequence.objects.values('route_number').distinct()
        stops = BusStopsSequence.objects.filter(route_number=route) # stop_id, route_number, route_direction, sequence
        start_stop = stops.filter(stop_id=start)
        end_stop = stops.filter(stop_id=end)
        
        # Checks if the inputs are valid, otherwise returns False        
        if len(start_stop) == 0 or len(end_stop) == 0:
                return False
        if len(start_stop) > 1 or len(end_stop) > 1:
                resolved = False
                for s in start_stop:
                        if resolved:
                                break
                        for e in end_stop:
                                print(s, '\n', e)
                                if s.sequence < e.sequence and s.route_direction == e.route_direction:
                                        start_stop, end_stop = s, e
                                        resolved = True
                                        break
                if not resolved:
                        return False
        else:
                start_stop = start_stop.first()
                end_stop = end_stop.first()
                
        if start_stop.route_direction != end_stop.route_direction:
                return False


        argument =str(start_stop.stop_id)        

        # Creates a list of tuples to pass into the model
        input_list = []
        stops = stops.filter(route_direction=start_stop.route_direction
                                ).filter(sequence__gte=start_stop.sequence
                                ).filter(sequence__lt=end_stop.sequence
                                )
        for stop in stops:
                input_list.append((hour, day, stop.stop_id))

        # Passes tuples into the model, sums up the results, and returns them
        t_predictions = t_model.predict(input_list)
        total += t_predictions.sum()
        input_list.append((hour, day, end_stop.stop_id))
        h_predictions = h_model.predict(input_list)
        total += h_predictions.sum()
        
       # returns real time info from api based on user selected stop id - refers to function in bus_realtime file
        stop_id=argument
        url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + stop_id + "&format=json"
        delete_current_rtpi()
        data = call_api(url)
        json_parsed=write_file(data)
        u_route="46A"
        next_bus=get_times(json_parsed, u_route)
        realtime=next_bus
        print (realtime)

                
        if (realtime == "Due"):
            total += 0
        else:
            realtime_int=int(realtime)
            total += realtime_int*60
       
        if total:
            mins=int(total/60)
            secs=int(total%60)
            total=str(mins) + '.' + str(secs)
        
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

def ajax_view(request):
        if request.method=='GET':
                message = request.GET['message']
                return HttpResponse('Message: ' + message)

def predict_request(request):
        if request.method=='GET':
                print("is get")
                g = request.GET
                start_stop, end_stop, route, day, hour = g['start_stop'],g['end_stop'],g['route'],g['day'],g['hour']
                prediction = predictions_model(start_stop, end_stop, route, day, hour)
                print("Predicted wait time is", prediction)
                return HttpResponse(prediction)

def bus_stops(request):
        if request.method=='GET':
            g=request.GET
            routes=BusStopsSequence.objects.values('route_number').distinct()
            route_no=g['route_number']
            stops2 = BusStopsSequence.objects.filter(route_number=route_no)
 
  
            return HttpResponse(stops2)
        
      

def outbound (request):
        if request.method=='GET':
            g=request.GET
            routes=BusStopsSequence.objects.values('route_number').distinct()
            route_no=g['route_number']
            stop=g['start_stop']
            stops2 = BusStopsSequence.objects.filter(route_number=route_no)
            inbound=stops2.values_list('stop_id').filter(route_direction="I")
            outbound=stops2.values_list('stop_id').filter(route_direction="O")
            if stop in inbound:
                    print ("hey")
                    return HttpResponse(inbound)
            else:
                    return HttpResponse(outbound)

     







 
