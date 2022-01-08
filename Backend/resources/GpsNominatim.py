from math import cos, sqrt, pi
import requests
import json


def get_data(address, postalCode):
    """[summary]

    Args:
        address ([type]): [description]
        postalCode ([type]): [description]

    Returns:
        [type]: [description]
    """
    print("*****************************YOU DID A REQUEIST*****************************")
    data = requests.get(
        f"https://nominatim.openstreetmap.org/search.php?street={address}&postalcode={postalCode}&format=jsonv2")._content
    return data


def get_close(lon, lat):
    """[summary]

    Args:
        lon ([type]): [description]
        lat ([type]): [description]

    Returns:
        [type]: [description]
    """
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
    R = 6371000  # radius of the Earth in m
    x = (lon2 - lon1) * cos(0.5*(lat2+lat1))
    y = (lat2 - lat1)
    return (2*pi*R/360) * sqrt(x*x + y*y)


def get_wind(key):
    f = open('data/dataWind.json',)
    data = json.load(f)
    for p in data['station']:
        if (key == int(p['key'])):
            return p['value'][0]['value']


def get_temp(key):
    f = open('data/dataTemp.json',)
    data = json.load(f)
    for p in data['station']:
        if (key == int(p['key'])):
            return p['value'][0]['value']
