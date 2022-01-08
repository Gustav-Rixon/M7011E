import jwt


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


jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiaWF0IjoxNjQwODk1NTUxLCJleHAiOjE2NDA5OTU1NTF9.U1WMK8LNOYQfmN014Z06__AvdNirUdliXLAnc1ptMzE",
           "Test", algorithms=["HS256"])
