from multiprocessing import Process, Queue, Pipe
from mp1 import send_info_wind, send_info_temp

class Simulator:
    def __init__(self):
        self._wind = 0
        self._temp = 0
    
    # getter method
    def get_wind(self):
        return self._wind
    
    # setter method
    def set_wind(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_wind, args=(child_conn, address, zipcode, ))
        p.start()
        self._wind = parent_conn.recv()

    def get_temp(self):
        return self._temp
        
    def set_temp(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_temp, args=(child_conn, address, zipcode, ))
        p.start()
        self._temp = parent_conn.recv()


    
raj = Simulator()
  
# setting the age using setter
raj.set_wind("Strandvägen 5", "104 40")
raj.set_temp("Strandvägen 5", "104 40")
  
# retrieving age using getter
print(raj.get_wind())
print(raj.get_temp())

while True:
    raj.set_wind("Strandvägen 5", "104 40")
    print(raj.get_wind())
