from math import floor
from resources.GpsTest import *
import numpy as np
import statistics

def calc_wind(address, zipcode):
    # take the wind data from SMHI and apply noice depending and distance

    data = json.loads(get_data(address, zipcode))

    lon = float(data[0]['lon'])
    lat = float(data[0]['lat'])

    closest_station = get_close(lon, lat)

    closest_station_id = closest_station[0]

    wind = get_wind(int(closest_station_id))

    closest_station_distance = closest_station[1]

    if (closest_station_distance > 3000):
        noise = statistics.median(np.random.normal(0,1,floor(closest_station_distance/10)))
    else:
        noise = statistics.median(np.random.normal(0,0.1,1000))

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
        noise = statistics.median(np.random.normal(0,1,floor(closest_station_distance/10)))
    else:
        noise = statistics.median(np.random.normal(0,0.1,1000))

    temp = float(temp) + noise
    return temp

