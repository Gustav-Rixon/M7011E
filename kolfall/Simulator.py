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

global_household_list = []
fastpris = 0


class Household:
    # closest station id fungera som grid? => grid offline no power
    def __init__(self, id, wind, temp, consumption, closest_station_id, closest_station_distance, power_status, turbine_status, production):
        self.id = id
        self.wind = wind
        self.temp = temp
        self.consumption = consumption
        self.closest_station_id = closest_station_id
        self.closest_station_distance = closest_station_distance
        self.power_status = power_status


class PowerPlant:
    def __init__(self, id, production, status, buffert_capacity, buffert_content):
        self.id = id
        self.production = production
        self.status = status
        self.buffert = Buffert(buffert_capacity, buffert_content)


class Buffert:
    def __init__(self, capacity, content):
        self.capacity = capacity
        self.content = content

    # Sadly you cant have more content then capacity
    def buffert_checker(self):
        if self.content > self.capacity:
            return self.capacity


class Exporter:
    def households(household_list):
        _household_list = household_list

    def export(child_conn):
        household_list = Simulator._household_list_in_siumulation
        # Simulator.export()
        child_conn.send(household_list)
        child_conn.close()


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


class Simulator:
    def __init__(self):
        self._household_list_in_siumulation = []
        self._power_plant = []
        self._event_list = []  # TODO EVENTS? power out turbine explode?

    # TODO:SHOULD GET ALL THE HOUSEHOLDS FROM THE DATABASE AND CREATE HOUSEHOLD OBJECTS
    def setupSim():
        p1 = PowerPlant(1, 100, None, 1000, 0)
        h1 = Household(1, None, None, None, 97200, 4500, None, None, None)
        h2 = Household(2, None, None, None, 162790, 3000, None, None, None)
        h3 = Household(3, None, None, None, 162790, 100000, None, None, None)
        h4 = Household(4, None, None, None, 97200, 4500, None, None, None)
        household_list = []
        power_plant_list = []
        household_list.append(h1)
        household_list.append(h2)
        household_list.append(h3)
        household_list.append(h4)
        power_plant_list.append(p1)
        print(household_list)
        return household_list, power_plant_list

    # y = kx+m, k = number of users, x = current consumtion, m = fast pris
    def calculate_electricity_price(current_consumption):
        global global_household_list
        global fastpris
        return len(global_household_list)*current_consumption+fastpris

    def run(self):
        self._household_list_in_siumulation, self._power_plant = Simulator.setupSim()
        self._event_list.append(Events.lightsOut)
        self._event_list.append(Events.lightsOn)

        while True:
            global global_household_list
            global_household_list = self._household_list_in_siumulation
            current_consumption = 0
            current_production = 0
            print("RUNNING")

            for event in self._event_list:
                if len(self._event_list) > 0:
                    event(97200)
                    self._event_list.pop(0)

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

            for power_plant in self._power_plant:
                current_production += power_plant.production

                if power_plant.buffert.content >= power_plant.buffert.capacity:  # OVERFLOWS why?
                    power_plant.buffert.content = power_plant.buffert.capacity - current_consumption
                else:
                    power_plant.buffert.content += current_production-current_consumption

                print("#############current_power_plant_buffert#############")
                print(power_plant.buffert.content)

            print("############current_consumption##############")
            print(current_consumption)
            print("###########################")
            print(Simulator.calculate_electricity_price(current_consumption))
            print("#############current_production#############")
            print(current_production)
            print("#############current_net#############")
            print(current_production-current_consumption)

            sleep(10)

        # On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses
        # set_temp(0,"Strandv%C3%A4gen%205", "104%2040")


if __name__ == "__main__":
    sim = Simulator()
    smhi = get_data_from_station()
    sim.setupSim

    # x = threading.Thread(target=sim.run)
    #x.daemon = True
    # x.start()
    y = threading.Thread(target=smhi.update_data)
    y.daemon = True
    y.start()
    sim.run()  # Main thred
