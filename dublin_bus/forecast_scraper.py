import requests
import json
import mysql.connector
from mysql.connector import errorcode
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import datetime
import pytz


# http://docs.sqlalchemy.org/en/latest/orm/tutorial.html
Base = declarative_base()
Session = sessionmaker()
metadata = MetaData()

def call_api(url):
    """Calls API and returns info from that"""

    req = requests.get(url)
    return req

def write_file (data):
    """Retrieves information from Dublin Bikes API and stores as JSON"""

    req_text= data.text
    json_parsed=json.loads(req_text)
    return json_parsed

class weather:
 
    def forecast_weather(self):
        """Selects and creates variables that will be stored in dynamic forecast weather table"""

        list=json_parsed1['list']
        
        i=0
        length=len(list)
        while i < length:

            try:
       	        first = list[i]
                main = first['main']
                temp = main['temp']
            except Exception as e:
                temp = '15.99'
            #temp_min = main['temp_min']
            #temp_max = main['temp_max']
            #humidity = main['humidity']
            #pressure = main['pressure']
            try:
                weather = first['weather']
                weather_desc = weather[0]
                mainDescription = weather_desc['main']
            except Exception as e:
                mainDescription = 'Clouds'
            #description = weather_desc['description']
            try:
                wind = first['wind']
                speed = wind['speed']
            except Exception as e:
                speed = '6'
            #deg = wind['deg']
            #cloud=first['clouds']
            #cloudiness=cloud['all']
            try:
                dt_txt = first['dt_txt']
            except:
                dt_txt = '2018-08-16 12:00:00'
            i+=1
            
            try:
                insert_forecast(temp, mainDescription, speed, dt_txt)
            except Exception as e:
                pass

    #http://pythonda.com/collecting-storing-tweets-python-mysql


    def current_weather(self):

    #        list1=json_parsed['list']
    #        first = list1[0]
        try:
            main1_current=json_parsed2['main']
            temp_current = main1_current['temp']
        except Exception as e:
            temp_current = '15.99'
        #temp_min_current = main1_current['temp_min']
        #temp_max_current = main1_current['temp_max']
        #humidity_current = main1_current['humidity']
        #pressure_current = main1_current['pressure']
        try:
            weather_current = json_parsed2['weather']
            weather_desc_current = weather_current[0]
            mainDescription_current = weather_desc_current['main']
        except Exception as e:
            mainDescription_current = 'Clouds'
            
        #description_current = weather_desc_current['description']
        try:
            wind_current = json_parsed2['wind']
            speed_current = wind_current['speed']
        except Exception as e:
            speed_current = '6'
        #deg_current = wind_current['deg']
        #cloud_current=json_parsed2['clouds']
        #cloudiness_current=cloud_current['all']
        try:
            dt_current = json_parsed2['dt']
        except Exception as e:
            dt_current = '1534417200'
        timestamp_current=datetime.datetime.fromtimestamp(dt_current, pytz.timezone('Europe/Dublin'))

        try:
            insert_current(temp_current, mainDescription_current, speed_current, timestamp_current)
        except Exception as e:
            pass

        #http://pythonda.com/collecting-storing-tweets-python-mysql

def connect():
    """Function to connect to database on Amazon Web Services"""
    try:
        engine = create_engine(
            'mysql+mysqlconnector://root:sbsw@127.0.0.1:1024/sbsw')
        #port = 3306
        connection = engine.connect()
        Session.configure(bind=engine)
        return engine
        # https://campus.datacamp.com/courses/introduction-to-relational-databases-in-python/advanced-sqlalchemy-queries?ex=2#skiponboarding

    except Exception as e:
        print("An error occurred when connecting to the database: ", e)
        # https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-error.html
    # https://campus.datacamp.com/courses/introduction-to-relational-databases-in-python/advanced-sqlalchemy-queries?ex=2#skiponboarding

def delete_current():
    try:
        connection = engine.connect()
        connection.execute("TRUNCATE TABLE dbus_current_weather;")
        return

    except Exception as e:
        print("An error occurred when deleting current rows: ", e)

def delete_forecast():
    try:
        connection = engine.connect()
        connection.execute("TRUNCATE TABLE dbus_forecast;")
        return

    except Exception as e:
        print("An error occurred when deleting forecast rows: ", e)
        
        
def insert_current(temp_current, mainDescription_current, speed_current, timestamp_current):
    try:
        connection = engine.connect()
        connection.execute(
            "INSERT INTO dbus_forecast  (temp, mainDescription, wind_speed, datetime) VALUES (%s, %s, %s, %s);",
            (temp_current, mainDescription_current, speed_current, timestamp_current))
    except Exception as e:
        print("An error occurred inserting data into current_weather table: ", e)
    return

def insert_forecast(temp, mainDescription, speed, dt_txt):
    connection = engine.connect()
    connection.execute(
        "INSERT INTO dbus_forecast (temp, mainDescription, wind_speed, datetime) VALUES (%s, %s, %s, %s);",
        (temp, mainDescription, speed, dt_txt))
    print("An error occurred inserting data into forecast_weather table: ", e)
    return

if __name__ == "__main__":
    url1="http://api.openweathermap.org/data/2.5/forecast?id=2964574&units=metric&APPID=bb260f441e7da59a28734895b6574b4d"
    url2="http://api.openweathermap.org/data/2.5/weather?id=2964574&units=metric&APPID=bb260f441e7da59a28734895b6574b4d"
    engine = connect()

    data1 = call_api(url1)
    data2 = call_api(url2)
    json_parsed1=write_file(data1)
    json_parsed2=write_file(data2)

    run = weather()
    delete_forecast()
    run.current_weather()
    run.forecast_weather()
