import datetime
import os
import random
from xdevs.models import Coupled
from xdevs.sim import Coordinator
from xdevs import INFINITY
from fog import FarmServer
from util import Generator
from util import DevsCsvFile
from edge import VirtualNode

class SingleFarmOahu(Coupled):
    """Clase que implementa un modelo de la pila IoT como entidad virtual."""

    def __init__(self, commands_filename: str, root_data_folder: str = 'data'):
        """Función de inicialización."""
        super().__init__("DataCenter")
        self.base_folder: str = os.path.join(root_data_folder, 'input', self.name)

        # Simulation file
        generator = Generator("Commander", os.path.join(root_data_folder, 'input', 'simulations', commands_filename))
        self.add_component(generator)

        # OAHU
        # Basic sensors ingfo:
        sensor_names = ["ap1","ap3","ap4","ap5","ap6","ap7","dh1","dh2","dh3","dh4","dh5","dh6","dh7","dh8","dh9","dh10","dh11"]
        sensor_latitudes = [21.31276, 21.31281, 21.31141, 21.30983, 21.30812, 21.31478, 21.31533, 21.31451, 21.31236, 21.31303, 21.31357, 21.31179, 21.31418, 21.31034, 21.31268, 21.31183, 21.31042]
        sensor_longitudes = [-158.08389, -158.08163, -158.07947, -158.08249, -158.07935, -158.07785, -158.087, -158.08534, -158.08463, -158.08505, -158.08424, -158.08678, -158.08685, -158.08675, -158.08688, -158.08554, -158.0853]
        # TODO: This should eventually be computed at simulation time:
        sensor_means = [369.5834609830342,371.67680280876823,370.76669098489083,374.4298641209037,376.3284942856716,375.61977942496674,370.2512986951063,371.36847690730417,377.2113228530946,370.58987227704154,374.5228818471059,375.17179612957113,376.5765075185596,371.38645481246544,375.34323650530564,374.9008210106542,371.6109395573938]
        sensor_stdevs = [347.8603522253601,351.3471034733037,348.7762834269417,355.133494051483,355.93551735948995,357.2219486117755,349.58499017577765,351.748549155852,363.10020704222654,350.4837024103112,354.85642801401656,354.72589053441334,356.31119569112786,351.57445886922625,363.0534413979577,353.1444320719626,351.12601315651744]
        # Main fog server
        oahu = FarmServer("Oahu", sensor_names, sensor_latitudes, sensor_longitudes, sensor_means, sensor_stdevs, self.base_folder)
        self.add_component(oahu)
        self.add_coupling(generator.o_cmd, oahu.iport_cmd)

        for sensor_name in sensor_names:
            sensor = VirtualNode(sensor_name, oahu.base_input_folder)
            db = DevsCsvFile(sensor_name, ['source', 'timestamp', 'radiation'], oahu.base_input_folder.replace('input', 'output'))
            self.add_component(sensor)
            self.add_component(db)
            self.add_coupling(generator.o_cmd, sensor.iport_cmd)
            self.add_coupling(generator.o_cmd, db.iport_cmd)
            self.add_coupling(sensor.oport_out, db.iport_data)


if __name__ == "__main__":
    # Initialize the seed of random number generator:
    random.seed(1975)
    coupled = SingleFarmOahu("oahu.txt", "data")
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
