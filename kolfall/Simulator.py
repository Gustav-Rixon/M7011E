from multiprocessing import Process, Queue, Pipe
from time import sleep
from mp1 import send_info_wind, send_info_temp
from resources.Rate_limited import rate_limited


class Simulator:
    def __init__(self):
        self._wind = 1
        self._temp = 0
        self._processes = []

    def get_wind(self):
        return self._wind

    def get_processes(self):
        return self._processes

    @rate_limited(1/10, mode='kill')
    def set_wind(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_wind, args=(
            child_conn, address, zipcode, ))
        p.start()
        self._wind = parent_conn.recv()

    def get_temp(self):
        return self._temp

    @rate_limited(1/10, mode='kill')
    def set_temp(self, address, zipcode):
        parent_conn, child_conn = Pipe()
        p = Process(target=send_info_temp, args=(
            child_conn, address, zipcode, ))
        p.start()
        self._temp = parent_conn.recv()

    def run(self):
        while True:
            print("RUNNING")
            self.set_temp("Strandv%C3%A4gen%205", "104%2040")
            sleep(10)
            print(self.get_temp())
            sleep(10)


# On Windows the subprocesses will import (i.e. execute) the main module at start. You need to insert an if __name__ == '__main__': guard in the main module to avoid creating subprocesses

#set_temp(0,"Strandv%C3%A4gen%205", "104%2040")
