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
import sys

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

      
class rtpi:
    def bus_realtime (self):
        """Selects and creates variables that will be stored in dynamic forecast weather table"""

        list=json_parsed['results']
        
        i=0
        length=len(list)
        while i < length:

            each = list[i]
            additional_info=each['additionalinformation']
            arrival_time = each['arrivaldatetime']
            departure_time = each['departuredatetime']
            departing_in = each['departureduetime']
            destination = each['destination']
            destination_local=each['destinationlocalized']
            direction = each['direction']
            arriving_in = each['duetime']
            low_floor=each['lowfloorstatus']
            monitored=each['monitored']
            operator=each['operator']
            origin = each['origin']
            origin_local=each['originlocalized']
            route=each['route']
            scheduled_arrival = each['scheduledarrivaldatetime']
            scheduled_departure = each['scheduleddeparturedatetime']
            timestamp = each['sourcetimestamp']
            i+=1
            
            
            insert_rtpi(arrival_time, departure_time, departing_in, destination, direction, arriving_in, origin, route,  scheduled_arrival, scheduled_departure, timestamp)
        #http://pythonda.com/collecting-storing-tweets-python-mysql

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

def create_table(databasename):
    """Function to create new tables for static, dynamic and latest station info in database"""

    metadata=MetaData()

    realtime_bus = Table('realtime_bus', metadata,                                Column ('arrival_time', String (60)),
        Column ('arrival_time', String (300), primary_key=True),
        Column('departure_time', String (300)),
        Column('departing_in', String (30)),
        Column('destination', String (300)),
        Column('direction', String (100)),
        Column('arriving_in', String (30)),
        Column('origin', String (100)),
        Column('route', String (40), primary_key=True),
        Column('scheduled_arrival', String (300)),
        Column('scheduled_departure', String(300)),
        Column('timestamp', String(300), primary_key=True))

    metadata.create_all(engine, checkfirst=True)

    #http://docs.sqlalchemy.org/en/latest/core/metadata.html
    
def delete_current_rtpi():
    try:
        connection = engine.connect()
        connection.execute("TRUNCATE TABLE realtime_bus;")
        return

    except Exception as e:
        print("An error occurred when deleting current rows: ", e)
        
        
def insert_rtpi(arrival_time, departure_time, departing_in, destination, direction, arriving_in, origin, route,  scheduled_arrival, scheduled_departure, timestamp):
    try:
        connection = engine.connect()
        connection.execute(
            "INSERT INTO realtime_bus(arrival_time, departure_time, departing_in, destination, direction, arriving_in, origin, route,  scheduled_arrival, scheduled_departure, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (arrival_time, departure_time, departing_in, destination, direction, arriving_in, origin, route,  scheduled_arrival, scheduled_departure, timestamp))
    except Exception as e:
        print("An error occurred inserting data into rtpi table: ", e)
    return


stop_id=sys.argv[1]
url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + stop_id + "&format=json"
engine = connect()
#create_table(engine)
delete_current_rtpi()
data = call_api(url)
json_parsed=write_file(data)
go=rtpi()
go.bus_realtime()



