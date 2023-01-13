import os
from xdevs.models import Coupled
from xdevs.sim import Coordinator
from xdevs import INFINITY
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

        # FOG 1
        # Sensores Internos

        sensor_ap1 = VirtualNode(name="ap1")
        sensor_ap3 = VirtualNode(name="ap3")
        db_ap1 = DevsCsvFile('ap1', ['source', 'timestamp', 'radiation'], os.path.join('data', 'output', self.name))
        db_ap3 = DevsCsvFile('ap3', ['source', 'timestamp', 'radiation'], os.path.join('data', 'output', self.name))

        # Components:
        self.add_component(generator)
        self.add_component(sensor_ap1)
        self.add_component(sensor_ap3)
        self.add_component(db_ap1)
        self.add_component(db_ap3)
        # Coupling relations:
        self.add_coupling(generator.o_cmd, sensor_ap1.iport_cmd)
        self.add_coupling(generator.o_cmd, sensor_ap3.iport_cmd)
        self.add_coupling(generator.o_cmd, db_ap1.iport_cmd)
        self.add_coupling(generator.o_cmd, db_ap3.iport_cmd)
        self.add_coupling(sensor_ap1.oport_out, db_ap1.iport_data)
        self.add_coupling(sensor_ap3.oport_out, db_ap3.iport_data)


if __name__ == "__main__":
    # Create the output directory:
    model_name: str = "main_test"
    # model_name: str = "main_test" + "_" + strftime("%Y%m%d%H%M%S", localtime())
    output_folder: str = os.path.join('data', 'output', model_name)
    os.makedirs(output_folder, exist_ok=True)
    coupled = MainTest(model_name, os.path.join(
        'data', 'input', 'services_data', 'main_test.txt'))
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
