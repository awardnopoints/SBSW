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
        in_order = False
        
        while i < length:

            each = list[i]

            if each['route'] not in recorded:
		#if the order of the current API call is different from the last then a bus has been and gone from the stop       
                #check that j is less than number of buses in last_order so avoid out of index error         
                if j < len(last_order) and last_order[j][1] != each['route'] and not in_order or last_order[j][1] == each['route'] and last_order[j][0] < each['route']:
               #treat last_order like queue. If first element is different from rtpi then the route that that element represents
               #must have been and gone from the stop so remove that element and check the next element in the 'queue'
                    popped_route = last_order.pop(0)
                    insertInDeparted(popped_route[1], stop)
                    time.sleep(1)
 
                elif j < len(last_order) and last_order[j][1] == each['route']:
                #if we get to a point where both the elements are equal after elements have (or haven't) been popped
                #from the last_order then we can assume the rest of the sequence is in order and no more buses need to be recorded
                #as having departed the stop

                    in_order = True
                    
                if in_order:
                #only begin iterating over last_order once the sequence is in order, else keep checking the first element against rtpi
                    j+=1

                recorded.add(each['route'])
                departing_in = each['departureduetime']
                route=each['route']
                timestamp = each['sourcetimestamp']
                
                insert_rtpi(departing_in, route, timestamp, stop)
                #must use a seperate counter to keep track of how many different routes have been recorded at the particular stop
                #so that the current pull can be compared to the last pull
                

            i+=1

        #http://pythonda.com/collecting-storing-tweets-python-mysql

def getLastOrder(stop_id):
    
    result = conex.execute("select * from realtime_bus where stopid = '%s' order by departing_in" % stop_id)
    return result.fetchall()

def insertInDeparted(route, stop):
    print("route",route,"has departed from stop #" + stop)    
  
    conex.execute("insert into departed (time, route, stopid) values ('%s', '%s', %s) on duplicate key update time = '%s'" % (str(datetime.now()), str(route), str(stop),str(datetime.now())))
    
    previous_stop = conex.execute("select previous from departed where route = '%s' and stopid = %s" % (str(route), str(stop))).fetchall()[0]

    updateTimeTaken(route, stop, previous_stop[0])

def updateTimeTaken(route, stop, previous):
    
    try:
      
        current_stop = conex.execute("select time from departed where route = '%s' and stopid = %s" % (str(route), str(stop))).fetchall()[0]
        current_stop = current_stop[0]
        print("route:",route)
        print("current_stop:",stop,"=",current_stop)
        previous_stop = conex.execute("select time from departed where route = '%s' and stopid = %s" % (str(route), str(previous))).fetchall()[0]
        previous_stop = previous_stop[0]
        print("previous_stop:",previous,"=",previous_stop)

        time_taken = to_datetime(current_stop) - to_datetime(previous_stop)
        print("time taken from",previous,"to",stop,":",time_taken.seconds)
        conex.execute("update times_taken set time = %d where current_stop = %s and previous_stop = %s" % (time_taken.seconds, stop, previous))

    except Exception as e:

        print("An error occured while trying to query database", e)

def connect():
    """Function to connect to database on Amazon Web Services"""
    try:
        engine = create_engine(
            'mysql+mysqlconnector://root:sbsw@127.0.0.1:1024/sbsw')
        #port = 3306

        return engine
        
    except Exception as e:
        print("An error occurred when connecting to the database: ", e)
        # https://dev.mysql.com/doc/connector-python/en/connector-python-api-errors-error.html
    # https://campus.datacamp.com/courses/introduction-to-relational-databases-in-python/advanced-sqlalchemy-queries?ex=2#skiponboarding
        
        
def insert_rtpi(departing_in, route, timestamp, stop):
    try:
        if departing_in == "Due":
            departing_in = 0
        conex.execute(
            "insert into realtime_bus (departing_in, timestamp, stopid, route) value (%d, '%s', %s, '%s') on duplicate key update departing_in = %d, timestamp = '%s'" % (int(departing_in), timestamp, stop, route, int(departing_in), timestamp))
  
    except Exception as e:
        print("An error occurred inserting data into rtpi table: ", e)
        exit()

def main():

    while True:

        stops = conex.execute("select stop_id from bus_stops_sequence where route_number = '46A'").fetchall()


        for i in stops:

            url="https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid=" + str(i[0]) + "&format=json"
            data = call_api(url)
            json_parsed = write_file(data)

            go=rtpi()
            go.bus_realtime(json_parsed, i[0])


conex = connect()
conex.connect()
Session = sessionmaker(bind=conex)
session = Session()

if __name__ == "__main__":

    main()
