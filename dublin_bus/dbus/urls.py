from django.urls import path
from . import views
from .models import Stopsv2

urlpatterns = [
        path('', views.home, name = 'home')
]



