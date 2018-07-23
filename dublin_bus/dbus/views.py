from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from dbus.models import DbusStopsv3
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
import dbus.bus_realtime as rt
import json
import requests
import datetime


routes_implemented = ('31')

routes_to_be_implemented = ('1', '102', '104', '11', '111', '114', '116', '118', '120', '122', '123', '13', '130', '14', '140', '142', '145', '15', '150', '151', '15A', '15B', '16', '161', '17', '17A', '18', '184', '185', '220', '236', '238', '239', '25', '25A', '25B', '25D', '25X', '26', '27', '270', '27A', '27B', '27X', '29A', '31A', '31B', '31D', '32', '32X', '33', '33A', '33B', '33X', '37', '38', '38A', '38B', '39', '39A', '4', '40', '40B', '40D', '41', '41B', '41C', '41X', '42', '42D', '43', '44', '44B', '45A', '46A', '46E', '47', '49', '51D', '51X', '53', '54A', '56A', '59', '61', '63', '65', '65B', '66', '66A', '66B', '66X', '67', '67X', '68', '68A', '68X', '69', '69X', '7', '70', '70D', '75', '757', '76', '76A', '77A', '77X', '79', '79A', '7A', '7B', '7D', '83', '84', '84A', '84X', '9')

routes_no_longer_in_service = ('83A','16C','41A','14C','38D')

routes_in_service_uncovered = ('7N', '15D', '15N', '25N', '29N', '31N', '33D', '33N', '39X', '39N', '41N', '42N', '46N', '49N', '66N')

stop_cats = sllz.objects.values_list('stop_id', flat=True).distinct()
day_cats = [i for i in range(7)]
weather_cats = ['Clouds','Rain','Drizzle','Fog','Clear','Mist','Smoke','Snow','Thunderstorm']
zone_cats = sllz.objects.values_list('zone', flat=True).distinct()



def unzip_models():
	for route in routes_implemented:
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

def stop_and_routes_info():
        print('building stops json')
        mystops = {}
        stops = sllz.objects.all()
        for stop in stops:
                mystop = {}
                mystop["lat"] = stop.lat
                mystop["long"] = stop.long
                mystop["stop_name"] = stop.stop_name
                mystop["stop_address"] = stop.stop_address
                mystop["zone"] = stop.zone
                mystops[stop.stop_id] = mystop

        print('building routes json')
        myroutes = {}
        route_numbers = bssd.objects.values_list('route_number',flat=True).distinct()
        for rn in route_numbers:
                myroutes[rn] = {'I':[],'O':[]}
        
        routes = bssd.objects.all()
        for stop in routes:
                mystop = {}
                mystop['stop_id'] = stop.stop_id
                mystop['sequence'] = stop.sequence
                mystop['distance'] = stop.distance
                myroutes[stop.route_number][stop.route_direction].append(mystop)
        

        mystops = json.dumps(mystops)
        myroutes = json.dumps(myroutes)
        
        print('json files complete')

        return(mystops, myroutes)


unzip_models()
models = load_models()
#stops, routes = stop_and_routes_info()

stops = sllz.objects.all()
routes = bssd.objects.all()
route_numbers = routes.values_list('route_number', flat=True).distinct()

def home(request):
        context = {
                'route_numbers':route_numbers,
                'stops':stops,
                'routes':routes
        }
        return render(request, 'dbus/index.html', context)

def get_times(json_parsed, user_route):
        
    results=json_parsed['results']
    i=0
    length=len(results)
    while i < length:

        each = results[i]
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
        minutes = str(int(total/60))
        seconds = int(total%60)
        if seconds < 10:
                seconds = '0' + str(seconds)
        else:
                seconds = str(seconds)
        total = minutes + ':' + seconds
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


def wait_time(route, stop_id):
        
       # returns real time info from api based on user selected stop id - refers to function in bus_realtime file
        url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + stop_id + "&format=json"
        rt.delete_current_rtpi()
        data = rt.call_api(url)
        json_parsed = rt.write_file(data)
        realtime = get_times(json_parsed, route)
        print ('Realtime:',realtime)
                
        if (realtime == "Due"):
            wait = 'Due Now'
        else:
            wait = realtime + ':00'
        
        if realtime == "":
                wait = "Unknown"
       
        return wait
        

def predict_request(request):
        if request.method=='GET':
                print("is get")
                g = request.GET
                start_stop, end_stop, route, year, month, day, hour = g['start_stop'],g['end_stop'],g['route'],g['year'],g['month'],g['day'],g['hour']
                prediction = predictions_model(start_stop, end_stop, route, int(year), int(month), int(day), int(hour))
                print("Predicted wait time is", prediction)
                wait = wait_time(route, start_stop)
                return HttpResponse('<p>Wait Time: ' + wait + '</p><p>Travel Time: ' + prediction + '</p>')

def getRoutes(request):
        return HttpResponse(routes)

def getStops(request):
        return HttpResponse(stops)

def bus_stops(request):
        if request.method=='GET':
            g=request.GET
            routes=BusStopsSequence.objects.values('route_number').distinct()
            route_no=g['route_number']
            stops2 = BusStopsSequence.objects.filter(route_number=route_no).values_list('stop_id', flat=True)
            #list_stops=[]
          
            return HttpResponse(json.dumps(list(stops2)))
        
      

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
 

def popStop(request):
        if request.method=='GET':
                g = request.GET
                start_stop, end_stop, route = str(g['start_stop']), str(g['end_stop']), g['route']
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
  
        
        return JsonResponse(response)
