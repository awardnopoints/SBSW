from django.db import models

#class Stops (models.Model):

#    stop_id=models.AutoField(max_length=200, primary_key=True)
#    stop_name=models.TextField()
#    latitude=models.FloatField()
#    longitude=models.FloatField()
#    stop_id_long=models.CharField(max_length=200)

#    def __str__(self):
#        return self.stop_name
#
#    def get_lat(self, id):
#        return self.latitude[stop_id]

#    def get_long(self):
#        return self.longitude[stop_id]


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


class current_weather (models.Model):
 
    datetime=models.DateTimeField(primary_key=True)
    dt=models.FloatField()
    temp=models.FloatField()
    min_temp=models.FloatField()
    max_temp=models.FloatField()    
    description=models.TextField()
    mainDescription=models.TextField()
    wind_speed=models.FloatField()
    wind_direction=models.FloatField()    
    humidity=models.FloatField()
    pressure=models.FloatField()
    cloudiness=models.FloatField()


class forecast (models.Model):

    datetime=models.DateTimeField(primary_key=True)
    temp=models.FloatField()
    min_temp=models.FloatField()
    max_temp=models.FloatField()           
    description=models.TextField()
    mainDescription=models.TextField()
    wind_speed=models.FloatField()
    wind_direction=models.FloatField()    
    humidity=models.FloatField()
#    pressure=models.FloatField()
#    cloudiness=models.FloatField()





class AvStretch(models.Model):
    start_stop = models.CharField(primary_key=True, max_length=20)
    end_stop = models.CharField(max_length=20)
    av_arr = models.CharField(max_length=20, blank=True, null=True)
    av_dep = models.CharField(max_length=20, blank=True, null=True)
    av_hang = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'av_stretch'
        unique_together = (('start_stop', 'end_stop'),)


class BusStopsSequence(models.Model):
    stop_id = models.BigIntegerField(blank=True, null=True)
    route_number = models.TextField(blank=True, null=True)
    route_direction = models.TextField(blank=True, null=True)
    sequence = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        unique_together = ('stop_id','route_number','route_direction')
        db_table = 'bus_stops_sequence'

    def __str__(self):
        return str(self.stop_id) + ", " + str(self.route_number) + ", " + str(self.route_direction)


class DbusCurrentWeather(models.Model):
    datetime = models.DateTimeField(primary_key=True)
    temp = models.FloatField()
    min_temp = models.FloatField()
    max_temp = models.FloatField()
    rain = models.FloatField()
    description = models.TextField()
    maindescription = models.TextField(db_column='mainDescription')  # Field name made lowercase.
    wind_speed = models.FloatField()
    wind_direction = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    cloudiness = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dbus_current_weather'


class DbusForecast(models.Model):
    datetime = models.DateTimeField(primary_key=True)
    temp = models.FloatField()
    min_temp = models.FloatField()
    max_temp = models.FloatField()
    description = models.TextField()
    maindescription = models.TextField(db_column='mainDescription')  # Field name made lowercase.
    wind_speed = models.FloatField()
    wind_direction = models.FloatField()
    humidity = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dbus_forecast'


class DbusStopNames(models.Model):
    stop_number = models.IntegerField(blank=True, null=True)
    stop_address = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dbus_stop_names'


class DbusStopsv2(models.Model):
    stop_id = models.AutoField(primary_key=True)
    stop_name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    stop_id_long = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'dbus_stopsv2'


class DbusStopsv3(models.Model):
    stop_id = models.AutoField(primary_key=True)
    lat = models.CharField(max_length=400, blank=True, null=True)
    stop_name = models.CharField(max_length=400, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dbus_stopsv3'


class DbusStopsv4(models.Model):
    stop_id = models.IntegerField()
    lat = models.CharField(max_length=400, blank=True, null=True)
    stop_name = models.CharField(max_length=400, blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    stop_address = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dbus_stopsv4'


class DbusTripAvg(models.Model):
    index_id = models.TextField()
    start_stop = models.TextField()
    end_stop = models.TextField()
    hour = models.FloatField()
    minute = models.FloatField()
    day_of_week = models.FloatField()
    avg_time_taken = models.FloatField()
    avg_hang = models.FloatField()

    class Meta:
        managed = False
        db_table = 'dbus_trip_avg'


class Dweather(models.Model):
    city_id = models.CharField(max_length=40, blank=True, null=True)
    clouds_all = models.CharField(max_length=3, blank=True, null=True)
    dt = models.CharField(primary_key=True, max_length=40)
    dt_iso = models.CharField(max_length=40, blank=True, null=True)
    main_humidity = models.CharField(max_length=40, blank=True, null=True)
    main_pressure = models.CharField(max_length=40, blank=True, null=True)
    main_temp = models.CharField(max_length=40, blank=True, null=True)
    main_temp_max = models.CharField(max_length=10, blank=True, null=True)
    main_temp_min = models.CharField(max_length=10, blank=True, null=True)
    rain_1h = models.CharField(max_length=1, blank=True, null=True)
    rain_24h = models.CharField(max_length=1, blank=True, null=True)
    rain_3h = models.CharField(max_length=1, blank=True, null=True)
    wind_deg = models.CharField(max_length=10, blank=True, null=True)
    wind_speed = models.CharField(max_length=10, blank=True, null=True)
    weather_description = models.CharField(max_length=10, blank=True, null=True)
    weather_icon = models.CharField(max_length=10, blank=True, null=True)
    weather_id = models.CharField(max_length=10, blank=True, null=True)
    weather_main = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dweather'


class RealtimeBus(models.Model):
    arrival_time = models.CharField(primary_key=True, max_length=100)
    departure_time = models.CharField(max_length=300, blank=True, null=True)
    departing_in = models.CharField(max_length=30, blank=True, null=True)
    destination = models.CharField(max_length=300, blank=True, null=True)
    direction = models.CharField(max_length=100, blank=True, null=True)
    arriving_in = models.CharField(max_length=30, blank=True, null=True)
    origin = models.CharField(max_length=100, blank=True, null=True)
    route = models.CharField(max_length=40)
    scheduled_arrival = models.CharField(max_length=300, blank=True, null=True)
    scheduled_departure = models.CharField(max_length=300, blank=True, null=True)
    timestamp = models.CharField(max_length=300)

    class Meta:
        managed = False
        db_table = 'realtime_bus'
        unique_together = (('arrival_time', 'route', 'timestamp'),)


class TripFileTable(models.Model):
    index_id = models.CharField(max_length=20, blank=True, null=True)
    date = models.CharField(max_length=20, blank=True, null=True)
    tripid = models.CharField(max_length=20, blank=True, null=True)
    lineid = models.CharField(max_length=20, blank=True, null=True)
    routeid = models.CharField(max_length=20, blank=True, null=True)
    act_arr = models.CharField(max_length=20, blank=True, null=True)
    act_dep = models.CharField(max_length=20, blank=True, null=True)
    lastupdate = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trip_file_table'


class TripRaw(models.Model):
    index_id = models.CharField(primary_key=True, max_length=20)
    date = models.CharField(max_length=20)
    trip_id = models.CharField(max_length=20, blank=True, null=True)
    start_stop = models.CharField(max_length=15, blank=True, null=True)
    end_stop = models.CharField(max_length=15, blank=True, null=True)
    time_taken = models.CharField(max_length=10, blank=True, null=True)
    act_dep = models.CharField(max_length=15, blank=True, null=True)
    hang = models.CharField(max_length=20, blank=True, null=True)
    day_of_week = models.CharField(max_length=20, blank=True, null=True)
    hour = models.CharField(max_length=10, blank=True, null=True)
    minute = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'trip_raw'
        unique_together = (('index_id', 'date'),)
