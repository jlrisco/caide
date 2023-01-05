import logging
import os
from lib.util import CommandEvent, CommandEventId, SensorEvent
from xdevs import get_logger
from xdevs.models import Atomic, Port

logger = get_logger(__name__, logging.DEBUG)

class VirtualNode(Atomic):
    '''Simulated sensor'''

    PHASE_INITIALIZE:str = "INITIALIZE"

    def __init__(self, name: str, base_folder: str = os.path.join('data','input','sensors_data')):
        super().__init__(name)
        # Simple attributes
        self.base_folder: str = base_folder
        self.files: list = []
        # Ports
        self.iport_cmd = Port(CommandEvent, "cmd")   # Event includes the command
        self.add_in_port(self.oport_cmd)
        self.oport_out = Port(SensorEvent, "out")   # Event includes the measurements
        self.add_out_port(self.oport_out)
        # Rest of the attributes
        name_parts: list = name.split(".")
        name_data_folder = os.path.join(self.base_folder, name_parts[-1])
        for file_entry in os.listdir(name_data_folder):
            file_path: str = os.path.join(name_data_folder, file_entry)
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
        pass

    def deltint(self):
        """DEVS internal transition function."""
        self.passivate()

    def deltext(self, e):
        self.continuef(e)
        """DEVS external transition function."""
        if self.iport_cmd.empty() is False:
            cmd: CommandEvent = self.iport_cmd.get()
            if cmd.cmd == CommandEventId.CMD_START_SIM:
                self.file_counter: int = 0
                self.reader = None
                self.current_input: SensorEvent = None
                self.next_input: SensorEvent = None
                self.update_inputs()
                self.hold_in(self.PHASE_INITIALIZE, 0.0) # TODO: This is not correct, fix it.

    def update_inputs(self):
        """Function to update the inputs."""
        while (self.current_input is None or current_input.getDate().isBefore(start)): # No se ha leído nunca la primera entrada.
            currentInput = self.get_next_input()
        next_input = self.get_next_input()

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
        if (input.getDate().isAfter(stop)):  # No quedan más datos en el intervalo de simulación.
            return None
        return input
