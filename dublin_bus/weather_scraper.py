import requests
import json
import csv
import datetime
from app import models

def call_api(url):
    """Calls API and returns info from that"""

    req = requests.get(url)
    return req

def write_file (data):
    """Retrieves information from Dublin Bikes API and stores as JSON"""

    req_text= data.text
    json_parsed=json.loads(req_text)
    return json_parsed

def write_to_csv(filename):
    """Converts parsed json to csv and stores in csv file"""
    csv_data=filename[0:]
    csv1_data = open('test.csv', 'a')
    csvwriter = csv.writer(csv1_data)
    count = 0

    for i in csv_data:
        if count == 0:
            header = i.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(i.values())
    csv1_data.close()
    #http://blog.appliedinformaticsinc.com/how-to-parse-and-convert-json-to-csv-using-python/


class weather:
    def current_weather(self):
        """Selects and creates variables that will be stored in dynamic current weather table"""
        
        list=json_parsed['list']
        first = list[0]
        main=first['main']
        temp = main['temp']
        temp_min = main['temp_min']
        temp_max = main['temp_max']
        humidity = main['humidity']
        pressure = main['pressure']
        weather = first['weather']
        weather_desc = weather[0]
        description = weather_desc['description']
        mainDescription = weather_desc['main']
        wind = first['wind']
        speed = wind['speed']
        deg = wind['deg']
        cloud=first['clouds']
        cloudiness=cloud['all']
        dt_txt = first['dt_txt']
             
        print(dt_txt)      
    #http://pythonda.com/collecting-storing-tweets-python-mysql

url="http://api.openweathermap.org/data/2.5/forecast?id=2964574&units=metric&APPID=bb260f441e7da59a28734895b6574b4d"
#url="http://api.openweathermap.org/data/2.5/weather?id=2964574&units=metric&APPID=bb260f441e7da59a28734895b6574b4d"
call_api(url)
data = call_api(url)
json_parsed=write_file(data)

print (json_parsed['main'])
parsed = weather.current_weather(json_parsed)

def orm_bulk_create(parsed):
    instances = [
        models.forecast_weather(
            datetime =dt_txt
            temp=temp
            description=description
            mainDescription=mainDescription
            wind_speed=speed
            humidity=humidity
            pressure=pressure
            cloudiness=cloudiness



#csv_write(json_parsed)

#w = csv.writer(open("output1.csv", "w"))
#for key, val in parsed.items():
#    w.writerow([key, val])

#for key, val in json_parsed.items():
#    print (key)

#https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.to_sql.html
