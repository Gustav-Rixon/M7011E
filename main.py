from Backend import Simulator
from Backend.resources import GetDataFromSMHIApi
import threading

if __name__ == "__main__":
    """[summary]

    """
    sim = Simulator.Simulator()
    smhi = GetDataFromSMHIApi.get_data_from_station()
    #sim._debugmode = True
    x = threading.Thread(target=sim.run)
    x.daemon = True
    x.start()
    y = threading.Thread(target=smhi.update_data)
    y.daemon = True
    y.start()

    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, Simulator.SimulatorEndPoints.application)
