from django.test import TestCase
from dbus.views import predictions_model, inputValidator, format_prediction, price_scrape, get_times, get_rtpi, wait_predict, getStops, getClose
from dbus.models import StopsLatlngZone as sllz
from dbus.models import BusStopsSequenceDistance as bssd
import datetime
import json
import django.db.models

from django.test import Client
import unittest

class LoadTestCase(TestCase):

    def testLoadStatus(self):
        response = Client().post('')
        self.assertEqual(response.status_code, 200)

class GetTestCase(TestCase):
    predict_response = Client().get('/predict_request/', {'start_stop':1499, 'end_stop':4516, 'route':'123', 'year':2018,'month':5,'day':2,'hour':10,'minute':12,'now':'true',})
    pop_response = Client().get('/popStops/', {'start_stop':1499, 'end_stop':4516, 'route':'123'})

    def testPredictStatus(self):
        self.assertEqual(self.predict_response.status_code, 200)

    def testPredictContent(self):
        content = self.predict_response.content.decode('utf-8')
        myjson = json.loads(content)
        assert myjson['price']
        assert myjson['wait']
        assert myjson['prediction']

    def testPopStopsStatus(self):
        self.assertEqual(self.pop_response.status_code, 200)
    
    def testPopStopsContent(self):
        content = self.pop_response.content.decode('utf-8')
        myjson = json.loads(content)
        assert myjson['stops'][0]['0']['stop']
        self.assertEqual(myjson['error'], '0')
        self.assertEqual(myjson['predictions'], [])

    

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
        self.assertEqual('O', results[0].route_direction, msg='End to start of circular route')


class PredictionsTestCase(TestCase):

    def getStop(self, r, s):
        return bssd.objects.filter(route_number = r, stop_id = s)
    
    now = datetime.datetime.now()

    def testPredictionTrue(self):
        start = self.getStop('15', 1151)
        end = self.getStop('15', 1158)
        start_stop, end_stop = inputValidator(start, end)

        result = predictions_model(start_stop, end_stop, start_stop.route_number, 2018, 10, 5, 10)
        self.assertIsInstance(result, float)

class FormatPredictionTestCase(TestCase):

    def testFormat(self):
        prediction = format_prediction(450)
        self.assertEqual(prediction, '7:30')
        prediction = format_prediction(425)
        self.assertEqual(prediction, '7:05')

class PriceTestCase(TestCase):

    def testPrice(self):
        price = price_scrape('15','I',10,15)
        self.assertEqual(price, '€2.10')

class GetTimesTestCase(TestCase):

    def testGetTimes(self):
        json_parsed = {'results':[{'departureduetime':10, 'route':'123'}, {'departureduetime':4, 'route':'15'}, {'departureduetime':5, 'route':'31'}]}
        self.assertEqual(get_times(json_parsed, '123'), 10)
        self.assertEqual(get_times(json_parsed, '15'), 4)
        self.assertEqual(get_times(json_parsed, '31'), 5)

class GetRtpiTestCase(TestCase):

    def testGetRTIP(self):
        self.assertIsInstance(get_rtpi('15', 1151), str)

class WaitPredictTestCase(TestCase):
    
    def getStop(self, r, s):
        return bssd.objects.filter(route_number = r, stop_id = s)

    def testWaitPredict(self):
        stop = self.getStop('15', 1151).first()
        self.assertIsInstance(wait_predict('15',stop,2018,10,5,10,10), str)

class GetStopsTestCase(TestCase):

    def testGetStops(self):
        self.assertEqual(set(getStops('15', '1151', '1158', '1')[0]),set(['lat', 'lon', 'rtpi', 'stop']))

class GetCloseTestCase(TestCase):

    def testLeap(self):
        self.assertIsInstance(getClose(16, 15, 'leap_stores', 0.01), django.db.models.query.RawQuerySet)

    def testStops(self):
        self.assertIsInstance(getClose(16, 15, 'dbus_stopsv3', 0.01), django.db.models.query.RawQuerySet)
    
    def testFalse(self):
        self.assertFalse(getClose(16, 15, 'Wrong', 0.01))