from django.test import TestCase
from dbus.views import predictions_model, inputValidator
from dbus.models import StopsLatlngZone as sllz
from dbus.models import BusStopsSequenceDistance as bssd
# # import requests
import datetime

# #from django.test import Client
import unittest
# import http.client as c
# import urllib.request
# import urllib.parse

# class RenderTestCase(TestCase):
#      def test_user_visit(self):
#         response = self.client.get('http://137.43.49.47/', follow=True)
#         self.assertRedirects(response, '/home/')

class InputValidatorTestCase(TestCase):
    
    def getStop(self, r, s):
        return bssd.objects.filter(route_number = r, stop_id = s)
    
    def testTrueSimple(self):
        start = self.getStop('15', 1151)
        end = self.getStop('15', 1158)
        results = inputValidator(start, end)

        self.assertEqual(results[0].route_direction, 'I', msg='basic in correct order')
        self.assertEqual(results[1].route_direction, 'I', msg='basic in correct order')

        start = self.getStop('15', 7581)
        end = self.getStop('15', 1020)
        results = inputValidator(start, end)

        self.assertEqual(results[0].route_direction, 'O', msg='basic in correct order')
        self.assertEqual(results[1].route_direction, 'O', msg='basic in correct order')

    def testFalseSimple(self):
        start = self.getStop('15', 1158)
        end = self.getStop('15', 1151)
        results = inputValidator(start, end)

        self.assertFalse(results, msg='Right stops wrong order')

        start = self.getStop('15', 100)
        end = self.getStop('15', 200)
        results = inputValidator(start, end)

        self.assertFalse(results, msg='Wrong stops')

        start = self.getStop('14', 1151)
        end = self.getStop('14', 1158)
        results = inputValidator(start, end)

        self.assertFalse(results, msg='Wrong route')

        start = self.getStop('14', 7581)
        end = self.getStop('15', 1158)
        results = inputValidator(start, end)

        self.assertFalse(results, msg='Different routes')


    def testEdgeCaseCircular(self):
        start = self.getStop('46A', 2039)
        end = self.getStop('46A', 807)
        results = inputValidator(start, end)

        self.assertEqual('I', results[0].route_direction, msg='Start to End of circular route')

        results = inputValidator(end, start)
        self.assertEqual('0', results[0].route_direction, msg='End to start of circular route')


class PredictionsTestCase(TestCase):

    now = datetime.datetime.now()

    def test_basic(self):
        self.assertEqual(1,1)

    def test_input(self):
        pass
        
    
    # def test_prediction(self):
    #     result = predictions_model('573', '579', '31', self.now.year, self.now.month, self.now.day, self.now.hour)
    #     self.assertEqual(result, "fail")

# class TestBasic(unittest.TestCase):

#     def test1(self):
#         x = 5
#         self.assertEqual(5, x)

# class TestResponse(unittest.TestCase):

#     url = 'https://csi420-01-vm1.ucd.ie/'
#     status = urllib.request.urlopen(url).getcode()
#     now = datetime.datetime.now()
#     print(now)

#     def testClient(self):
#         self.assertEqual(200, self.status)

#     def testQuery(self):
#         data = {'route': '46A', 
#         'start_stop': "2041", 
#             'end_stop': "2045", 
#             'year': str(self.now.year()), 'month': str(self.now.month()), 'day': str(self.now.weekday()), 
#             'hour': str(self.now.hour()), 'minute': str(self.now.minute()), 'now': "true"}
#         url_values = urllib.parse.urlencode(data) 
#         #print(url_values)
#         url = self.url + '?' + url_values
#         print(url)
#         data = urllib.request.urlopen(url)
#         #print(data.info())



    


# if __name__ == '__main__':
#     unittest.main()
