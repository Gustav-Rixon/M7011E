import mysql.connector
from mysql.connector import Error
from werkzeug.wrappers.response import Response
from Backend.resources.Functions import calc_station
from urllib.parse import unquote
import json


class Consumer:
    """[summary]
        Consumer class
    """

    def __init__(self, id, consumption, closest_station_id, closest_station_distance, power_status):
        self._id = id
        self._consumption = consumption
        self._temp = 0
        self._closest_station_id = closest_station_id
        self._closest_station_distance = closest_station_distance
        self._power_status = 0
        self._prosumer = 0
        self._blackout_duration = 0


class Prosumer(Consumer):
    """[summary]
        Prosumer class
    """

    def __init__(self, id, consumption, closest_station_id, closest_station_distance, power_status, turbine_status):
        super().__init__(id, consumption, closest_station_id,
                         closest_station_distance, power_status)

        self._prosumer = 1
        self._wind = 0
        self._turbine_status = turbine_status
        self._production = 0
        self._blocked_status = False
        self._blocked_number_of_cykels = 0
        self._ratio_to_market = 0.0  # Determents how much is sent to the market default is 0%
        self._buffert = Buffert(1000, 0)  # TODO

    def power_check(self):
        """[summary]
            Checks if the buffert content is 0 or not.
            If buffert is empty then a prosumer gets a blackout
        """
        self._buffert.buffert_checker()
        if self._buffert.content > 0:
            self._power_status = 1
        else:
            self._power_status = 0


class PowerPlant:
    """[summary]
        Power plant class
    """

    def __init__(self, id, production, status, buffert_capacity, buffert_content):
        self._id = id
        self._production = production
        self._status = status
        self._buffert = Buffert(buffert_capacity, buffert_content)


class Buffert:
    """[summary]
        Buffert class used by outer classes to represend a buffert
    """

    def __init__(self, capacity, content):
        self.capacity = capacity
        self.content = content

    def buffert_checker(self):
        """[summary]
            Checks so that the buffert content does not exceeds the buffert capacity
        """
        if self.content > self.capacity:
            self.content = self.capacity
        if self.content == 0:  # TODO TRIGER EVENT BLACKOUT
            pass


def database_cred():
    f = open('conf/configuration.json')
    data = json.load(f)
    host = data.get("DATABASE_CONF").get("host")
    database = data.get("DATABASE_CONF").get("database")
    user = data.get("DATABASE_CONF").get("user")
    password = data.get("DATABASE_CONF").get("password")
    return mysql.connector.connect(host=host,
                                   database=database,
                                   user=user,
                                   password=password)


def create_house_holds_objects():
    """[summary]
        Creates house holds objects from the database

    Returns:
        [list]: [Two lists. One list of consumers and one list_of_prosumers]
    """

    list_of_consumer = []
    list_of_prosumer = []

    try:
        connection = database_cred()
        sql_select_Query = "select * from house_hold"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        for row in records:
            closest_station_id = row["closest_station_id"]
            user_user_id = row["user_user_id"]
            distans_to_station = row["distans_to_station"]
            prosumer = row["prosumer"]

            if prosumer == 0:
                list_of_consumer.append(Consumer(user_user_id, 0, closest_station_id,
                                                 distans_to_station, 0))
            elif prosumer == 1:
                list_of_prosumer.append(Prosumer(user_user_id, 0, closest_station_id,
                                                 distans_to_station, 0, 0))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return list_of_consumer, list_of_prosumer


def create_power_plants_objects():
    """[summary]
        Creates a power plant object from the database

    NOTE
        The system currently only supports one power plant object

    Returns:
        [list]: [A list of power plant objects]
    """

    list = []

    try:
        connection = database_cred()
        sql_select_Query = "select * from power_plant"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        for row in records:
            id = row["idpower_plant"]
            buffert = row["buffert"]
            buffert_capacety = row["buffert_capacety"]
            status = row["status"]

            list.append(PowerPlant(id, 0, status, buffert_capacety,
                                   buffert))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return list


def check_trade(list):
    """[summary]
        Checks a list of prosumer objects and checks if they are blockd from trading

    Args:
        list ([list]): [A list of prosumer objects]
    """
    for object in list:
        if object._blocked_number_of_cykels == 0:
            object._blocked_status = False
        if object._blocked_status == True and object._blocked_number_of_cykels > 0:
            object._blocked_number_of_cykels -= 1


def check(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    """[summary]
        Checks if a new user needs to be added to the simulation or if a user is removed

    Args:
        consumer_households_in_siumulation ([list]): [List of current consumers in the simulation]
        prosumer_households_in_siumulation ([list]): [List of current prosumers in the simulation]

    Returns:
        [list]: [A new list of current consumers in the simulation and current prosumers in the simulation]
    """

    check_trade(prosumer_households_in_siumulation)

    count = 0
    check = len(consumer_households_in_siumulation +
                prosumer_households_in_siumulation)
    try:
        connection = database_cred()
        sql_select_Query = "select * from house_hold"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        consumer_households_in_siumulation, prosumer_households_in_siumulation = check_prosumer_change(consumer_households_in_siumulation,
                                                                                                       prosumer_households_in_siumulation)

        for row in records:
            count += 1

        if count == check:
            print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤__NO__CHANGE__¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
            pass

        if count > check:
            print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤__CHANGE__ADDING__USER__¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
            consumer_households_in_siumulation, prosumer_households_in_siumulation = add_new_user(
                consumer_households_in_siumulation, prosumer_households_in_siumulation)

        if count < check:
            print("¤¤¤¤¤¤¤¤¤¤¤¤¤¤__CHANGE__REMOVING__USER__¤¤¤¤¤¤¤¤¤¤¤¤¤¤")
            consumer_households_in_siumulation, prosumer_households_in_siumulation = remove_user_from_simulation(
                consumer_households_in_siumulation, prosumer_households_in_siumulation)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return consumer_households_in_siumulation, prosumer_households_in_siumulation


def check_prosumer_change(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    """[summary]
        Checks if a user has changed prosumer status.

    Args:
        consumer_households_in_siumulation ([list]): [List of current consumers in the simulation]
        prosumer_households_in_siumulation ([list]): [List of current prosumers in the simulation]

    Returns:
        [list]: [A new list of current consumers in the simulation and current prosumers in the simulation]
    """
    try:
        connection = database_cred()
        sql_select_Query = "select * from user"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        for row in records:
            prosumer = row["prosumer"]
            user_id = row["user_id"]
            consumer_households_in_siumulation, prosumer_households_in_siumulation = convert_house_hold(
                consumer_households_in_siumulation, prosumer_households_in_siumulation, user_id, prosumer)

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return consumer_households_in_siumulation, prosumer_households_in_siumulation


def convert_house_hold(consumer_households_in_siumulation, prosumer_households_in_siumulation, user_id, prosumer):
    """[summary]

    Args:
        consumer_households_in_siumulation ([list]): [List of current consumers in the simulation]
        prosumer_households_in_siumulation ([list]): [List of current prosumers in the simulation]
        user_id ([int]): [id of the user]
        prosumer ([int]): [prosumer status]

    Returns:
        [list]: [A new list of current consumers in the simulation and current prosumers in the simulation]
    """
    for house_hold in consumer_households_in_siumulation:
        if house_hold._id == user_id:
            if house_hold._prosumer == prosumer:
                continue
            consumer_households_in_siumulation.remove(house_hold)
            prosumer_households_in_siumulation.append(Prosumer(house_hold._id, 0, house_hold._closest_station_id,
                                                               house_hold._closest_station_distance, 1, 0))
    for house_hold in prosumer_households_in_siumulation:
        if house_hold._id == user_id:
            if house_hold._prosumer == prosumer:
                continue
            prosumer_households_in_siumulation.remove(house_hold)
            consumer_households_in_siumulation.append(Consumer(house_hold._id, 0, house_hold._closest_station_id,
                                                               house_hold._closest_station_distance, 1))

    return consumer_households_in_siumulation, prosumer_households_in_siumulation


def add_new_user(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    """[summary]
        Adds a new user from the database to the simulation.

    Args:
        consumer_households_in_siumulation ([list]): [List of current consumers in the simulation]
        prosumer_households_in_siumulation ([list]): [List of current prosumers in the simulation]

    Returns:
        [list]: [A new list of current consumers in the simulation and current prosumers in the simulation]
    """
    list3 = consumer_households_in_siumulation + prosumer_households_in_siumulation
    try:
        connection = database_cred()
        sql_select_Query = "select * from house_hold"
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

        for row in records:
            closest_station_id = row["closest_station_id"]
            user_user_id = row["user_user_id"]
            distans_to_station = row["distans_to_station"]
            prosumer = row["prosumer"]

            if search_global_list(user_user_id, list3) == False:
                if prosumer == 0:
                    consumer_households_in_siumulation.append(Consumer(user_user_id, 0, closest_station_id,
                                                                       distans_to_station, 0))
                elif prosumer == 1:
                    prosumer_households_in_siumulation.append(Prosumer(user_user_id, 0, closest_station_id,
                                                                       distans_to_station, 0, 0))

    except Error as e:
        print("Error reading data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return consumer_households_in_siumulation, prosumer_households_in_siumulation


def remove_user_from_database(request, **data):
    """[summary]
        Takes on an request and removes that user from the database.

    Args:
        request ([WSGI request]): []

    Returns:
        [Response]: [-1 if failed, 1 if success]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('DELETE FROM user WHERE user_id=%s',
                       (data.get('user_id'),))
        connection.commit()

    except Error as e:
        print("Error deleting data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{cursor.rowcount}")


def remove_user_from_simulation(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    """[summary]
        Removes a user from the simulation

    Args:
        consumer_households_in_siumulation ([list]): [List of current consumers in the simulation]
        prosumer_households_in_siumulation ([list]): [List of current prosumers in the simulation]

    Returns:
        [list]: [A new list of current consumers in the simulation and current prosumers in the simulation]
    """
    lista = []  # list of consumers in simulator
    listb = []  # list of prosumers in simulator
    consumer_households_in_siumulation_temp = []  # list of consumers form database
    prosumer_households_in_siumulation_temp = []  # list of prosumers form database

    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor.execute('SELECT user_id, prosumer FROM user')
        records = cursor.fetchall()

        for object in records:
            if object[1] == 0:
                lista.append(object[0])
            if object[1] == 1:
                listb.append(object[0])

        for object in consumer_households_in_siumulation:
            consumer_households_in_siumulation_temp.append(object._id)
        for object in prosumer_households_in_siumulation:
            prosumer_households_in_siumulation_temp.append(object._id)

        remove1 = list(set(consumer_households_in_siumulation_temp) -
                       set(lista))
        remove2 = list(set(prosumer_households_in_siumulation_temp) -
                       set(listb))

        # If this if statment is removed you cant remove consumer if there are prosumer(s)
        if remove1 < remove2:
            prosumer_households_in_siumulation = remove_element(
                prosumer_households_in_siumulation, remove2)
        else:
            consumer_households_in_siumulation = remove_element(
                consumer_households_in_siumulation, remove1)

    except Error as e:
        print("Error selecting data from MySQL table", e)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return consumer_households_in_siumulation, prosumer_households_in_siumulation


def remove_element(list, remove):
    """[summary]

    Args:
        list ([list]): [List of objects]
        remove ([]): [What element to remove]

    Returns:
        [list]: [A new list where the element has been removed]
    """
    for object in list:
        if object._id == remove[0]:
            list.remove(object)
    return list


def register(request, **data):
    """[summary]
        Add a regesterd user to the database.

    Args:
        request ([WSGI request]): [request containing information]

    Returns:
        [Response]: [-1 if failed, 1 if succes]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor(dictionary=True)

        sql = "INSERT INTO user (user_name, password, email, address, zipcode, prosumer) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (data.get("username"), unquote(data.get("password")).replace('/\//g', "slash"), data.get(
            "email"), data.get("address"), data.get("zipcode"), data.get("prosumer"))

        cursor.execute(sql, val)
        connection.commit()
        add_house_hold(data.get("username"))

    except Error as e:
        return Response("Failed to insert into MySQL table {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{cursor.rowcount}")


def login(request, **data):
    """[summary]
        Check if user login credentials is correct

    Args:
        request ([WSGI request]): [request containing information]

    Returns:
        [Response]: [-1 if failed, 1 if succes]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT password, user_id FROM user WHERE user_name=%s', (data.get('username'),))
        records = cursor.fetchall()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{records}")


def admin_login(request, **data):
    """[summary]
        Check if admin login credentials is correct

    Args:
        request ([WSGI request]): [request containing information]

    Returns:
        [Response]: [-1 if failed, 1 if succes]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT password FROM admin WHERE user_name =%s', (data.get('username'),))
        records = cursor.fetchall()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{records}")


def add_house_hold(username):
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT user_id, prosumer, address, zipcode FROM user WHERE user_name=%s', (username,))
        records = cursor.fetchall()

        # Get GPS FOR ADDRESS
        closest_station_id, closest_station = calc_station(
            records[0]['address'], records[0]['zipcode'])

        sql = """INSERT INTO house_hold (closest_station_id, distans_to_station, user_user_id, prosumer) VALUES (%s, %s, %s, %s)"""
        val = (closest_station_id, closest_station,
               records[0]['user_id'], records[0]['prosumer'])

        cursor.execute(sql, val)
        connection.commit()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{cursor.rowcount}")


def upload_user_pic(pic_name, user_id):
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'UPDATE user SET user_pic=%s WHERE user_id=%s', (pic_name, user_id,))
        connection.commit()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{cursor.rowcount}")


def change_user_info(user_id, info, row):
    """[summary]
        Change user information in database and update simulation if required.
    Args:
        user_id ([int]): [User id]
        info ([Any]): [What to update to]
        row ([type]): [What row in the database to update]

    Returns:
        [Response]: [Returns error if failed. Else response successfully]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        if row == 'user_name':
            cursor.execute(
                'UPDATE user SET user_name=%s WHERE user_id=%s', (info, user_id,))

        if row == 'password':  # HOW???? NEED HASH + salt from frontend
            cursor.execute(
                'UPDATE user SET password=%s WHERE user_id=%s', (info, user_id,))

        if row == 'email':
            cursor.execute(
                'UPDATE user SET email=%s WHERE user_id=%s', (info, user_id,))

        if row == 'adddress+zipcode':  # HOW
            cursor.execute(
                'UPDATE user SET address=%s, zipcode=%s WHERE user_id=%s', (info[0], info[1], user_id,))

        if row == 'prosumer':
            cursor.execute(
                'UPDATE user SET prosumer=%s WHERE user_id=%s', (info, user_id,))
            cursor.execute(
                'UPDATE house_hold SET prosumer=%s WHERE user_user_id=%s', (info, user_id,))

        connection.commit()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return Response(f"{cursor}")


def get_user_pic(user_id, table):
    """[summary]
        Gets users profile picture

    Args:
        user_id ([int]): [User id]
        table ([string]): [Table target]

    Returns:
        [string]: [Filename]
    """
    try:
        connection = database_cred()
        cursor = connection.cursor()
        cursor = connection.cursor(dictionary=True)
        if table == "admin":
            cursor.execute(
                'SELECT user_pic FROM admin WHERE user_id=%s', (user_id,))

        if table == "user":
            cursor.execute(
                'SELECT user_pic FROM user WHERE user_id=%s', (user_id,))

        records = cursor.fetchall()

    except Error as e:
        print("parameterized query failed {}".format(e))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            return records


def search_global_list(id, list):
    """[summary]

    Args:
        id ([type]): [description]
        list ([type]): [description]

    Returns:
        [type]: [description]
    """
    for object in list:
        if object._id == id:
            return True
    return False


database_cred()
