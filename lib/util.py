import logging
import datetime as dt
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from xdevs import get_logger
from xdevs.models import Atomic, Port

logger = get_logger(__name__, logging.INFO)

class DataEvent(ABC):
    """Abstract class for data events."""

    @abstractmethod
    def to_string(self) -> str:
        """Return a string representation of the event."""
        pass

    @abstractmethod
    def parse(name: str, line: str) -> 'DataEvent':
        """Parse a string representation of the event."""
        pass

@dataclass
class SensorEvent(DataEvent):
    """A message to model events."""

    source: str = field(default_factory=str)
    timestamp: dt.datetime = field(default_factory=dt.datetime.now)
    radiation: float = field(default_factory=float)

    def to_string(self) -> str:
        """Return a string representation of the event."""
        msg: str = f"{self.source},{self.timestamp},{self.radiation}"
        return msg

    def parse(name: str, line: str) -> 'SensorEvent':
        """Parse a string representation of the event."""
        parts: list = line.split(',')
        event: SensorEvent = SensorEvent()
        event.source = name
        event.timestamp = dt.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S-10:00')
        event.radiation = float(parts[1])
        return event


class CommandEventId(Enum):
    """Allowed commands."""

    CMD_START_SIM = "START_SIM"
    CMD_STOP_SIM = "STOP_SIM"
    # CMD_FIX_OUTLIERS = "FIX_OUTLIERS"
    # CMD_FOG_REPORT = "FOG_REPORT"
    # CMD_CLOUD_REPORT = "CLOUD_REPORT"


class CommandEvent:
    """Clase para enviar mensajes del Generator al entorno de simulación."""

    def __init__(self, date: dt.datetime = None, cmd: CommandEventId = None,
                 args: str = ''):
        """Función de instanciación."""
        self.date: dt.datetime = date
        self.cmd: CommandEventId = cmd
        self.args: str = args

    def parse(self, cmdline):
        """Función que transforma una cadena de texto en CommandEvent."""
        parts: list = cmdline.split(';')
        self.date = dt.datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
        self.cmd = CommandEventId[parts[1]]
        if(len(parts) > 2):
            self.args = parts[2]

    def str(self):
        """Return a string representation of this object."""
        return self.date.strftime('%Y-%m-%d %H:%M:%S') + ";" + self.cmd.value


class Generator(Atomic):
    """Clase para emular directivas de simulación."""

    def __init__(self, name: str, commands_path: str):
        """Inicialización de la clase."""
        super().__init__(name)
        self.commands_path: str = commands_path
        self.commands: list = []
        self.cmd_counter: int = -1
        self.curr_input: CommandEvent = None
        self.next_input: CommandEvent = None
        self.o_cmd = Port(CommandEvent, "o_cmd")
        self.add_out_port(self.o_cmd)

    def initialize(self):
        """Inicialización de la simulación DEVS."""
        reader = open(self.commands_path, mode='r')
        self.commands = reader.readlines()[1:]
        self.commands = [x for x in self.commands if not x.startswith('#')]
        super().passivate()
        if (len(self.commands) > 0):  # At least we must have two commands
            self.cmd_counter = 0
            self.curr_input = self.get_next_input()
            self.next_input = None
            super().hold_in("active", 0.0)

    def exit(self):
        """Función de salida."""
        pass

    def deltint(self):
        """Función de transición interna."""
        self.next_input = self.get_next_input()
        if(self.next_input is None):
            super().passivate()
        else:
            sigma_aux = (self.next_input.date - self.curr_input.date).total_seconds()
            self.curr_input = self.next_input
            super().hold_in("active", sigma_aux)

    def deltext(self, e):
        """Función de transición externa."""
        super().passivate()

    def lambdaf(self):
        """Función de salida."""
        logger.info("%s::%s -> %s", self.name, self.o_cmd.name, self.curr_input.str())
        self.o_cmd.add(self.curr_input)

    def get_next_input(self):
        """Función que toma la siguiente entrada del archivo de comandos."""
        input: CommandEvent = None
        if (self.cmd_counter < len(self.commands)):
            input = CommandEvent()
            input.parse(self.commands[self.cmd_counter])
            self.cmd_counter += 1
        return input


class DevsCsvFile(Atomic):
    """Class to save data in csv file."""
    PHASE_WRITING:str = "WRITING"

    def __init__(self, name: str, fields: list, base_folder: str):
        """Class constructor"""
        super().__init__(name)
        self.fields: list = fields
        self.base_folder: str = base_folder
        self.iport_data: Port = Port(SensorEvent, "data")
        self.add_in_port(self.iport_data)
        self.iport_cmd = Port(CommandEvent, "cmd")
        self.add_in_port(self.iport_cmd)

    def initialize(self):
        """DEVS initialize function."""
        super().passivate()

    def exit(self):
        """DEVS exit function."""
        pass

    def lambdaf(self):
        """DEVS lambda function."""
        pass

    def deltint(self):
        """DEVS deltint function."""
        super().passivate()

    def deltext(self, e):
        """DEVS deltext function."""
        self.continuef(e)
        # Command input port                
        if self.iport_cmd.empty() is False:
            cmd: CommandEvent = self.iport_cmd.get()
            if cmd.cmd == CommandEventId.CMD_START_SIM:
                self.base_file = open(self.base_folder + "/" + self.name + ".csv", "w")    
                for pos, field in enumerate(self.fields):
                    if(pos > 0):
                        self.base_file.write(",")
                    self.base_file.write(field)
                self.base_file.write("\n")
                super().passivate(DevsCsvFile.PHASE_WRITING)
            if cmd.cmd == CommandEventId.CMD_STOP_SIM:
                if(self.base_folder is not None):
                    self.base_file.close()
                super().passivate()
        if (self.iport_data.empty() is False and self.phase == DevsCsvFile.PHASE_WRITING):
            data: DataEvent = self.iport_data.get()
            self.base_file.write(data.to_string() + "\n")
            super().passivate(DevsCsvFile.PHASE_WRITING)
