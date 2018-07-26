from django.urls import path
from . import views
from .models import Stopsv2

urlpatterns = [
        path('', views.home, name = 'home'),
        path('dbus/ajax_test/', views.ajax_view, name = 'ajax_view'),
        path('predict_request/', views.predict_request, name='predict_request'),
        path('popStop/', views.popStop, name = 'popStop'),
        path('predict_address/' , views.predict_address, name='predict_address')

]



