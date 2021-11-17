import requests


def get_station_data_temp():
    # HOW OFTEN TO UPDATE?????
    # Outside tempature in Celsius
    data_outside = requests.get(
        "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station-set/all/period/latest-hour/data.json")
    data_outside.raise_for_status()
    with open("dataTemp.json", "w") as file:
        file.write(data_outside.text)


def get_station_data_wind():
    # HOW OFTEN TO UPDATE?????
    # wind speed in m/s
    data_outside = requests.get(
        "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/4/station-set/all/period/latest-hour/data.json")
    data_outside.raise_for_status()
    with open("dataWind.json", "w") as file:
        file.write(data_outside.text)
