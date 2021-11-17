from typing import Pattern
from math import cos, nan, sqrt, pi
import requests
import re
import json


# TODO
# ADD USER INPUT

def get_data(address, postalCode):
    data = requests.get(
        f"https://nominatim.openstreetmap.org/search.php?street={address}&postalcode={postalCode}&format=jsonv2")._content
    return data


test = json.loads(get_data("Strandvägen 5", "104 40"))
lon = float(test[0]['lon'])
lat = float(test[0]['lat'])


def get_close(lon, lat):
    # Get closest station
    f = open('data.json',)
    data = json.load(f)

    closestStation = None
    currentD = 10000000000  # REMOVE

    for p in data['station']:
        latTMP = p['latitude']
        lonTMP = p['longitude']

        d = distance(lon, lat, lonTMP, latTMP)

        if (d < currentD):
            currentD = d
            closestStation = p['key']

    return closestStation


def distance(lon1, lat1, lon2, lat2):
    # Returns the distans betwen two points
    R = 6371000  # radius of the Earth in m
    x = (lon2 - lon1) * cos(0.5*(lat2+lat1))
    y = (lat2 - lat1)
    return R * sqrt(x*x + y*y)


def get_wind(key):
    # Thunderfury blessed blade of the windseeker
    f = open('dataWind.json',)
    data = json.load(f)
    for p in data['station']:
        if (key == int(p['key'])):
            return p['value'][0]['value']


def get_temp(key):
    # By fire be purged
    f = open('dataTemp.json',)
    data = json.load(f)
    for p in data['station']:
        if (key == int(p['key'])):
            return p['value'][0]['value']


#print(get_wind(int(get_close(lon, lat))))
#print(get_temp(int(get_close(lon, lat))))
