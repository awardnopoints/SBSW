from django.test import TestCase
from dbus.views import predictions_model
import requests
import datetime

class RenderTestCase(TestCase):
    def test_user_visit(self):
        response = self.client.get('http://137.43.49.47/', follow=True)
        self.assertRedirects(response, '/home/')
    
class PredictionsTestCase(TestCase):
    now = datetime.datetime.now()

    def test_basic(self):
        self.assertEqual(1,1)
    
    def test_predition(self):
        result = predictions_model('573', '579', '31', self.now.year, self.now.month, self.now.day, self.now.hour)
        self.assertEqual(result, "fail")