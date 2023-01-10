import datetime
import logging
import os
from lib.util import CommandEvent, CommandEventId, SensorEvent
from xdevs import get_logger
from xdevs.models import Atomic, Port

logger = get_logger(__name__, logging.INFO)

class VirtualNode(Atomic):
    '''Simulated sensor'''

    PHASE_NEXT_DATA:str = "NEXT_DATA"

    def __init__(self, name: str, sensors_folder: str = os.path.join('data','input','sensors_data')):
        super().__init__(name)
        # Simple attributes
        self.sensors_folder: str = sensors_folder
        self.files: list = []
        # Ports
        self.iport_cmd = Port(CommandEvent, "cmd")   # Event includes the command
        self.add_in_port(self.iport_cmd)
        self.oport_out = Port(SensorEvent, "out")   # Event includes the measurements
        self.add_out_port(self.oport_out)
        # Rest of the attributes
        name_parts: list = name.split(".")
        name_sensors_folder = os.path.join(self.sensors_folder, name_parts[-1])
        for file_entry in os.listdir(name_sensors_folder):
            file_path: str = os.path.join(name_sensors_folder, file_entry)
            if os.path.isfile(file_path):
                self.files.append(file_path)
        '''
        TODO: Se asume que los ficheros se organizarán en orden
        por fecha, y que al menos hay un fichero. Esto
        convendría mejorarlo, pero como vamos a incorporar el
        formato H5, puede que no sea necesario.
        '''
        self.files.sort()

    def initialize(self):
        """Initialization function."""
        self.passivate()

    def exit(self):
        """Exit function."""
        pass

    def lambdaf(self):
        """DEVS output function."""
        logger.debug("lambdaf: %s", self.current_input.to_string())
        self.oport_out.add(self.current_input)

    def deltint(self):
        """DEVS internal transition function."""
        if (self.next_input is None):
            self.passivate()
        else:
            sigma_aux: float = (self.next_input.timestamp - self.current_input.timestamp).total_seconds()
            self.hold_in(self.PHASE_NEXT_DATA, sigma_aux)
            self.current_input = self.next_input
            self.next_input = self.get_next_input()

    def deltext(self, e):
        self.continuef(e)
        """DEVS external transition function."""
        if self.iport_cmd.empty() is False:
            cmd: CommandEvent = self.iport_cmd.get()
            if cmd.cmd == CommandEventId.CMD_START_SIM:
                self.start = cmd.date
                self.stop = datetime.datetime(9999, 1, 1, 0, 0, 0)
                self.file_counter: int = 0
                self.reader = None
                self.current_input: SensorEvent = None
                self.next_input: SensorEvent = None
                self.update_inputs()
                sigma_aux: float = (self.current_input.timestamp - self.start).total_seconds()
                self.hold_in(self.PHASE_NEXT_DATA, sigma_aux)
            if cmd.cmd == CommandEventId.CMD_STOP_SIM:
                self.stop = cmd.date
                self.next_input = None
                self.reader.close()
                self.passivate()

    def update_inputs(self):
        """Function to update the inputs."""
        while ((self.current_input is None) or (self.current_input.timestamp < self.start)): # No se ha leído nunca la primera entrada.
            self.current_input = self.get_next_input()
        self.next_input = self.get_next_input()

    def get_next_input(self):
        """Function to get the next input."""
        input: SensorEvent = None
        # Se abre reader por primera vez:
        if self.reader is None:
            if self.file_counter < len(self.files):
                self.reader = open(self.files[self.file_counter], 'r')
                self.file_counter += 1
                self.reader.readline()  # Nos saltamos la cabecera
            else:  # No quedan ficheros
                return None
        line: str = self.reader.readline()
        if (line==''):  # Hemos llegado al final del fichero
            if self.file_counter < len(self.files):
                self.reader = open(self.files[self.file_counter], 'r')
                self.file_counter += 1
                self.reader.readline()  # Nos saltamos la cabecera
                line = self.reader.readline()
            else:  # No quedan ficheros
                return None
        input = SensorEvent.parse(self.name, line)
        if (input.timestamp > self.stop):  # No quedan más datos en el intervalo de simulación.
            return None
        return input
