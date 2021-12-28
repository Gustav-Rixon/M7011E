# TODO use WERKZEUG :(
import logging
import threading
import time
from multiprocessing import Process, Queue, Pipe
from flask.app import Flask
from mp1 import send_info_temp, send_info_wind
from Simulator import Simulator, Exporter
from flask import Flask, json, jsonify
from Simulator import global_household_list
from resources.GetDataFromExApi import get_data_from_station

app = Flask(__name__)


# EXAMPLE REQUEST http://127.0.0.1:5000/DATA/wind/street=Strandv%C3%A4gen%205&postalcode=104%2040
# TODO ASK DATABASE FOR INFORMATION ABOUT CLOSEST STATION ID AND DISTANCE
# WORKS IF MOVED TO Simulator.py
@app.route('/DATA/wind/street=<string:address>&postalcode=<string:zipcode>', methods=['GET'])
def get_test(address, zipcode):
    global global_household_list
    parent_conn, child_conn = Pipe()
    p = Process(target=send_info_wind, args=(child_conn, address, zipcode, ))
    p.start()
    response = app.response_class(
        response=json.dumps(parent_conn.recv()),
        status=200,
        mimetype='application/json'
    )
    print("##########")
    print(global_household_list)
    print("##########")
    return response
    # response = f"Current data for address:{address}, zipcode:{zipcode} WIND {parent_conn.recv()}"
    # return jsonify({'address', {address},
    #                'zipcode', "test"})


# http://127.0.0.1:5000/DATA/test/street=Strandv%C3%A4gen%205&postalcode=104%2040
@app.route('/DATA/test/street=<string:address>&postalcode=<string:zipcode>', methods=['GET'])
def get_test2(address, zipcode):
    parent_conn, child_conn = Pipe()
    p = Process(target=Exporter.export,
                args=(child_conn, ))
    p.start()

    for household in parent_conn.recv():
        print(json.dumps(household.id))
        print(json.dumps(household.wind))
        print(json.dumps(household.temp))
        print(json.dumps(household.consumption))

    response = app.response_class(
        response=json.dumps(parent_conn.recv()),
        status=200,
        mimetype='application/json'
    )
    print(response)
    return response


if __name__ == "__main__":
    # sim = Simulator()
    # sim.setupSim()
    # x = threading.Thread(target=sim.run)
    # x.start()
    sim = Simulator()
    smhi = get_data_from_station()
    sim.setupSim

    x = threading.Thread(target=sim.run)
    x.daemon = True
    x.start()
    y = threading.Thread(target=smhi.update_data)
    y.daemon = True
    y.start()
    # sim.run()  # Main thred
    app.run()
