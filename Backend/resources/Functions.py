from multiprocessing import Process, Pipe
from math import floor
from flask.scaffold import F
from .GpsNominatim import *
import numpy as np
import statistics
from multiprocessing import Process, Queue, Pipe
import jwt


def calc_wind(station_id, distance):
    """[Calculates the wind speed from smhi data and adds noice to the data]

    Args:
        station_id ([int]): [Id of the station]
        distance ([int]): [Distance to the station]

    Returns:
        [int]: [A wind speed]
    """
    wind = get_wind(station_id)

    if (distance > 3000):
        noise = statistics.median(np.random.normal(
            0, 1, floor(distance/10)))
    else:
        noise = statistics.median(np.random.normal(0, 0.1, 1000))

    wind = float(wind) + noise
    return abs(wind)


def calc_station(address, zipcode):
    """[Calculates the closest station for a household]

    .. NOTE::

        This method only returns a smhi weather station

    Args:
        address ([String]): [Households address]
        zipcode ([String]): [Households zipcode]

    Returns:
        [int,int]: [The closest station and its id]
    """
    data = json.loads(get_data(address, zipcode))
    lon = float(data[0]['lon'])
    lat = float(data[0]['lat'])
    closest_station, closest_station_id = get_close(lon, lat)
    return closest_station, closest_station_id


def calc_temp(station_id, distance):
    """[Calculates the temperature of a household by taking Weather station data and applying noise depending on disctance]

    Args:
        station_id ([int]): [Weather stations id]
        distance ([int]): [Distance between the household and station]

    Returns:
        [type]: [Temperature in celsius]
    """

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


def check_JWT(token, id):
    test = jwt.decode(token,
                      "Test", algorithms=["HS256"])

    if str(id) == test.get("id"):
        return True
    else:
        return False
