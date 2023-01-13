import logging
from xdevs import get_logger
from xdevs.models import Atomic, Port
from lib.util import CommandEvent

logger = get_logger(__name__, logging.DEBUG)


class FogServer(Atomic):
    """Simulated fog server"""

    def __init__(self, name: str):
        super().__init__(name)
        # Ports
        self.iport_cmd = Port(CommandEvent, "cmd")
        self.add_in_port(self.iport_cmd)

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
