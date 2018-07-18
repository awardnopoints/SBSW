from django.urls import path
from . import views
from .models import Stopsv2

urlpatterns = [
        path('', views.home, name = 'home'),
        path('dbus/ajax_test/', views.ajax_view, name = 'ajax_view'),
        path('predict_request/', views.predict_request, name='predict_request'),
        path('bus_stops/', views.bus_stops, name='bus_stops')
        
]



