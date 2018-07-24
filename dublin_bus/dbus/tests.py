from django.test import TestCase
from dbus.views import predictions_model

class RenderTestCase(TestCase):
    def user_visit(self):
        response = self.client.get('http://137.43.49.47/', follow=True)
        self.assertRedirects(response, '/home/')

    def user_prediction(self):
        pass
    
class PredictionsTestCase(TestCase):
    pass