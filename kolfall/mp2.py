from multiprocessing import Process, Queue, Pipe

from flask.app import Flask
from mp1 import send_info_test
from flask import Flask

app = Flask(__name__)


# street={address}&postalcode={postalCode}
# EXAMPLE REQUEST http://127.0.0.1:5000/DATA/street=Strandv%C3%A4gen%205&postalcode=104%2040
@app.route('/DATA/street=<string:address>&postalcode=<string:zipcode>', methods=['GET'])
def get_weather_data(address, zipcode):
    parent_conn, child_conn = Pipe()
    p = Process(target=send_info_test, args=(child_conn, address, zipcode, ))
    p.start()
    string = f"Current data TEMP;WIND {parent_conn.recv()}"
    return string


if __name__ == "__main__":
    app.run()
