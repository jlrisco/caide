import os
import random
import tables as tb
import time
from xdevs.models import Coupled
from xdevs.sim import Coordinator
from xdevs import INFINITY
from fog import FarmServer
from util import Generator
from edge import VirtualNode

class SingleFarm(Coupled):
    """Clase que implementa un modelo de la pila IoT como entidad virtual."""

    def __init__(self, simulation_filename: str, farm_name: str, root_data_folder: str = 'data'):
        """Función de inicialización."""
        super().__init__("DataCenter")

        # Simulation file
        simulation_filepath = os.path.join(root_data_folder, 'input', 'simulations', simulation_filename)
        generator = Generator("Commander", simulation_filepath)
        self.add_component(generator)

        # Basic sensors info:
        self.h5s = tb.open_file(os.path.join(root_data_folder, 'input', farm_name, 'sensors_data.h5'), 'r')
        info_group = self.h5s.get_node('/', 'info')
        sensor_names: tb.Array = self.h5s.get_node(info_group, 'sensor_names')
        sensor_names = [name.decode() for name in sensor_names]
        sensor_latitudes: tb.Array = self.h5s.get_node(info_group, 'sensor_latitudes')
        sensor_longitudes: tb.Array = self.h5s.get_node(info_group, 'sensor_longitudes')
        # Main fog server
        farm = FarmServer(farm_name, sensor_names, sensor_latitudes, sensor_longitudes, root_data_folder)
        self.add_component(farm)
        self.add_coupling(generator.o_cmd, farm.iport_cmd)
        # Sensors
        for sensor_name in sensor_names:
            sensor = VirtualNode(sensor_name, self.name, farm_name, self.h5s)
            self.add_component(sensor)
            self.add_coupling(generator.o_cmd, sensor.iport_cmd)
            self.add_coupling(sensor.oport_out, farm.iports[sensor_name])

    def exit(self):
        """Función de finalización."""
        self.h5s.close()


class SeveralFarms(Coupled):
    """Clase que implementa un modelo de la pila IoT como entidad virtual."""

    def __init__(self, simulation_filename: str, farm_names: list, root_data_folder: str = 'data'):
        """Función de inicialización."""
        super().__init__("DataCenter")
        self.farm_names = farm_names

        # Simulation file
        simulation_filepath = os.path.join(root_data_folder, 'input', 'simulations', simulation_filename)
        generator = Generator("Commander", simulation_filepath)
        self.add_component(generator)

        self.h5s = {}
        for farm_name in farm_names:
            # Basic sensors info:
            self.h5s[farm_name] = tb.open_file(os.path.join(root_data_folder, 'input', farm_name, 'sensors_data.h5'), 'r')
            info_group = self.h5s[farm_name].get_node('/', 'info')
            sensor_names: tb.Array = self.h5s[farm_name].get_node(info_group, 'sensor_names')
            sensor_names = [name.decode() for name in sensor_names]
            sensor_latitudes: tb.Array = self.h5s[farm_name].get_node(info_group, 'sensor_latitudes')
            sensor_longitudes: tb.Array = self.h5s[farm_name].get_node(info_group, 'sensor_longitudes')
            # Main fog server
            farm = FarmServer(farm_name, sensor_names, sensor_latitudes, sensor_longitudes, root_data_folder)
            self.add_component(farm)
            self.add_coupling(generator.o_cmd, farm.iport_cmd)
            # Sensors
            for sensor_name in sensor_names:
                sensor = VirtualNode(sensor_name, self.name, farm_name, self.h5s[farm_name])
                self.add_component(sensor)
                self.add_coupling(generator.o_cmd, sensor.iport_cmd)
                self.add_coupling(sensor.oport_out, farm.iports[sensor_name])

    def exit(self):
        """Función de finalización."""
        for farm_name in self.farm_names:
            self.h5s[farm_name].close()


if __name__ == "__main__":
    # Initialize the seed of random number generator:
    tic = time.time() 
    random.seed(1975)    
    coupled = SeveralFarms("two-farms.txt", ["Oahu", "Almeria"])
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
    print('Simulation successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
