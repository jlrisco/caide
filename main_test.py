import os
from xdevs.models import Coupled
from xdevs.sim import Coordinator
from xdevs import INFINITY
from lib.fog import FogServer
from lib.util import Generator
from lib.util import DevsCsvFile
from lib.edge import VirtualNode


class MainTest(Coupled):
    """Clase que implementa un modelo de la pila IoT como entidad virtual."""

    def __init__(self, name: str, commands_path: str, sensors_folder: str = os.path.join('data', 'input', 'sensors_data')):
        """Función de inicialización."""
        super().__init__(name)

        # Simulation file
        generator = Generator("Commander", commands_path)
        self.add_component(generator)

        # FOG 1
        # Sensores Internos
        sensor_names = ["ap1","ap3","ap4","ap5","ap6","ap7","dh1","dh2","dh3","dh4","dh5","dh6","dh7","dh8","dh9","dh10","dh11"]
        for sensor_name in sensor_names:
            sensor = VirtualNode(name=sensor_name)
            db = DevsCsvFile(sensor_name, ['source', 'timestamp', 'radiation'], os.path.join('data', 'output', self.name))
            self.add_component(sensor)
            self.add_component(db)
            self.add_coupling(generator.o_cmd, sensor.iport_cmd)
            self.add_coupling(generator.o_cmd, db.iport_cmd)
            self.add_coupling(sensor.oport_out, db.iport_data)
        # Main body
        fog = FogServer("FogServer01")
        self.add_component(fog)
        self.add_coupling(generator.o_cmd, fog.iport_cmd)


if __name__ == "__main__":
    # Create the output directory:
    model_name: str = "DataCenter"
    # model_name: str = "main_test" + "_" + strftime("%Y%m%d%H%M%S", localtime())
    output_folder: str = os.path.join('data', 'output', model_name)
    os.makedirs(output_folder, exist_ok=True)
    coupled = MainTest(model_name, os.path.join(
        'data', 'input', 'services_data', 'main_test.txt'))
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
