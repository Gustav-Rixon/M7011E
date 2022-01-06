import threading
from time import sleep
from resources.Rate_limited import rate_limited
from mp1 import calc_temp, calc_wind, calc_electricity_consumption, calc_production
from werkzeug.wrappers import Request, Response
from Lorax import create_house_holds_objects, create_power_plants_objects, register, login, add_house_hold, admin_login, checktest, remove_user_from_database, remove_user_from_simulation
from Market import Market
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import responder


global_household_list = []
global_power_plant_list = []
global_event_list = []
global_market = Market(0)
fixed_price = 10


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
            if power_plant._id == id:
                power_plant._production = order

    # event id 3 - blackout
    def blackout_whole_network():
        global global_household_list
        for household in global_household_list:
            household._power_status = 0

    # event id 4 - blackout
    def remove_blackout():
        global global_household_list
        for household in global_household_list:
            household._power_status = 1

    # event id 5
    def remove_participant_from_simulation():
        global global_household_list
        for household in global_household_list:
            household._power_status = 1

    def remove_participant():
        global global_household_list
        for household in global_household_list:
            household._power_status = 1


class Simulator:
    def __init__(self):
        self._household_list_in_siumulation = []
        self._power_plants = []
        self._event_list = []  # TODO EVENTS? power out turbine explode?
        self._total_buffert = 0
        self._simulator_market = 0
        self._consumer_households_in_siumulation = []
        self._prosumer_households_in_siumulation = []

    # TODO:SHOULD GET ALL THE HOUSEHOLDS FROM THE DATABASE AND CREATE HOUSEHOLD OBJECTS
    # kWh
    def setupSim():
        list_of_consumer, list_of_prosumer = create_house_holds_objects()
        power_plant_list = create_power_plants_objects()
        return list_of_consumer, list_of_prosumer, power_plant_list

    def calc_consumer(list_of_consumer):
        total_consumer_consumption = 0
        for consumer in list_of_consumer:
            consumer._temp = calc_temp(
                consumer._closest_station_id, consumer._closest_station_distance)
            consumer._consumption = calc_electricity_consumption(
                consumer._temp)
            total_consumer_consumption += consumer._consumption
        return total_consumer_consumption

    def calc_prosumer(list_of_prosumer):
        total_prosumer_consumption = 0
        total_prosumer_production = 0
        for prosumer in list_of_prosumer:
            prosumer._wind = calc_wind(
                prosumer._closest_station_id, prosumer._closest_station_distance)
            prosumer._production = calc_production(
                prosumer._wind)
            prosumer._temp = calc_temp(
                prosumer._closest_station_id, prosumer._closest_station_distance)
            prosumer._consumption = calc_electricity_consumption(
                prosumer._temp)

            if prosumer._production > prosumer._consumption:  # Only send to buffert when condison is meet
                # TODO In case of excessive production, Prosumer should be able to control the ratio of how much should be sold to the market and how much should be sent to the buffer
                prosumer._buffert.content += (prosumer._production -
                                              prosumer._consumption)*prosumer._ratio_to_market
                global_market.market_buffert.content = (prosumer._production -
                                                        prosumer._consumption)*(1-prosumer._ratio_to_market)

            if prosumer._consumption > prosumer._production:  # TODO REMOVE UNDERSKOTT FRÅN BUFFERT
                prosumer._buffert.content -= abs(prosumer._production -
                                                 prosumer._consumption)

            if prosumer._buffert.content < 0:  # cant have 0 power
                prosumer._buffert.content = 0

            total_prosumer_consumption += prosumer._consumption
            total_prosumer_production += prosumer._production
        return total_prosumer_consumption, total_prosumer_production

    def calc_power_plant_production(list_of_power_plants):
        total_production = 0
        for power_plant in list_of_power_plants:
            total_production += power_plant._production
        return total_production

    # TODO BE ABLE TO ADD NEW USERS TO THE LOOP AND REMOVE THEM
    def run(self):
        self._consumer_households_in_siumulation, self._prosumer_households_in_siumulation, self._power_plant = Simulator.setupSim()
        self._simulator_market = Market(1000)

        global global_household_list
        global global_power_plant_list
        global global_event_list
        global global_market

        global_household_list = self._consumer_households_in_siumulation + \
            self._prosumer_households_in_siumulation
        global_power_plant_list = self._power_plant
        global_market = self._simulator_market

        # global_event_list.append(Events.change_production)

        while True:

            print("RUNNING")
            self._consumer_households_in_siumulation, self._prosumer_households_in_siumulation = checktest(self._consumer_households_in_siumulation,
                                                                                                           self._prosumer_households_in_siumulation)
            # global_household_list = self._consumer_households_in_siumulation + \
            #    self._prosumer_households_in_siumulation
            # TODO HAVE A LIST OR INSTAND ACTION
            # for event in global_event_list:
            #    if len(global_event_list) > 0:
            #        event()  # pre defined varibels pls
            #        global_event_list.pop(0)

            simulator_consumption, simulator_production = Simulator.calc_prosumer(
                self._prosumer_households_in_siumulation)

            simulator_consumption += Simulator.calc_consumer(
                self._consumer_households_in_siumulation)

            simulator_production += Simulator.calc_power_plant_production(
                self._power_plant)

            market_status = self._simulator_market.update_market(
                simulator_production-simulator_consumption)

            #################################################

            if self._simulator_market.market_buffert.content == 0:
                Events.blackout_whole_network()

            if self._simulator_market.market_buffert.content > 0:
                Events.remove_blackout()

            for object in self._consumer_households_in_siumulation:
                print(
                    f"CONSUMER id:{object._id} status:{object._power_status}")

            for object in self._prosumer_households_in_siumulation:
                object.power_check()
                print(
                    f"PROSUMER id:{object._id} status:{object._power_status} buffert:{object._buffert.content} consumption:{object._consumption} production:{object._production}")

            #################################################

            print(f"markut status {market_status}")

            print("############current_consumption##############")
            print(simulator_consumption)
            print("#############current_production total#############")
            print(simulator_production)
            print("#############current_net#############")
            print(simulator_production-simulator_consumption)
            print(
                f"????????????????? {global_market.market_buffert.content} ?????????????????")
            sleep(1)

        # On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses
        # set_temp(0,"Strandv%C3%A4gen%205", "104%2040")


# TODO MAKE METHODS ONYL RESPOND IF CORRECT GET/POST IS USED
# TODO ADD TOKEN FROM FRONTEND
class SimulatorEndPoints:

    @rate_limited(1/10, mode='kill')
    def on_change_power_plant_output(request, **data):
        Events.change_production(data.get('id'), data.get('power'))
        return Response(f"burning {data} hamsters insted")

    def buy(request, **data):
        global global_market
        for house_hold in global_household_list:
            if house_hold._id == data.get('id'):
                if data.get('amount') < global_market.market_buffert.content:
                    house_hold._buffert.content += data.get('amount')
                    Market.buy_from_market(global_market, data.get('amount'))
                    return Response(f"SUCC {global_market.market_buffert.content}")
                return Response(f"FAIL {global_market.market_buffert.content}")

    def sell(request, **data):
        global global_market
        for house_hold in global_household_list:
            if house_hold._id == data.get('id'):
                if data.get('amount') < house_hold._buffert.content:
                    house_hold._buffert.content -= data.get('amount')
                    Market.send_to_market(global_market, data.get('amount'))
                    return Response(f"SUCC {global_market.market_buffert.content}")
                return Response(f"FAIL {house_hold._buffert.content}")

    @rate_limited(1/10, mode='kill')  # FIX
    def change_market_size(request, **data):
        global global_market
        Market.change_market_size(global_market, data.get('size'))
        return Response(f"Changning market size to {data.get('size')} hamsters insted")

    def get_house_hold_consumption(request, **data):
        global global_household_list
        for house_hold in global_household_list:
            if house_hold._id == data.get('id'):
                return Response(str(house_hold.consumption))
            else:
                return Response("do not finns")

    @responder
    def application(environ, start_response):
        url_map = Map([
            Rule(
                '/admin/tools/change_power/id=<int:id>&power=<int:power>', endpoint='change_power'),
            Rule(
                '/buy/house_hold/prosumer/house_hold=<int:id>&amount=<int:amount>', endpoint='buy'),
            Rule(
                '/sell/house_hold/prosumer/house_hold=<int:id>&amount=<int:amount>', endpoint='sell'),
            Rule('/admin/tools/change_market_size/size=<int:size>',
                 endpoint="change_market_size"),
            Rule('/DATA/house_hold/consumption/house_hold=<int:id>',
                 endpoint='get_house_hold_consumption'),
            Rule(
                '/register/username=<string:username>&password=<string:password>&email=<string:email>&address=<string:address>&zipcode=<string:zipcode>&prosumer=<int:prosumer>', endpoint='register'),
            Rule('/login/username=<string:username>', endpoint='login'),
            Rule('/test/username=<string:username>', endpoint='test'),
            Rule('/admin/login/username=<string:username>',
                 endpoint='admin_login'),
            Rule('/admin/remove_user/user_id=<int:user_id>',
                 endpoint='remove_user'),
            Rule('/test', endpoint='test2')
        ])

        views = {'change_power': SimulatorEndPoints.on_change_power_plant_output,
                 'buy': SimulatorEndPoints.buy,
                 'sell': SimulatorEndPoints.sell,
                 'change_market_size': SimulatorEndPoints.change_market_size,
                 'get_house_hold_consumption': SimulatorEndPoints.get_house_hold_consumption,
                 'register': register,
                 'login': login,
                 'test': add_house_hold,
                 'admin_login': admin_login,
                 'remove_user': remove_user_from_database,
                 'test2': remove_user_from_simulation}

        request = Request(environ)
        urls = url_map.bind_to_environ(environ)
        return urls.dispatch(lambda e, v: views[e](request, **v),
                             catch_http_exceptions=True)


if __name__ == "__main__":
    sim = Simulator()
    # smhi = get_data_from_station()

    x = threading.Thread(target=sim.run)
    x.daemon = True
    x.start()
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, SimulatorEndPoints.application)
