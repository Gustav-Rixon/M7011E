from multiprocessing import Process, Pipe
from math import floor

from flask.scaffold import F
from resources.GpsTest import *
import numpy as np
import statistics
from multiprocessing import Process, Queue, Pipe


def calc_wind(address, zipcode):
    # take the wind data from SMHI and apply noice depending and distance
    data = json.loads(get_data(address, zipcode))
    print(data)
    lon = float(data[0]['lon'])
    lat = float(data[0]['lat'])
    closest_station = get_close(lon, lat)
    closest_station_id = closest_station[0]
    wind = get_wind(int(closest_station_id))
    closest_station_distance = closest_station[1]

    if (closest_station_distance > 3000):
        noise = statistics.median(np.random.normal(
            0, 1, floor(closest_station_distance/10)))
    else:
        noise = statistics.median(np.random.normal(0, 0.1, 1000))

    wind = float(wind) + noise
    return wind


def calc_temp(address, zipcode):
    # take the temp data from SMHI and apply noice depending and distance
    data = json.loads(get_data(address, zipcode))
    lon = float(data[0]['lon'])
    lat = float(data[0]['lat'])
    closest_station = get_close(lon, lat)
    closest_station_id = closest_station[0]
    temp = get_temp(int(closest_station_id))
    closest_station_distance = closest_station[1]

    if (closest_station_distance > 3000):
        noise = statistics.median(np.random.normal(
            0, 1, floor(closest_station_distance/10)))
    else:
        noise = statistics.median(np.random.normal(0, 0.1, 1000))
    temp = float(temp) + noise
    return temp


def calc_electricity_consumption(address, zipcode):
    temp = calc_temp(address, zipcode)
    consumption = statistics.median(np.random.normal(
        0, 1, 100))
    return abs(consumption-temp)


def calc_production(prosumer, address, zipcode):
    if(prosumer == True):
        return calc_wind(address, zipcode)/2
    else:
        return 0


# ISSU returns the same value?
def send_info_temp(child_conn, address, zipcode):
    data = calc_temp(address, zipcode)
    child_conn.send(data)
    child_conn.close()


def send_info_wind(child_conn, address, zipcode):
    data = calc_wind(address, zipcode)
    child_conn.send(data)
    child_conn.close()
