import json
from time import sleep
from Backend.resources.RateLimited import rate_limited
from Backend.resources.GpsNominatim import get_data
from Backend.resources.Functions import calc_temp, calc_wind, calc_electricity_consumption, calc_production, check_JWT, do_ceil
from werkzeug.wrappers import Request, Response
from Backend.Lorax import create_house_holds_objects, create_power_plants_objects, register, login, add_house_hold, admin_login, check, remove_user_from_database, remove_user_from_simulation, upload_user_pic, get_user_pic, change_user_info
from Backend.Market import Market
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.wsgi import responder
from werkzeug.utils import secure_filename
import os
import base64
import random

global_household_list = []
global_power_plant_list = []
global_event_list = []
global_market = Market(0)


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
        try:
            global global_power_plant_list
            print(order)
            print(id)
            print("Burning more hamsters!!!!")
            for power_plant in global_power_plant_list:
                if power_plant._id == int(id):
                    power_plant._production = int(order)
        except ValueError as e:
            return e

    # event id 3 - blackout
    def blackout_whole_network():
        global global_household_list
        for household in global_household_list:
            household._power_status = 0
            household._blackout = 1

    # event id 4 - blackout
    def remove_blackout():
        global global_household_list
        for household in global_household_list:
            if household._blackout_duration > 0:
                household._blackout_duration -= 1
                continue
            household._power_status = 1

    def blackout_house_hold():
        global global_household_list
        target = random.randint(1, len(global_household_list))
        number_of_cycels = random.randint(1, 10)
        for household in global_household_list:
            if household._id == target:
                household._power_status = 0
                household._blackout_duration = number_of_cycels
                household._consumption = 0

    def change_power():
        global global_power_plant_list
        for power_plant in global_power_plant_list:
            if power_plant._changing_power == True:
                change = do_ceil(
                    power_plant._change_left, power_plant._changing_power_number_of_cyckels)
                power_plant._change_left -= change

                power_plant._production -= -change
                power_plant._changing_power_number_of_cyckels -= 1

                if power_plant._changing_power_number_of_cyckels == 0:
                    power_plant._changing_power = False
                    pass


class Simulator:
    """[summary]
        This it the main object that hadnels the simulation.
    """

    def __init__(self):
        self._household_list_in_siumulation = []
        self._power_plants = []
        self._event_list = []  # TODO EVENTS? power out turbine explode?
        self._total_buffert = 0
        self._simulator_market = 0
        self._consumer_households_in_siumulation = []
        self._prosumer_households_in_siumulation = []
        self._debugmode = False

    def setupSim():
        """[summary]
            Setups the first batch of house hold objects for the simulation.
            And the power plant

        Returns:
            [lists]: [list of consumers, list of prosumer and list of power plants ]
        """
        list_of_consumer, list_of_prosumer = create_house_holds_objects()
        power_plant_list = create_power_plants_objects()
        return list_of_consumer, list_of_prosumer, power_plant_list

    def get_JWC_keys():
        global key
        global adminKey
        f = open('conf/configuration.json')
        data = json.load(f)
        adminKey = data.get("JWT_KEYS").get("admin_key")
        key = data.get("JWT_KEYS").get("user_key")

    def calc_consumer(list_of_consumer):
        """[summary]
            Calcualates how much all the consumers consume.

        Args:
            list_of_consumer ([list]): [List of consumers in simulation.]

        Returns:
            [int]: [Total consumption from consumers]
        """
        total_consumer_consumption = 0
        for consumer in list_of_consumer:

            if consumer._blackout_duration > 0:
                continue

            consumer._temp = calc_temp(
                consumer._closest_station_id, consumer._closest_station_distance)
            consumer._consumption = calc_electricity_consumption(
                consumer._temp)
            total_consumer_consumption += consumer._consumption
        return total_consumer_consumption

    def calc_prosumer(list_of_prosumer):
        """[summary]
            Calcualates how much all the prosumer consumes and produces.

        Args:
            list_of_prosumer ([list]): [List of prosumer objects in simulation]

        Returns:
            [int]: [Total prosumer consumption and total prosumer production]
        """
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
                prosumer._buffert.content += (prosumer._production -
                                              prosumer._consumption)*(1-prosumer._ratio_to_market)
                # global_market.market_buffert.content = (prosumer._production -
                #                                        prosumer._consumption)*prosumer._ratio_to_market

            if prosumer._consumption > prosumer._production:
                prosumer._buffert.content -= abs(prosumer._production -
                                                 prosumer._consumption)

            if prosumer._buffert.content < 0:  # cant have negetiv power
                prosumer._buffert.content = 0

            total_prosumer_consumption += prosumer._consumption
            total_prosumer_production += prosumer._production
        return total_prosumer_consumption, total_prosumer_production

    def calc_power_plant_production(list_of_power_plants):
        """[summary]
            Calculate power plant production.

            NOTE
            Only one power plant object can be present in the simulation

        Args:
            list_of_power_plants ([list]): [A list of power plant objects]

        Returns:
            [int]: [Total power plant production]
        """
        total_production = 0
        for power_plant in list_of_power_plants:

            power_plant._buffert.content += power_plant._production * \
                (1-power_plant._ratio_to_market)

            power_plant.check_buffert()

            total_production += power_plant._production * \
                (power_plant._ratio_to_market)
        return total_production

    def run(self):
        """[summary]

        Args:
            debugmode ([Boolean]): [If true prints debug messages]

        """
        Simulator.get_JWC_keys()
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

        while True:

            self._consumer_households_in_siumulation, self._prosumer_households_in_siumulation = check(self._consumer_households_in_siumulation,
                                                                                                       self._prosumer_households_in_siumulation)

            Events.blackout_house_hold()
            Events.remove_blackout()
            Events.change_power()

            global_household_list = self._consumer_households_in_siumulation + \
                self._prosumer_households_in_siumulation

            simulator_consumption, simulator_production = Simulator.calc_prosumer(
                self._prosumer_households_in_siumulation)

            simulator_consumption += Simulator.calc_consumer(
                self._consumer_households_in_siumulation)

            simulator_production += Simulator.calc_power_plant_production(
                self._power_plant)

            global_market.update_market(
                simulator_production-simulator_consumption)

            if self._debugmode == True:

                print("RUNNING")

                for object in self._consumer_households_in_siumulation:
                    print(
                        f"CONSUMER id:{object._id} status:{object._power_status}")

                for object in self._prosumer_households_in_siumulation:
                    object.power_check()
                    print(
                        f"PROSUMER id:{object._id} status:{object._power_status} buffert:{object._buffert.content} consumption:{object._consumption} production:{object._production}")

                global_market.calculate_recommended_electricity_price(
                    simulator_consumption, len(global_household_list))
                print("############current_consumption##############")
                print(simulator_consumption)
                print("#############current_production total#############")
                print(simulator_production)
                print("#############current_net#############")
                print(simulator_production-simulator_consumption)
                print(
                    f"????????????????? {global_market.market_buffert.content} ?????????????????")
                print(f"POWER{global_power_plant_list[0]._production}")
            sleep(1)

        # On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses
        # set_temp(0,"Strandv%C3%A4gen%205", "104%2040")


class SimulatorEndPoints:
    """[summary]
        Contains all the API endpoints and their handels theres requests.
    """

    # @rate_limited(1/10, mode='kill')
    def on_change_power_plant_output(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):

                for power_plant in global_power_plant_list:
                    if power_plant._id == int(request.args.get('target')):

                        if int(request.args.get('power')) == power_plant._production:
                            return Response("Changeing to nothing")

                        else:
                            change = int(request.args.get('power')
                                         ) - power_plant._production

                            number_of_cycels = random.randint(1, 10)
                            power_plant._changing_power_number_of_cyckels = number_of_cycels
                            power_plant._change_left = change
                            power_plant._changing_power = True
                    return Response("Changing power")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def view_power_plant(request):
        if request.method == ('GET'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                data = []
                for power_plant in global_power_plant_list:
                    data.append(
                        {"id": power_plant._id, "production": power_plant._production, "status": power_plant._status,
                         "Buffert content": power_plant._buffert.content, "Buffert size": power_plant._buffert.capacity, "Ratio to market": power_plant._ratio_to_market})
                contents = json.dumps(data, sort_keys=False)
                return Response(contents, content_type="application/json")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def change_power_plant_ratio(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                for power_plant in global_power_plant_list:
                    if int(request.args.get("target")) == power_plant._id:

                        if int(request.args.get("target")) < 0:
                            return Response("Must be posetive")

                        power_plant._ratio_to_market = int(
                            request.args.get("ratio"))/100
                    return Response("Changing ratio")
                return Response("Powerplant not found")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def send_to_market(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                for power_plant in global_power_plant_list:
                    if int(request.args.get("target")) == power_plant._id:

                        if int(request.args.get("amount")) < 0:
                            return Response("Must be posetive")

                        amount = int(request.args.get("amount"))

                        if amount > power_plant._buffert.content:
                            return Response("Cant sell more then curret content")

                        Market.send_to_market(global_market, amount)
                        power_plant._buffert.content -= amount

                    return Response("Sent power to market")
                return Response("Powerplant not found")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def buy(request, **data):
        global global_market
        if request.method == ('POST'):
            if check_JWT(data.get("token"), data.get('id'), key):
                for house_hold in global_household_list:
                    if house_hold._id == data.get('id'):
                        if data.get('amount') < global_market.market_buffert.content:
                            house_hold._buffert.content += data.get('amount')
                            Market.buy_from_market(
                                global_market, data.get('amount'))
                            return Response(f"SUCC {global_market.market_buffert.content}")
                        return Response(f"FAIL {global_market.market_buffert.content}")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def sell(request, **data):
        global global_market
        if request.method == ('POST'):
            if check_JWT(data.get("token"), data.get('id'), key):
                for house_hold in global_household_list:
                    if house_hold._id == data.get('id'):
                        if house_hold._blocked_status == True and int(house_hold._blocked_number_of_cykels) > 0:
                            return Response(f"Failed you are blocked from selling. Blocked for {house_hold._blocked_number_of_cykels} cycles")
                        if data.get('amount') < house_hold._buffert.content:
                            house_hold._buffert.content -= data.get('amount')
                            Market.send_to_market(
                                global_market, data.get('amount'))
                            return Response(f"You have now sold {data.get('amount')}kWh")
                        return Response(f"Failed not enough minerals!")
            return Response("Unauthorised")
        return Response("Wrong request method")

    # @rate_limited(1/10, mode='kill')  # FIX
    def change_market_size(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                global global_market
                Market.change_market_size(
                    global_market, int(request.args.get('size')))
                return Response(f"Changning market size to { request.args.get('size')}")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def block_user(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                global global_household_list
                cycle = int(request.args.get('cycle'))
                id = int(request.args.get('target'))
                if int(cycle) <= 0:
                    return Response("You need a pos int!")

                for house_hold in global_household_list:
                    if house_hold._id == id:
                        house_hold._blocked_number_of_cykels = cycle
                        house_hold._blocked_status = True
                        return Response(f"user{id} blocked for {cycle} cycles")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def remove_block(request, **data):
        if request.method == ('POST'):
            if check_JWT(data.get("token"), data.get('id'), adminKey):
                global global_household_list
                cycle = data.get('cycle')
                id = data.get('id')
                if cycle <= 0:
                    return Response("You need a pos int!")

                for house_hold in global_household_list:
                    if house_hold._id == id:
                        house_hold._blocked_number_of_cykels = cycle
                        house_hold._blocked_status = True
                        return Response(f"user{id} blocked for {cycle} cycles")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def get_house_hold_data(request, **data):
        """[summary]
        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        if request.method == ('GET'):
            global global_household_list
            if check_JWT(data.get("token"), data.get('id'), key):
                for house_hold in global_household_list:
                    if house_hold._id == int(data.get('id')):
                        if hasattr(house_hold, '_wind'):
                            Net_production = int(
                                house_hold._production) - int(house_hold._consumption)
                            resp = {house_hold._id: [{"wind": house_hold._wind, "temp": house_hold._temp, "production": house_hold._production, "consumption": house_hold._consumption,
                                                      "buffert_content": house_hold._buffert.content, "buffert_capacity": house_hold._buffert.capacity, "buffert_ratio": house_hold._ratio_to_market, "power_status": house_hold._power_status, "net_production": Net_production}]}
                        else:
                            resp = {house_hold._id: [
                                {"temp": house_hold._temp, "consumption": house_hold._consumption, "power_status": house_hold._power_status}]}
                        contents = json.dumps(resp, sort_keys=True)
                    else:
                        continue
                    return Response(contents, content_type="application/json")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def get_market_info(request, **data):
        if request.method == ('GET'):
            global global_market
            data = {"market_size": str(global_market.market_buffert.capacity)+" kWh",
                    "market_content": str(global_market.market_buffert.content)+" kwH", "market_price": str(global_market.market_price)+" öre", "recommended": str(global_market.recommended_market_price)+" öre"}
            contents = json.dumps(data, sort_keys=False)
            return Response(contents, content_type="application/json")
        return Response("Wrong request method")

    def change_market_price(request):
        if request.method == ('POST'):
            if check_JWT(request.args.get("token"), request.args.get('id'), adminKey):
                global_market.market_price = int(
                    request.args.get("market_price"))
                return Response("Market price changed")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def change_ratio_to_market(request, **data):
        if request.method == ('POST'):
            if check_JWT(data.get("token"), data.get('id'), key):
                global global_household_list

                # check if request is legit
                if int(data.get('amount')) > 100 or int(data.get('amount')) < 0:
                    return Response("You cant do that")

                for house_hold in global_household_list:
                    if house_hold._id == data.get('id') and house_hold._buffert.content > 0:
                        house_hold._ratio_to_market = int(
                            data.get('amount'))/100
                        return Response(f"Sending {data.get('amount')}% to market")
                return Response("User not found or not alode to change buffert")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def allowed_file(filename):
        """[summary]
        Dictates what file formats are allowed to upload
        Args:
            filename ([String]): [The name of the file]

        Returns:
            [Boolean]: [True if allowd, False of file format not in ALLOWED_EXTENSIONS]
        """
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def upload_file(request):
        """[summary]
            This route recives an file from an form typ file and uplodes it to the server.

        Returns:
            [redirect]: [redirects user after successfully a upload, returns error if not successfully]
        """
        if request.method == 'POST':

            if request.args.get("type"):
                UPLOAD_FOLDER = 'Database/ProfilePictures/admin'
            else:
                UPLOAD_FOLDER = 'Database/ProfilePictures/users'

            if 'file' not in request.files:
                return Response('No file part')
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return Response('No selected file')
            if file and SimulatorEndPoints.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER,
                          request.form.get('userid')+filename))
                # TODO INSERT FILE PATHE INTO USER TABLE
                upload_user_pic(request.form.get('userid') +
                                filename, request.form.get('userid'), request.args.get("type"))
                return Response("Picture successfully uploaded")
        return Response("Wrong method")

    def send_file(request):
        file_name = SimulatorEndPoints.get_pic(request)

        if request.args.get('type') == "admin":
            UPLOAD_FOLDER = 'Database/ProfilePictures/admin/'
        if request.args.get('type') == "user":
            UPLOAD_FOLDER = 'Database/ProfilePictures/users/'

        with open(UPLOAD_FOLDER+file_name[0].get("user_pic"), 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
        return Response(encoded_string)

    def get_pic(request):
        if request.method == 'GET':
            if request.args.get('type') == "admin":
                if check_JWT(request.args.get('token'), int(request.args.get('id')), adminKey):
                    file = get_user_pic(request.args.get('id'), "admin")
                    return file
            if check_JWT(request.args.get('token'), int(request.args.get('id')), key):
                file = get_user_pic(request.args.get('id'), "user")
                return file
            return Response("Unauthorised")
        return Response("Wrong request method")

    def admin_view(request):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [type]: [description]
        """
        if request.method == 'GET':
            if check_JWT(request.args.get('token'), int(request.args.get('id')), adminKey):
                data = []
                for house_hold in global_household_list:
                    if hasattr(house_hold, '_wind'):
                        Net_production = int(
                            house_hold._production) - int(house_hold._consumption)
                        data.append({"id": house_hold._id, "wind": house_hold._wind, "temp": house_hold._temp, "production": house_hold._production, "consumption": house_hold._consumption,
                                     "buffert_content": house_hold._buffert.content, "buffert_capacity": house_hold._buffert.capacity, "buffert_ratio": house_hold._ratio_to_market, "power_status": house_hold._power_status, "blackout_duration": house_hold._blackout_duration, "net_production": Net_production})
                    else:
                        data.append({"id": house_hold._id, "temp": house_hold._temp,
                                    "consumption": house_hold._consumption, "power_status": house_hold._power_status, "blackout_duration": house_hold._blackout_duration})

                contents = json.dumps(data, sort_keys=False)
                return Response(contents, content_type="application/json")
            return Response("Unauthorised")
        return Response("Wrong request method")

    def change_user_credentials(request):
        if request.method == 'POST':
            if check_JWT(request.args.get('token'), int(request.args.get('id')), adminKey):

                if request.args.get('user_name'):
                    res = change_user_info(request.args.get(
                        'target_id'), request.args.get('user_name'), request.args.get('target_row'))
                    return Response(f"{res}")

                if request.args.get('password'):
                    res = change_user_info(request.args.get(
                        'target_id'), request.args.get('password'), request.args.get('target_row'))
                    return Response(f"{res}")

                if request.args.get('email'):
                    res = change_user_info(request.args.get(
                        'target_id'), request.args.get('email'), request.args.get('target_row'))
                    return Response(f"{res}")

                if request.args.get('address') and request.args.get('zipcode'):
                    data = get_data(request.args.get('address'),
                                    request.args.get('zipcode'))
                    if len(data) == 0:
                        return Response("Address not found")
                    change_user_info(request.args.get(
                        'target_id'), [request.args.get('address'), request.args.get('zipcode')], request.args.get('target_row'))
                    return Response("Address changed")

                if request.args.get('prosumer'):
                    if request.args.get('prosumer') < 0 or request.args.get('prosumer') < 1:
                        return Response("Value not allowed")
                    change_user_info(request.args.get(
                        'target_id'), request.args.get('prosumer'), request.args.get('target_row'))
                    return Response(f"prosumer for id {request.args.get('target_id')} changed")

                if request.args.get('user_pic'):
                    responese = SimulatorEndPoints.upload_file(request)
                    return Response(str(responese))

            return Response("Unauthorised or bad request")
        return Response("Wrong request method")

    def remove_user(request):
        """[summary]

        Args:
            request ([type]): [description]

        Returns:
            [String]: [Returns 0 if no change was made. Returns 1 if change was made.]
        """
        if request.method == 'POST':
            if check_JWT(request.args.get('token'), int(request.args.get('id')), adminKey):
                if len(request.args.get('target')) == 0:
                    return Response("Pls type target id")
                res = remove_user_from_database(
                    int(request.args.get('target')))
                return Response(f"{res}")
            return Response("Unauthorised or bad request")
        return Response("Wrong request method")

    @responder
    def application(environ, start_response):
        """[summary]
            This is API written in werkzeug.

        Endpoints:
            test

        Args:
            environ ([type]): [description]
            start_response ([type]): [description]

        Returns:
            [type]: [description]
        """

        url_map = Map([
            Rule(
                '/admin/tools/change_power', endpoint='change_power'),
            Rule('/admin/tools/block_user_from_trade', endpoint='block_user'),
            Rule('/admin/tools/change_market_size',
                 endpoint="change_market_size"),
            Rule('/admin/login/username=<string:username>',
                 endpoint='admin_login'),
            Rule('/admin/tools/remove_user', endpoint='remove_user'),
            Rule('/admin/tools/view', endpoint='admin_view'),
            Rule('/admin/tools/view_power_plants',
                 endpoint='admin_view_power_plants'),
            Rule('/admin/tools/change_power_ratio',
                 endpoint='admin_change_power_ratio'),
            Rule('/admin/tools/send_to_market',
                 endpoint='admin_send_to_market'),
            Rule(
                '/buy/house_hold/prosumer/house_hold=<int:id>&amount=<int:amount>&token=<string:token>', endpoint='buy'),
            Rule(
                '/sell/house_hold/prosumer/house_hold_id=<int:id>&amount=<int:amount>&token=<string:token>', endpoint='sell'),
            Rule('/data/house_hold=<int:id>&token=<string:token>',
                 endpoint='get_house_hold_data'),
            Rule(
                '/change_buffert/house_hold=<int:id>&amount=<int:amount>&token=<string:token>', endpoint='change_buffert_to_market'),
            Rule(
                '/user/change_profile_picture', endpoint='change_profile_picture'),
            Rule('/data/get_market_data', endpoint='get_market_data'),
            Rule(
                '/register/username=<string:username>&password=<string:password>&email=<string:email>&address=<string:address>&zipcode=<string:zipcode>&prosumer=<int:prosumer>', endpoint='register'),
            Rule('/login/username=<string:username>', endpoint='login'),
            Rule('/uploader', endpoint='uploader'),
            Rule('/admin/tools/change_user_info', endpoint='change_user_info'),
            Rule('/user/get_user_pic', endpoint='get_user_pic'),
            Rule('/admin/tools/change_market_price',
                 endpoint='change_market_price')
        ])

        views = {'change_power': SimulatorEndPoints.on_change_power_plant_output,
                 'buy': SimulatorEndPoints.buy,
                 'sell': SimulatorEndPoints.sell,
                 'change_market_size': SimulatorEndPoints.change_market_size,
                 'get_house_hold_data': SimulatorEndPoints.get_house_hold_data,
                 'register': register,
                 'login': login,
                 'admin_login': admin_login,
                 'remove_user': SimulatorEndPoints.remove_user,
                 'block_user': SimulatorEndPoints.block_user,
                 'get_market_data': SimulatorEndPoints.get_market_info,
                 'change_buffert_to_market': SimulatorEndPoints.change_ratio_to_market,
                 'uploader': SimulatorEndPoints.upload_file,
                 'admin_view': SimulatorEndPoints.admin_view,
                 'get_user_pic': SimulatorEndPoints.send_file,
                 'change_user_info': SimulatorEndPoints.change_user_credentials,
                 'change_market_price': SimulatorEndPoints.change_market_price,
                 'admin_change_power_ratio': SimulatorEndPoints.change_power_plant_ratio,
                 'admin_view_power_plants': SimulatorEndPoints.view_power_plant,
                 'admin_send_to_market': SimulatorEndPoints.send_to_market}

        request = Request(environ)
        urls = url_map.bind_to_environ(environ)
        return urls.dispatch(lambda e, v: views[e](request, **v),
                             catch_http_exceptions=True)
