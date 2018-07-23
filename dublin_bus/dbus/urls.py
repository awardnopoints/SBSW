from django.urls import path
from . import views
from .models import Stopsv2

urlpatterns = [
        path('', views.home, name = 'home'),
        path('predict_request/', views.predict_request, name='predict_request'),
        #path('bus_stops/', views.bus_stops, name='bus_stops'),
        #path('outbound/', views.outbound, name='outbound'),
        path('popStop/', views.popStop, name = 'popStop')
]



