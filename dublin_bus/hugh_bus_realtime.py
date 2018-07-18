import requests
import json
from sqlalchemy import *
from mysql.connector import errorcode
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pandas import to_datetime
import time

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
    def bus_realtime (self, json_parsed, stop_id):
        """Selects and creates variables that will be stored in dynamic forecast weather table"""

        list=json_parsed['results']
        stop = json_parsed['stopid']
        last_order = getLastOrder(stop_id)
        recorded = set()
        i=0
        j=0
        length=len(list)
        
        while i < length:

            each = list[i]

            if each['route'] not in recorded:
		#if the order of the current API call is different from the last then a bus has been and gone from the stop       
                #check that j is less than number of buses in last_order so avoid out of index error         
                if j < len(last_order) and last_order[j][0] < each['departureduetime']:

                    insertInDeparted(last_order[j][1], stop)

                recorded.add(each['route'])
                departing_in = each['departureduetime']
                route=each['route']
                timestamp = each['sourcetimestamp']
                print("route:",route,"stop:",stop)
                insert_rtpi(departing_in, route, timestamp, stop)
                #must use a seperate counter to keep track of how many different routes have been recorded at the particular stop
                #so that the current pull can be compared to the last pull
                j+=1

            i+=1

        print("executed")
        #http://pythonda.com/collecting-storing-tweets-python-mysql

def getLastOrder(stop_id):
    
    connection = engine.connect()
    result = connection.execute("select * from realtime_bus where stopid = '%s' order by departing_in" % stop_id)
    return result.fetchall()

def insertInDeparted(route, stop):
    
    connection = engine.connect()
    connection.execute("update departed set time = '%s' where route = '%s' and stopid = %s" % (str(datetime.now()), str(route), str(stop)))
    
    previous_stop = connection.execute("select previous from departed where route = '%s' and stopid = %s" % (str(route), str(stop))).fetchall()[0]

    updateTimeTaken(route, stop, previous_stop[0])

def updateTimeTaken(route, stop, previous):
    
    try:
        connection = engine.connect()
        current_stop = connection.execute("select time from departed where route = '%s' and stopid = %s" % (str(route), str(stop))).fetchall()[0]
        current_stop = current_stop[0]
        previous_stop = connection.execute("select time from departed where route = '%s' and stopid = %s" % (str(route), str(previous))).fetchall()[0]
        previous_stop = previous_stop[0]

        time_taken = to_datetime(current_stop) - to_datetime(previous_stop)

        connection.execute("update times_taken set time = %d where current_stop = %s and previous_stop = %s" % (time_taken.seconds, stop, previous))

    except Exception as e:

        print("An error occured while trying to query database", e)

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
        
        
def insert_rtpi(departing_in, route, timestamp, stop):
    try:
        connection = engine.connect()
        if departing_in == "Due":
            departing_in = 0
        connection.execute(
            "update realtime_bus set departing_in=%d, timestamp='%s' where stopid = %s and route = '%s'" % (int(departing_in), timestamp, stop, route))
    except Exception as e:
        print("An error occurred inserting data into rtpi table: ", e)

engine = connect()

def main():

    while True:

        stops = engine.execute("select stop_id from bus_stops_sequence where route_number = '46A'").fetchall()


        for i in stops:

            url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + str(i[0]) + "&format=json"
            data = call_api(url)
            json_parsed = write_file(data)

            go=rtpi()
            go.bus_realtime(json_parsed, i[0])

    

if __name__ == "__main__":

    main()
