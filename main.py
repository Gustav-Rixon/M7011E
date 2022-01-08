from Backend import Simulator
import threading

if __name__ == "__main__":
    """[summary]

    """
    sim = Simulator.Simulator()
    #smhi = get_data_from_station()

    x = threading.Thread(target=sim.run)
    x.daemon = True
    x.start()
    from werkzeug.serving import run_simple
    run_simple('127.0.0.1', 5000, Simulator.SimulatorEndPoints.application)
