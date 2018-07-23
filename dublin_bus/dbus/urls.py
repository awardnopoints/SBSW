from django.urls import path
from . import views
from .models import Stopsv2

urlpatterns = [
        path('', views.home, name = 'home'),
        path('predict_request/', views.predict_request, name='predict_request'),
        path('popStop/', views.popStop, name = 'popStop'),
        path('get_routes/', views.getRoutes, name = 'getRoutes'),
        path('get_stops/', views.getStops, name= 'getStops')
]



