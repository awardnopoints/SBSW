from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.db import connection
from dbus.models import DbusStopsv3
from dbus.models import DbusStopsv4
from dbus.models import Trip_avg
from dbus.models import BusStopsSequenceDistance as bssd
from dbus.models import StopsLatlngZone as sllz
from dbus.models import forecast
from dbus.forms import Predictions
from sklearn.externals import joblib
import pandas as pd
import os
import zipfile
import sys
import json
import requests
import datetime


routes = ('46A','31')
stop_cats = sllz.objects.values_list('stop_id', flat=True).distinct()
day_cats = [i for i in range(7)]
weather_cats = ['Clouds','Rain','Drizzle','Fog','Clear','Mist','Smoke','Snow','Thunderstorm']
zone_cats = sllz.objects.values_list('zone', flat=True).distinct()



def unzip_models():
	for route in routes:
        	for aspect in ('hangtime','traveltime'):
                	if os.path.exists('dbus/predictive_models/{}_{}_model'.format(route, aspect)):
                        	print('Model {}, {} found'.format(route, aspect))
                	else:
                        	print('Model {}, {} not found'.format(route, aspect))
                        	if os.path.exists('dbus/predictive_models/{}_{}_model.zip'.format(route, aspect)) :
                                	print('Zip found, unzipping.')
                                	zip_ref = zipfile.ZipFile('dbus/predictive_models/{}_{}_rfr.zip'.format(route, aspect))
                                	zip_ref.extractall('dbus/predictive_models')
                                	zip_ref.close()
                                	print('Unzipped')
                        	else:
                                	sys.exit('Error: No model exists for: {}, {}'.format(route, aspect))

def load_models():
        models = {}
        for route in routes:
        	models[route + '_h'] = joblib.load('dbus/predictive_models/{}_hangtime_model'.format(route))
        	models[route + '_t'] = joblib.load('dbus/predictive_models/{}_traveltime_model'.format(route))
        return models

unzip_models()
models = load_models()


def home(request):

        if request.method == "POST":         
                
                form = Predictions(request.POST)
                if form.is_valid():
                        stops = DbusStopsv3.objects.all()
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        form = Predictions()
                        day = 0
                        hour = 10.0
                        minute = 15
                        route = "46A"

                        #result = predictions(start, end, route, hour, day, minute) #etc )
                        result = predictions_model(start, end, route, day, hour)
                        if result:
                                mins = int(result/60)
                                secs = int(result%60)
                                result = str(mins) + ':' + str(secs)

                        context = {
                                "stops": stops,
                                "result": result,
                                "form": form
                                }

                return render(request, 'dbus/result.html', context)

        else:

                stops = DbusStopsv3.objects.all()
                form = Predictions()
                context = {
                        "stops": stops,
                        "form": form
                        }


                return render(request, 'dbus/index.html', context)


def predictions_model(start, end, route, year, month, day, hour):

        """
        Takes the route, stop, and time information and returns
        a travel time prediction based on that.
        """
        total = 0
        stops = bssd.objects.filter(route_number=route) # stop_id, route_number, route_direction, sequence
        zones = sllz.objects.all()
        start_stop = stops.filter(stop_id=start)
        end_stop = stops.filter(stop_id=end)

        r = inputValidator(start_stop, end_stop)
        if r:
                start_stop, end_stop = r[0], r[1]
        else:
                return False

        # Creates a list of tuples to pass into the model
        input_list = []
        stops = stops.filter(route_direction=start_stop.route_direction,
                                sequence__gte=start_stop.sequence,
                                sequence__lt=end_stop.sequence
                                )
        for stop in stops:
                input_list.append((stop.stop_id, stop.distance, zones.get(pk=stop.stop_id).zone))
        date = datetime.datetime(year, month, day, hour)
        weather = forecast.objects.filter(datetime__date=datetime.date(year, month, day),
                                        datetime__hour__lte=hour+1.5
                                        )
        print(len(weather))
        if len(weather) == 0:
                weather = forecast.objects.all().first()
        else:
                weather = weather.last()
        print(weather)
        df = pd.DataFrame(input_list, columns=['stop_id','distance','zone'])
        df['day'] = date.weekday()
        df['weather_main'] = weather.mainDescription
        df['temp'] = weather.temp
        df['wind_speed'] = weather.wind_speed

        hours_tuple = ((hour < 7),(7 <= hour < 9),(9 <= hour <= 11),
                        (11 <= hour < 15), (15 <= hour < 18), (18 <= hour))
        df['before_7am'], df['7am_9am'], df['9am_11am'],df['11am_3pm'], df['3pm_6pm'], df['6pm_midnight'] = hours_tuple
        
        df['stop_id'] = df['stop_id'].astype('category', categories=stop_cats)
        df['day'] = df['day'].astype('category', categories=day_cats)
        df['weather_main'] = df['weather_main'].astype('category', categories=weather_cats)
        df['zone'] = df['zone'].astype('category', categories=zone_cats)

        df = df[['stop_id','day','before_7am','7am_9am','9am_11am', '11am_3pm', '3pm_6pm', '6pm_midnight','temp','wind_speed','weather_main','zone','distance']]
        df = pd.get_dummies(df, columns=['stop_id','day','weather_main','zone'])
        # Passes tuples into the model, sums up the results, and returns them
        t_predictions = models[route+'_t'].predict(df)
        total += t_predictions.sum()
        del df['distance']
        h_predictions = models[route+'_h'].predict(df)
        total += h_predictions.sum()
        return total

def inputValidator(start_stop, end_stop):
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
        return(start_stop, end_stop)        
        

"""
def predictions(start, end, route, hour, day, minute):


#A function to return basic average predictions

	
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

"""

def ajax_view(request):
    if request.method=='GET':
        message = request.GET['message']
        return HttpResponse('Message: ' + message)

def predict_request(request):
    if request.method=='GET':
        print("is get")
        g = request.GET
        start_stop, end_stop, route, year, month, day, hour = g['start_stop'],g['end_stop'],g['route'],g['year'],g['month'],g['day'],g['hour']
        prediction = predictions_model(start_stop, end_stop, route, int(year), int(month), int(day), int(hour))
        print("Predicted wait time is", prediction)
        return HttpResponse(prediction)

def getStops(route, start_stop, end_stop):

    stops = bssd.objects.all().filter(route_number = route)
    first = False
    last = False
    response = {}
    i = 0
    for stop in stops:

        stop = str(stop.stop_id)


        if not first and stop == start_stop:
            url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + str(stop) + "&format=json"
            req = requests.get(url)
            req_text = req.text
            json_parsed = json.loads(req_text)
            first = True
            latlong = DbusStopsv3.objects.all().filter(stop_id = stop)

            lat = latlong[0].lat
            lon = latlong[0].longitude
            response[i] = {'stop': stop,'lat' : lat, 'lon' : lon, "rtpi" : json_parsed}
            i += 1

        elif first and not last and stop != end_stop:

            latlong = DbusStopsv3.objects.all().filter(stop_id = stop)

            lat = latlong[0].lat
            lon = latlong[0].longitude
            response[i] = {'stop': stop,'lat' : lat, 'lon' : lon}
            i += 1


        elif first and not last and stop == end_stop:

             last = True
             latlong = DbusStopsv3.objects.all().filter(stop_id = stop)
             lat = latlong[0].lat
             lon = latlong[0].longitude
             response[i] = {'stop': stop, 'lat' : lat, 'lon' : lon}
             break

    return response



def popStop(request):
    if request.method=='GET':
        g = request.GET
        start_stop, end_stop, route = str(g['start_stop']), str(g['end_stop']), g['route']
        response = getStops(route, start_stop, end_stop)


    return JsonResponse(response)


def predict_address(request):

    if request.method=="GET":
        g = request.GET
        lat1, lng1, lat2, lng2, walk_time, year, month, day, hour = g['lat1'], g['lng1'], g['lat2'], g['lng2'], g['walk_time'], g['year'], g['month'], g['day'], g['hour']

        query = "select * from dbus_stopsv3 where lat >= (%f*0.9999) and lat <= (%f*1.0001) and abs(longitude) >= abs(%f*0.9999) and abs(longitude) <= abs(%f*1.0001) order by abs(lat-%f) limit 1;"

        stop1 = DbusStopsv3.objects.raw(query % (float(lat1), float(lat1), float(lng1), float(lng1), float(lat1)))[0].stop_id

        stop2 = DbusStopsv3.objects.raw("select * from dbus_stopsv3 where lat >= (%f*0.9999) and lat <= (%f*1.0001) and abs(longitude) >= abs(%f*0.9999) and abs(longitude) <= abs(%f*1.0001) order by abs(lat-%f) limit 1;" % (float(lat2), float(lat2), float(lng2), float(lng2), float(lat2)))[0].stop_id

        route = (bssd.objects.all().filter(stop_id = stop1) & bssd.objects.all().filter(stop_id = stop1))[0].route_number

        prediction = predictions_model(stop1, stop2, route, int(year), int(month), int(day), int(hour))

        stops = getStops(route, stop1, stop2)

        context = {}

        context["stops"] = stops
        context["prediciton"] = prediction + walk_time

        return JsonResponse(context)

def get_stop_no (request):
    if request.method=="GET":
        g=request.GET
        lat=g['lat']
        stops=[]
        stops=DbusStopsv4.objects.values_list('stop_id', flat=True).filter(lat=lat)
        return HttpResponse(stops)
        

