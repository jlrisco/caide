import os
import random
import tables as tb
from xdevs.models import Coupled
from xdevs.sim import Coordinator
from xdevs import INFINITY
from fog import FarmServer
from util import Generator
from util import DevsH5File
from edge import VirtualNode

class SingleFarmOahu(Coupled):
    """Clase que implementa un modelo de la pila IoT como entidad virtual."""

    def __init__(self, simulation_filename: str, root_data_folder: str = 'data'):
        """Función de inicialización."""
        super().__init__("DataCenter")

        # Simulation file
        simulation_filepath = os.path.join(root_data_folder, 'input', 'simulations', simulation_filename)
        generator = Generator("Commander", simulation_filepath)
        self.add_component(generator)

        # OAHU
        farm_name = "Oahu"
        # Basic sensors info:
        h5 = tb.open_file(os.path.join(root_data_folder, 'input', farm_name, 'sensors_data.h5'), 'r')
        info_group = h5.get_node('/', 'info')
        sensor_names: tb.Array = h5.get_node(info_group, 'sensor_names')
        sensor_names = [name.decode() for name in sensor_names]
        sensor_latitudes: tb.Array = h5.get_node(info_group, 'sensor_latitudes')
        sensor_longitudes: tb.Array = h5.get_node(info_group, 'sensor_longitudes')
        # TODO: This should eventually be computed at simulation time:
        sensor_means = [369.5834609830342,371.67680280876823,370.76669098489083,374.4298641209037,376.3284942856716,375.61977942496674,370.2512986951063,371.36847690730417,377.2113228530946,370.58987227704154,374.5228818471059,375.17179612957113,376.5765075185596,371.38645481246544,375.34323650530564,374.9008210106542,371.6109395573938]
        sensor_stdevs = [347.8603522253601,351.3471034733037,348.7762834269417,355.133494051483,355.93551735948995,357.2219486117755,349.58499017577765,351.748549155852,363.10020704222654,350.4837024103112,354.85642801401656,354.72589053441334,356.31119569112786,351.57445886922625,363.0534413979577,353.1444320719626,351.12601315651744]
        # Main fog server
        oahu = FarmServer(farm_name, sensor_names, sensor_latitudes, sensor_longitudes, sensor_means, sensor_stdevs, root_data_folder)
        self.add_component(oahu)
        self.add_coupling(generator.o_cmd, oahu.iport_cmd)
        # Sensors
        for sensor_name in sensor_names:
            sensor = VirtualNode(sensor_name, h5)
            self.add_component(sensor)
            self.add_coupling(generator.o_cmd, sensor.iport_cmd)
            self.add_coupling(sensor.oport_out, oahu.iports[sensor_name])


if __name__ == "__main__":
    # Initialize the seed of random number generator:
    random.seed(1975)    
    coupled = SingleFarmOahu("oahu.txt")
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
