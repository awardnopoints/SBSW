from django.db import models

class Stops (models.Model):

    stop_id=models.AutoField(max_length=200, primary_key=True)
    stop_name=models.TextField()
    latitude=models.FloatField()
    longitude=models.FloatField()
    stop_id_long=models.CharField(max_length=200)

    def __str__(self):
        return self.stop_name

    def get_lat(self, id):
        return self.latitude[stop_id]

    def get_long(self):
        return self.longitude[stop_id]


class Stopsv2 (models.Model):

    stop_id=models.AutoField(max_length=200, primary_key=True)
    stop_name=models.TextField()
    latitude=models.FloatField()
    longitude=models.FloatField()
    stop_id_long=models.CharField(max_length=200)

    def __str__(self):
        return self.stop_name

    def get_lat(self):
        return self.latitude

    def get_long(self):
        return self.longitude
