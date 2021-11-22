from typing import Pattern
from math import cos, nan, sqrt, pi
import requests
import re
import json

# TODO
# ADD USER INPUT


def get_data(address, postalCode):
    print("*****************************YOU DID A REQUEIST*****************************")
    data = requests.get(
        f"https://nominatim.openstreetmap.org/search.php?street={address}&postalcode={postalCode}&format=jsonv2")._content
    return data


def get_close(lon, lat):
    # Get closest station and the distans between the points
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

    return closestStation, currentD


def distance(lon1, lat1, lon2, lat2):
    # Returns the distans betwen two points
    R = 6371000  # radius of the Earth in m
    x = (lon2 - lon1) * cos(0.5*(lat2+lat1))
    y = (lat2 - lat1)
    return (2*pi*R/360) * sqrt(x*x + y*y)


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


#print('wind ' + get_wind(int(get_close(lon, lat)[0])) + ' m/s')
#print('temp ' + get_temp(int(get_close(lon, lat)[0])) + ' c')
