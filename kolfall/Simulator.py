from multiprocessing import Process, Queue, Pipe
from time import sleep
from mp1 import send_info_wind, send_info_temp
from resources.Rate_limited import rate_limited
import json
from mp1 import calc_station, calc_temp, calc_wind, calc_electricity_consumption


class Simulator:
    def __init__(self):
        self._wind = 1
        self._temp = 0
        self._processes = []

    def get_wind(self):
        return self._wind

    def get_processes(self):
        return self._processes

    @rate_limited(1/10, mode='kill')
    def set_wind(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_wind, args=(
            child_conn, address, zipcode, ))
        p.start()
        self._wind = parent_conn.recv()

    def get_temp(self):
        return self._temp

    @rate_limited(1/10, mode='kill')
    def set_temp(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_temp, args=(
            child_conn, address, zipcode, ))
        p.start()
        self._temp = parent_conn.recv()

    def setupSim(self):
        # TODO SHOULD CREATE AN JSON FILE WITH ALL HOUSE HOLDS
        # RIGHT NOW THIS DOES NOT WORK :(
        print("setup go brrrrrr")
        f = open('EventList.json',)
        data = json.load(f)
        f.close()

        for p in data['house_hold']:
            if(p["data"][0]["closest_station_id"] == 0 and p["data"][0]["closest_station_distance"] == 0):
                address = p["position"][0]["address"]
                zipcode = p["position"][0]["zipcode"]
                test = calc_station(address, zipcode)
                p["data"][0]["closest_station_id"] = test[0]
                p["data"][0]["closest_station_distance"] = test[1]

                f = open('EventList.json', "w")
                f.write(json.dumps(p))
                f.close()

    def run(self):
        while True:
            print("RUNNING")
            with open('EventList.json', 'r+') as f:
                data = json.load(f)
                for p in data['house_hold']:
                    p["data"][0]["temp"] = calc_temp(
                        p["data"][0]["closest_station_id"], p["data"][0]["closest_station_distance"])
                    p["data"][0]["wind"] = calc_wind(
                        p["data"][0]["closest_station_id"], p["data"][0]["closest_station_distance"])
                    p["data"][0]["consumption"] = calc_electricity_consumption(
                        p["data"][0]["temp"])
                    f.seek(0)
                    f.write(json.dumps(data))
                    f.truncate()
            sleep(100)

            # On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses

            #set_temp(0,"Strandv%C3%A4gen%205", "104%2040")
