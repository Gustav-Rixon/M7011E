from time import sleep
import requests
from resources.Rate_limited import rate_limited


class get_data_from_station:
    @rate_limited(1/10, mode='kill')
    def get_station_data_temp():
        # HOW OFTEN TO UPDATE?????
        # Outside tempature in Celsius
        data_outside = requests.get(
            "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/1/station-set/all/period/latest-hour/data.json")
        data_outside.raise_for_status()
        with open("dataTemp.json", "w") as file:
            file.write(data_outside.text)

    @rate_limited(1/10, mode='kill')
    def get_station_data_wind():
        # HOW OFTEN TO UPDATE?????
        # wind speed in m/s
        data_outside = requests.get(
            "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/4/station-set/all/period/latest-hour/data.json")
        data_outside.raise_for_status()
        with open("dataWind.json", "w") as file:
            file.write(data_outside.text)

    @rate_limited(1/10, mode='kill')
    def get_station_data():
        # HOW OFTEN TO UPDATE????? THIS ONE NOT SO MUCH
        # Get station information without values
        data_station = requests.get(
            "https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/34/station-set/all/period/latest-hour/data.json")
        data_station.raise_for_status()
        with open("data.json", "w") as file:
            file.write(data_station.text)

    def update_data(self):
        while True:
            print("UPDATING SMHI DATA")
            get_data_from_station.get_station_data()
            get_data_from_station.get_station_data_wind()
            get_data_from_station.get_station_data_temp()
            sleep(60*60*24)
