import mysql.connector


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


def create_house_holds_objects():

    list = []

    myconn = mysql.connector.connect(
        host="localhost", user="root", passwd="", database="m7011e")
    cur = myconn.cursor()

    try:
        cur.execute("select * from house_hold")
        result = cur.fetchall()
        num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        print(field_names)

        for value in result:
            list.append(Household(value[6], None, None, None,
                                  value[0], value[2], None, None, None))

        myconn.commit()
    except:
        myconn.rollback()
    myconn.close()

    return list


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
