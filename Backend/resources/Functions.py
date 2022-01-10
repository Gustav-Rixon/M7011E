from math import floor
from Backend.resources.GpsNominatim import *
import numpy as np
import statistics
import jwt


def calc_wind(station_id, distance):
    """[Summary]
        Calculates the wind speed from smhi data and adds noice to the data

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
    return float(abs(wind))


def calc_station(address, zipcode):
    """[Summary]
        Calculates the closest station for a household

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
    """[Summary]
        Calculates the temperature of a household by taking Weather station data and applying noise depending on disctance

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
    return float(temp)


# https://www.energimarknadsbyran.se/el/dina-avtal-och-kostnader/elkostnader/elforbrukning/normal-elforbrukning-och-elkostnad-for-villa/
def calc_electricity_consumption(temp):
    """[summary]
        Calculates the consumtion for a house hold dependning on temprature data.

    Args:
        temp ([int]): [Temperature data from SMHI that has noice added to it. Temp is in celsius]

    Returns:
        [int]: [consumption in kWh]
    """
    consumption = statistics.median(np.random.normal(
        0, 1, 100))
    return int(50 + (consumption-temp))


# TODO DO MATH
def calc_production(wind):
    """[summary]
         Calculates the production for a house hold dependning on wind data.

    Args:
        wind ([type]): [Wind data from SMHI that has noice added to it. Wind is in m/s]

    Returns:
        [type]: [Production in kWh]
    """
    return int(wind * 20)


def check_JWT(token, id, key):
    """[Summary]
        Takes a JWT token and checks if the id is the same as the JWT id 

    Args:
        token ([String]): [JWT token]
        id ([int]): [id of the requester]
        key ([string]): [Key for JWT]


    Returns:
        [Boolean]: [True if its a match, False if not a match]
    """
    test = jwt.decode(token,
                      key=key, algorithms=["HS256"])

    if str(id) == test.get("id"):
        return True
    else:
        return False


def create_JWT(id):
    return jwt.encode({"id": "68"}, "Test", algorithm="HS256")
