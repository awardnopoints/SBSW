from django.db import models

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

class Trip_avg(models.Model):
	
	index_id=models.IntegerField(primary_key=True)
	start_stop=models.TextField()
	end_stop=models.TextField()
	hour=models.FloatField()
	minute=models.FloatField()
	day_of_week=models.FloatField()
	avg_time_taken=models.FloatField()
	avg_hang=models.FloatField()
