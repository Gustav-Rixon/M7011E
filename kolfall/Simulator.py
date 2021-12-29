from multiprocessing import Process, Queue, Pipe
from multiprocessing.process import current_process
import threading
import signal
from time import sleep
from mp1 import send_info_wind, send_info_temp
from resources.Rate_limited import rate_limited
import json
from mp1 import calc_station, calc_temp, calc_wind, calc_electricity_consumption
from werkzeug.wrappers import Request, Response
from multiprocessing import Process, Queue, Pipe
from resources.GetDataFromExApi import get_data_from_station
from Lorax import create_house_holds_objects, create_power_plants_objects
from flask import Flask, json, jsonify

global_household_list = []
global_power_plant_list = []
global_event_list = []
fastpris = 10

app = Flask(__name__)


class Events:
    # TODO SHOULD HAVE type: GLOBAL EVENT; GRID EVENT; HOUSEHOLD EVENT
    def __init__(self, type):
        self.type = type

    # event id 0 - Shit got dark pls help
    def lightsOut(grid_id):
        print("LIGHTS OUT")
        global global_household_list
        for household in global_household_list:
            if household.closest_station_id == grid_id:
                household.power_status = 0

    # event id 1 - Give light
    def lightsOn(grid_id):
        print("LIGHTS ON")
        global global_household_list
        for household in global_household_list:
            if household.closest_station_id == grid_id:
                household.power_status = 1

    # event id 2 - Change power plant prod
    def change_production(id, order):
        global global_power_plant_list
        print("Burning more hamsters!!!!")
        for power_plant in global_power_plant_list:
            if power_plant.id == id:
                power_plant.production = order


class Simulator:
    def __init__(self):
        self._household_list_in_siumulation = []
        self._power_plants = []
        self._event_list = []  # TODO EVENTS? power out turbine explode?
        self._total_buffert = 0

    # TODO:SHOULD GET ALL THE HOUSEHOLDS FROM THE DATABASE AND CREATE HOUSEHOLD OBJECTS
    # kWh
    def setupSim():
        household_list = create_house_holds_objects()
        power_plant_list = create_power_plants_objects()
        return household_list, power_plant_list

    # y = kx+m, k = number of users, x = current consumtion, m = fast pris öre/kWh
    def calculate_electricity_price(current_consumption, current_buffert):
        global global_household_list
        global fastpris

        if ((len(global_household_list)*current_consumption) + fastpris - current_buffert <= fastpris):
            return fastpris
        else:
            return (len(global_household_list)*current_consumption) + fastpris - current_buffert

    def run(self):
        self._household_list_in_siumulation, self._power_plant = Simulator.setupSim()
        # self._event_list.append(Events.lightsOut)
        # self._event_list.append(Events.lightsOn)

        global global_household_list
        global global_power_plant_list
        global global_event_list
        global_household_list = self._household_list_in_siumulation
        global_power_plant_list = self._power_plant

        # global_event_list.append(Events.change_production)

        while True:
            current_consumption = 0
            current_production = 0
            total_current_production = 0

            print("RUNNING")

            # TODO HAVE A LIST OR INSTAND ACTION
            # for event in global_event_list:
            #    if len(global_event_list) > 0:
            #        event()  # pre defined varibels pls
            #        global_event_list.pop(0)

            for household in self._household_list_in_siumulation:
                household.wind = calc_wind(
                    household.closest_station_id, household.closest_station_distance)
                household.temp = calc_temp(
                    household.closest_station_id, household.closest_station_distance)
                household.consumption = calc_electricity_consumption(
                    household.temp)

                print(household.id, household.wind,
                      household.temp,  household.consumption, household.power_status)
                current_consumption += household.consumption

            #############################Powerplant and buffert#######################################

            # I CRY want to calculate what the networks capacity is
            for power_plant in self._power_plant:

                print("#############current_production from reactor #############")
                print(power_plant.production)
                print("#############current_buffert in reactor #############")
                print(power_plant.buffert.content)

                #############################Powerplant and buffert#######################################

            print("############current_consumption##############")
            print(current_consumption)
            print("###########################")
            print(f"buffert is {self._total_buffert}")
            print(Simulator.calculate_electricity_price(
                current_consumption, self._total_buffert))
            print("#############current_production total#############")
            print(power_plant.production)
            print("#############current_net#############")
            print(total_current_production-current_consumption)
            sleep(1)

        # On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses
        # set_temp(0,"Strandv%C3%A4gen%205", "104%2040")


class API_ENDPOINTS:
    @app.route('/DATA/house_hold/consumption/house_hold=<int:id>', methods=['GET'])
    def get_house_hold_consumption(id):
        global global_household_list

        for house_hold in global_household_list:
            if house_hold.id == id:
                return str(house_hold.consumption)
            else:
                return "do not finns"

    # ONLY WORKS FOR ONE EVENT
    @app.route('/admin/tools/change_power/id=<int:id>&power=<int:power>', methods=['POST'])
    @rate_limited(1/10, mode='kill')
    def change_power(id, power):
        Events.change_production(id, power)
        return f"burning {power} hamsters insted"


if __name__ == "__main__":
    sim = Simulator()
    #smhi = get_data_from_station()

    x = threading.Thread(target=sim.run)
    x.daemon = True
    x.start()
    #y = threading.Thread(target=smhi.update_data)
    #y.daemon = True
    # y.start()
    app.run()  # Main thred
