import mysql.connector
from mysql.connector import Error


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
        self._ratio_to_market = 0.5  # Determents how much is sent to the market default is 50%
        self._buffert = Buffert(1000, 0)

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
