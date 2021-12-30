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


# https://www.energimarknadsbyran.se/el/dina-avtal-och-kostnader/elkostnader/elforbrukning/normal-elforbrukning-och-elkostnad-for-villa/
def calc_electricity_consumption(temp):
    consumption = statistics.median(np.random.normal(
        0, 1, 100))
    return 50 + (consumption-temp)


# TODO DO MATH
def calc_production(wind):
    return wind * 10000


# ISSU returns the same value?
def send_info_temp(child_conn, closest_station_id, closest_station_distance):
    data = calc_temp(closest_station_id, closest_station_distance)
    child_conn.send(data)
    child_conn.close()


def send_info_wind(child_conn, closest_station_id, closest_station_distance):
    data = calc_wind(97200, 4500)
    child_conn.send(data)
    child_conn.close()


#print(calc_station("strandvägen 5", "104 40"))
