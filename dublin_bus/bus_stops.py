import requests
import json
import csv
import datetime
import mysql.connector
from mysql.connector import errorcode
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
import pandas as pd
from pandas.io import sql

#http://docs.sqlalchemy.org/en/latest/orm/tutorial.html
Base = declarative_base()
Session = sessionmaker()
metadata=MetaData()

def call_api(url):
    """Calls API and returns info from that"""

    req = requests.get(url)
    return req

def write_file (data):
    """Retrieves information from Dublin Bikes API and stores as JSON"""

    req_text= data.text
    json_parsed=json.loads(req_text)
    return json_parsed

class stops:
    def bus_stops(self):
        list=json_parsed['results']
        length_stop=len(list)
        i=0
        stop_dict=dict()
        bus_stops=dict()
        while i < length_stop:
            first = list[i]
            stop=first['displaystopid']
            stop_name=first['fullname']
            local_name=first['fullnamelocalized']
            last_update=first['lastupdated']
            lat=first['latitude']
            longitude=first['longitude']
            more=first['operators'][0]
            name=more['name']
            routes=more['routes']
            short_name=first['shortname']
            short_local=first['shortnamelocalized']
            stop2=first['stopid']
            if name == 'bac':
                stop_id=stop
                bac_routes=routes
                bus_stops[stop_id]=lat, longitude, stop_name
                stop_dict[stop_id]=bac_routes
       
            i+=1

            insert_stops(stop_id, lat, stop_name, longitude)

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



def create_table(databasename):
    """Function to create new tables for static, dynamic and latest station info in database"""

    metadata=MetaData()

#    dbus_stopsv3 = Table('dbus_stopsv3', metadata,
 #       Column('stop_id', Integer, primary_key=True),
#        Column('lat', String(400)),
#        Column('stop_name', String (400)),
 #       Column('longitude', Float(40)))

    dbus_stop_names = Table('dbus_stop_names', metadata,
        Column('stop_number', Integer),
        Column('stop_address', String(400)))
    
    metadata.create_all(engine, checkfirst=True)

def insert_stops(stop_id, lat, stop_name, longitude):
    try:
        connection = engine.connect()
        connection.execute(
            "INSERT INTO dbus_stopsv3(stop_id, lat, stop_name, longitude) VALUES (%s, %s, %s, %s);",
            (stop_id, lat, stop_name, longitude))
    except Exception as e:
        print("An error occurred inserting data into stops3 table: ", e)
    return



url="https://data.smartdublin.ie/cgi-bin/rtpi/busstopinformation?stopid&format=json"
call_api(url)
data = call_api(url)
json_parsed=write_file(data)
engine=connect()
create_table(engine)

df = pd.read_csv('stop_names.csv', index_col=0)
df.to_sql(name='dbus_stop_names',con=engine,if_exists='append',index=False)

run = stops()
#delete_forecast();
#run.bus_stops()


