from os import remove
from time import sleep
import mysql.connector
from mysql.connector import Error
from werkzeug.wrappers.response import Response
import mp1


class Consumer:
    def __init__(self, id, consumption, closest_station_id, closest_station_distance, power_status):
        self._id = id
        self._consumption = consumption
        self._temp = 0
        self._closest_station_id = closest_station_id
        self._closest_station_distance = closest_station_distance
        self._power_status = 1


class Prosumer(Consumer):
    def __init__(self, id, consumption, closest_station_id, closest_station_distance, power_status, turbine_status):
        super().__init__(id, consumption, closest_station_id,
                         closest_station_distance, power_status)
        self._wind = 0
        self._turbine_status = turbine_status
        self._production = 0
        self._blocked_status = False
        self._blocked_number_of_cykels = 0
        self._ratio_to_market = 0.5  # Determents how much is sent to the market default is 50%
        self._buffert = Buffert(1000, 0)  # TODO

    def power_check(self):
        self._buffert.buffert_checker()
        if self._buffert.content > 0:
            self._power_status = 1
        else:
            self._power_status = 0


class PowerPlant:
    def __init__(self, id, production, status, buffert_capacity, buffert_content):
        self._id = id
        self._production = production
        self._status = status
        self._buffert = Buffert(buffert_capacity, buffert_content)


class Buffert:
    def __init__(self, capacity, content):
        self.capacity = capacity
        self.content = content

    # Sadly you cant have more content then capacity
    def buffert_checker(self):
        if self.content > self.capacity:
            self.content = self.capacity
        if self.content == 0:  # TODO TRIGER EVENT BLACKOUT
            pass


def create_house_holds_objects():

    list_of_consumer = []
    list_of_prosumer = []

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')
        sql_select_Query = "select * from house_hold"
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
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

    list = []

    myconn = mysql.connector.connect(
        host="localhost", user="root", passwd="", database="m7011e")
    cur = myconn.cursor()

    try:
        cur.execute("select * from power_plant")
        result = cur.fetchall()
        num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        print(field_names)

        for value in result:
            list.append(PowerPlant(value[0], 0, value[3], value[2],
                                   value[1]))

        myconn.commit()
    except:
        myconn.rollback()
    myconn.close()

    return list


def check_trade(list):
    for object in list:
        if object._blocked_number_of_cykels == 0:
            object._blocked_status = False
        if object._blocked_status == True and object._blocked_number_of_cykels > 0:
            object._blocked_number_of_cykels -= 1


def checktest(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    """[Checks if a new user needs to be added to the simulation or if a user is removed]

    Args:
        current_list ([list]): [a list of all the current households in the simulation]

    Returns:
        [type]: [description]
    """

    check_trade(prosumer_households_in_siumulation)

    count = 0
    check = len(consumer_households_in_siumulation +
                prosumer_households_in_siumulation)
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')
        sql_select_Query = "select * from house_hold"
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()

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


def add_new_user(consumer_households_in_siumulation, prosumer_households_in_siumulation):
    list3 = consumer_households_in_siumulation + prosumer_households_in_siumulation
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')
        sql_select_Query = "select * from house_hold"
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
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


# TODO REMOVE FROM SIM
def remove_user_from_database(request, **data):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
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
    lista = []  # list of consumers in simulator
    listb = []  # list of prosumers in simulator
    consumer_households_in_siumulation_temp = []  # list of consumers form database
    prosumer_households_in_siumulation_temp = []  # list of prosumers form database

    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
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
    for object in list:
        if object._id == remove[0]:
            list.remove(object)
    return list


# TODO SOLV ERROR MASSAGE
# TODO REJECT SAME USERNAME
def register(request, **data):
    """[Checks if object id is in list]

    Args:
        id ([int]): [id to search for]
        list ([list]): [list of objects to search through]

    Returns:
        [String]: [1 if inserted, -1 if not inserted]
    """
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)

        sql = """INSERT INTO user (user_name, password, email, address, zipcode, prosumer) VALUES (%s, %s, %s, %s, %s, %s)"""
        val = (data.get("username"), data.get("password"), data.get(
            "email"), data.get("address"), data.get("zipcode"), data.get("prosumer"))
        cursor.execute(sql, val)
        # records = cursor.commit()
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
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor()
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
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


# TODO ADD ADMIN TABLE IN DATABASE
def admin_login(request, **data):
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor()
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT password FROM admin_table WHERE admin =%s', (data.get('username'),))
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
        connection = mysql.connector.connect(host='localhost',
                                             database='m7011e',
                                             user='root',
                                             password='')

        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor()
        # MySQLCursorDict creates a cursor that returns rows as dictionaries
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT user_id, prosumer, address, zipcode FROM user WHERE user_name=%s', (username,))
        records = cursor.fetchall()

        # Get GPS FOR ADDRESS
        closest_station_id, closest_station = mp1.calc_station(
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


def search_global_list(id, list):
    """[Checks if object id is in list]

    Args:
        id ([int]): [id to search for]
        list ([list]): [list of objects to search through]

    Returns:
        [Boolean]: [True if found, false if not found]
    """
    for object in list:
        if object._id == id:
            return True
    return False
