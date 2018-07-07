from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
from dbus.models import Trip_avg
from dbus.forms import Predictions
import datetime

def home(request):

        if request.method == "POST":

                form = Predictions(request.POST)
                if form.is_valid():
                        stops = Stopsv2.objects.all()
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        dt = datetime.datetime.now()
                        day = 0
                        hour = dt.hour
                        minute = dt.minute
                        route = form.cleaned_data['route']
                        form = Predictions()

                        result = predictions(start, end, route, hour, day, minute) #etc )

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

