from multiprocessing import Process, Pipe
from math import floor

from flask.scaffold import F
from resources.GpsTest import *
import numpy as np
import statistics
from multiprocessing import Process, Queue, Pipe


def calc_wind(station_id, distance):
    # take the wind data from SMHI and apply noice depending and distance
    wind = get_wind(station_id)

    if (distance > 3000):
        noise = statistics.median(np.random.normal(
            0, 1, floor(distance/10)))
    else:
        noise = statistics.median(np.random.normal(0, 0.1, 1000))

    wind = float(wind) + noise
    return abs(wind)


# Calculates the closest station and returns its id and distans
# TODO VAR FÖR KAN DEN INTE TA EMOT ÅÄÖ NU???????? FULL LÖSNING ÅÄ = A; Ö = O
def calc_station(address, zipcode):
    data = json.loads(get_data(address, zipcode))
    lon = float(data[0]['lon'])
    lat = float(data[0]['lat'])
    closest_station = get_close(lon, lat)
    return closest_station


def calc_temp(station_id, distance):
    # take the temp data from SMHI and apply noice depending and distance

    temp = get_temp(station_id)
    if (distance > 3000):
        noise = statistics.median(np.random.normal(
            0, 1, floor(distance/10)))
    else:
        noise = statistics.median(np.random.normal(0, 0.1, 1000))
    temp = float(temp) + noise
    return temp


def calc_electricity_consumption(temp):
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


#print(calc_station("strandvägen 5", "104 40"))
