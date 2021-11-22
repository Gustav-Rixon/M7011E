import logging
import threading
import time
from multiprocessing import Process, Queue, Pipe
from flask.app import Flask
from mp1 import send_info_temp, send_info_wind
from Simulator import Simulator
from flask import Flask

app = Flask(__name__)


# EXAMPLE REQUEST http://127.0.0.1:5000/DATA/temp/street=Strandv%C3%A4gen%205&postalcode=104%2040
@app.route('/DATA/temp/street=<string:address>&postalcode=<string:zipcode>', methods=['GET'])
def get_weather_data_temp(address, zipcode):
    parent_conn, child_conn = Pipe()
    p = Process(target=send_info_temp, args=(child_conn, address, zipcode, ))
    p.start()
    string = f"Current data for address:{address}, zipcode:{zipcode} TEMP {parent_conn.recv()}"
    return string


# EXAMPLE REQUEST http://127.0.0.1:5000/DATA/wind/street=Strandv%C3%A4gen%205&postalcode=104%2040
@app.route('/DATA/wind/street=<string:address>&postalcode=<string:zipcode>', methods=['GET'])
def get_weather_data_wind(address, zipcode):
    parent_conn, child_conn = Pipe()
    p = Process(target=send_info_wind, args=(child_conn, address, zipcode, ))
    p.start()
    string = f"Current data for address:{address}, zipcode:{zipcode} WIND {parent_conn.recv()}"
    return string


if __name__ == "__main__":
    x = threading.Thread(target=Simulator.run)
    x.start()
    app.run()
