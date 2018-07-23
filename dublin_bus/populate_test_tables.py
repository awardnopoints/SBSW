import sqlalchemy as sa
import datetime

def main():

    engine = sa.create_engine("mysql+mysqlconnector://root:sbsw@127.0.0.1:1024/sbsw")
    
    conex = engine.connect()

    stops = conex.execute("select stop_id from bus_stops_sequence where route_number = '%s'" % "46A").fetchall()

    start = False

    for i in stops:

        if not start:
 
            start_stop = i[0]
            start = True

        else:

             destination = i[0]

             if start_stop != destination:

                 conex.execute("insert into departed(route, stopid, time, previous) values('%s', %s, '%s', %s)" % ('46A', destination, datetime.datetime.now(), start_stop))

             start_stop = i[0]


if __name__ == "__main__":
    main()
    
