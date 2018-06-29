import requests
import json
import mysql.connector
from mysql.connector import errorcode
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import datetime
import pytz
from current_weather_scraper import weather

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


def connect():
    """Function to connect to database on Amazon Web Services"""
    try:
        engine = create_engine(
            'mysql+mysqlconnector://root@localhost/sbsw')
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
        connection.execute("TRUNCATE TABLE dbus_forecast_weather;")
        return

    except Exception as e:
        print("An error occurred when deleting forecast rows: ", e)
        
        

def insert_forecast(temp, temp_min, temp_max, description, mainDescription, speed, deg, dt_txt, humidity):
    try:
        connection = engine.connect()
        connection.execute(
            "INSERT INTO dbus_forecast_weather (temp, min_temp, max_temp, description, mainDescription, wind_speed, wind_direction, datetime, humidity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (temp, temp_min, temp_max, description, mainDescription, speed, deg, dt_txt, humidity))
    except Exception as e:
        print("An error occurred inserting data into forecast_weather table: ", e)
    return

url1="http://api.openweathermap.org/data/2.5/forecast?id=2964574&units=metric&APPID=bb260f441e7da59a28734895b6574b4d"

engine = connect()
data1 = call_api(url1)
json_parsed1=write_file(data1)
run = weather()
delete_forecast();
run.forecast_weather()




 
