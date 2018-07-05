from django.shortcuts import render
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.generic import TemplateView
from dbus.models import Stopsv2
from dbus.models import Trip_avg
from dbus.forms import Predictions
from dbus.forms import BusForm

def home(request):

        if request.method == "POST":

                form = Predictions(request.POST)
                if form.is_valid():
                        stops = Stopsv2.objects.all()
                        start = form.cleaned_data['start']
                        end = form.cleaned_data['end']
                        form = Predictions()

                        #result = predictions(start, end) #etc )

                        context = {
                                "stops": stops,
                                #"result" = result
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

