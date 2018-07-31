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
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import os
import zipfile
import sys
import dbus.bus_realtime as rt
import json
import requests
import datetime
import math


routes_implemented = ['31','130','140','14','15','16','31','39A','46A','1', '102', '104', '11', '111', '114', '116', '118', '120', '13', '142', '145', '150', '151', '15A', '15B', '161', '17', '17A', '18', '184', '185', '220', '236', '238', '239', '25', '25A', '25B', '25D', '25X', '26', '27', '270', '27A', '27B', '27X', '29A', '31A', '31B', '31D', '32', '32X', '33', '33A', '33B', '33X', '37', '38', '38A', '38B', '39', '4', '40', '40B', '40D', '41', '41B', '41C', '41X', '42', '42D', '43', '44', '44B', '45A', '46E', '47', '49', '51D', '51X', '53', '54A', '56A', '59', '61', '63', '65', '65B', '66', '66A', '66B', '66X', '67', '67X', '68', '68A', '68X', '69', '69X', '7', '70', '70D', '75', '757', '76', '76A', '77A', '77X', '79', '79A', '7A', '7B', '7D', '83', '84', '84A', '84X', '9']

routes_implemented = ['46A','31','14','17', '27','11']

routes_to_be_implemented = ('123', '122')

routes_no_longer_in_service = ('83A','16C','41A','14C','38D')

routes_in_service_uncovered = ('7N', '15D', '15N', '25N', '29N', '31N', '33D', '33N', '39X', '39N', '41N', '42N', '46N', '49N', '66N')

routes_unsupported_by_data = ('116','118','236','25D','25X','27X','31D','32X','41X','42D','44B','46E','51D','51X','68A','68X','69X','70D','76A','77X','7D')

#for route in routes_unsupported_by_data:
        #routes_implemented.remove(route)


print('building categories')
stop_cats = sllz.objects.values_list('stop_id', flat=True).distinct()
day_cats = [i for i in range(7)]
weather_cats = ['Clouds','Rain','Drizzle','Fog','Clear','Mist','Smoke','Snow','Thunderstorm']
zone_cats = sllz.objects.values_list('zone', flat=True).distinct()

def price_scrape(route, direction, start_sequence, end_sequence):
        quote_page= 'https://www.dublinbus.ie/Fare-Calculator/Fare-Calculator-Results/?routeNumber=' + str(route).lower() + '&direction=' + str(direction).upper() + '&board=' + str(int(start_sequence)-1) + '&alight=' + str(int(end_sequence)-1)    
        page = urlopen(quote_page)    
        soup = BeautifulSoup(page, 'html.parser')
        try:
                name_box = soup.find("span", id="ctl00_FullRegion_MainRegion_ContentColumns_holder_FareListingControl_lblFare").get_text()    
        except Exception:
                return "Price calculation unresponsive."
        return str(name_box)

def find_models():
        for route in routes_implemented:
                for aspect in ('hangtime','traveltime'):
                        if os.path.exists('dbus/predictive_models/{}_{}_model'.format(route, aspect)):
                                pass
                                #print('Model {}, {} found'.format(route, aspect))
                        else:
                                print('Model {}, {} not found'.format(route, aspect))
                                sys.exit('Error: No model exists for: {}, {}'.format(route, aspect))

def load_models():
        models = {}
        for route in routes_implemented:
                print('loading',route,'models')
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

print('finding models')
find_models()
models = load_models()
#stops, routes = stop_and_routes_info()

stops = sllz.objects.all()
routes = bssd.objects.all()
route_numbers = routes.values_list('route_number', flat=True).distinct()
weather = forecast.objects.all().first()

def home(request):
        context = {
                'route_numbers':route_numbers,
                'stops':stops,
                'routes':routes,
                'weather':weather
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
        print("route",route)
        stops = bssd.objects.filter(route_number=route) # stop_id, route_number, route_direction, sequence
        print(len(stops))
        zones = sllz.objects.all()
        print("start:",start)
        print("end:",end)
        start_stop = stops.filter(stop_id=start)
        end_stop = stops.filter(stop_id=end)

        r = inputValidator(start_stop, end_stop)
        if r:
                start_stop, end_stop = r[0], r[1]
        else:
                
                return False

        # Get Price

        price = price_scrape(route, start_stop.route_direction, start_stop.sequence, end_stop.sequence)

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
        #print(len(weather))
        if len(weather) == 0:
                weather = forecast.objects.all().first()
        else:
                weather = weather.last()
        #print(weather)
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
        prediction = minutes + ':' + seconds
        return prediction, price 

def inputValidator(start_stop, end_stop):
        # Checks if the inputs are valid, otherwise returns False        
        if len(start_stop) == 0 or len(end_stop) == 0:
                #print("start_stop length:",len(start_stop),"end_stop length",len(end_stop))
                return False
        if len(start_stop) > 1 or len(end_stop) > 1:
                resolved = False
                for s in start_stop:
                        if resolved:
                                break
                        for e in end_stop:
                                #print(s, '\n', e)
                                if s.sequence < e.sequence and s.route_direction == e.route_direction:
                                        start_stop, end_stop = s, e
                                        resolved = True
                                        break
                if not resolved:
                        return False
        else:
                start_stop = start_stop.first()
                end_stop = end_stop.first()
                
        #if start_stop.route_direction != end_stop.route_direction:
                #return False
        return(start_stop, end_stop)


def wait_time(route, stop_id):
        
       # returns real time info from api based on user selected stop id - refers to function in bus_realtime file
        url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + stop_id + "&format=json"
        rt.delete_current_rtpi()
        data = rt.call_api(url)
        json_parsed = rt.write_file(data)
        realtime = get_times(json_parsed, route)
        print ('Realtime:',realtime)
                
        if realtime == "Due":
            wait = 'Due Now'
        elif realtime:
            wait = realtime + ':00'
        else:
                wait = "Unknown"
       
        return wait
        

def predict_request(request):
        if request.method=='GET':
                g = request.GET
                start_stop, end_stop, route, year, month, day, hour = g['start_stop'],g['end_stop'],g['route'],g['year'],g['month'],g['day'],g['hour']
                
                if route in routes_to_be_implemented:
                        return HttpResponse('<p>Predictions for route ' + route + ' have yet to be implemented.</p>')
                elif route in routes_in_service_uncovered:
                        return HttpResponse('<p>Unfortunately, our data does not allow to us to make predictions for Route ' + route + '</p>')
                elif route in routes_no_longer_in_service:
                        return HttpResponse('<p>Route ' + route + ' is no longer in service</p>')
                elif route in routes_unsupported_by_data:
                        return HttpResponse('<p>Route ' + route + ' not sufficiently supported by dataset, prediction unavailable</p>')
                elif route not in routes_implemented:
                        return HttpResponse('<p>Route ' + route + ' not recognised</p>')
                prediction, price = predictions_model(start_stop, end_stop, route, int(year), int(month), int(day), int(hour))
                #print("Predicted wait time is", prediction)
                wait = wait_time(route, start_stop)
                return HttpResponse('<p>Wait Time: ' + wait + ', Travel Time: ' + prediction + ', Price: ' + price + '</p>')

def getRoutes(request):
        return HttpResponse(routes)

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



def popStops(request):
        if request.method=='GET':
                g = request.GET
                start_stop, end_stop, route = str(g['start_stop']), str(g['end_stop']), g['route']
                response = getStops(route, start_stop, end_stop)

        #print(response)

        context = {}
        context['stops'] = []
        context['predictions'] = []
        context['error'] = '0'

        context['stops'].append(response)
  
        return JsonResponse(context)


def predict_address(request):

    if request.method=="GET":
        g = request.GET
        year, month, day, hour = g['year'], g['month'], g['day'], g['hour']
        latlng = json.loads(g["context"])[0]
        walk_time = int(latlng["walk_time"])
        prediction = 0
        context = {}
        context["stops"] = []
        context["prediction"] = []
        context["error"] = "0"
	#context from the front end could include more that one bus journey so loop through all bus journeys
	#and added on prediction for each one and relevant stops

        try:
            for key, i in latlng.items():
                if key in "012345689":
                   #print(key)
                   #print(i)
                   lat1, lng1, lat2, lng2 = i[0], i[1], i[2], i[3]
                   query = "select * from dbus_stopsv3 where lat >= (%f*0.99995) and lat <= (%f*1.00015) and abs(longitude) >= abs(%f*0.99995) and abs(longitude) <= abs(%f*1.00015) order by abs(lat-%f) limit 1;"
                                
                   stop1 = DbusStopsv3.objects.raw(query % (float(lat1), float(lat1), float(lng1), float(lng1), float(lat1)))[0].stop_id

                   stop2 = DbusStopsv3.objects.raw(query % (float(lat2), float(lat2), float(lng2), float(lng2), float(lat2)))[0].stop_id

                   url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + str(stop1) + "&format=json"
                   req = requests.get(url)
                   req_text = req.text
                   json_parsed = json.loads(req_text)

                   route_time = math.inf

                   route = bssd.objects.raw("select * from (select * from bus_stops_sequence_distance where stop_id = %s) as a join (select * from bus_stops_sequence_distance where stop_id = %s) as b where a.route_number = b.route_number;" % (str(stop1), str(stop2)))

                   print(route)
        
                   final_route = route[0].route_number

        #above query could return more than one route so use rtpi to decide which one to use (next one due at the first stop)
 
                   for i in route:
                       results = json_parsed["results"]


                       for result in results:

                           if result["route"] == str(i.route_number):  

                               if result["duetime"] == "Due":

                                   route_time = 0
                                   final_route = result["route"]

                               elif int(result["duetime"]) < route_time:
                                   route_time = int(result["duetime"])
                                   final_route = result["route"]     
       
                   prediction = predictions_model(str(stop1), str(stop2), str(final_route), int(year), int(month), int(day), int(hour))
                   print("prediction",prediction)
                   prediction = prediction + walk_time
               
                   stops = getStops(str(final_route), str(stop1), str(stop2))

                   context["stops"].append(stops)
                   context["prediction"].append(prediction)

        except Exception as e:
           context["error"] =  "1"
           print(e)

        #print(context) 

        return JsonResponse(context)


