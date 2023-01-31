import logging
import datetime
from xdevs import get_logger
from xdevs.models import Atomic, Port
from lib.util import CommandEvent, CommandEventId, SensorEvent

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
            if cmd.cmd == CommandEventId.CMD_RUN_PREDICTION:
                logger.info(f"Fog server received command to run prediction with arguments: {cmd.args} ...")
                # TODO: Complete this:
                self.run_prediction(cmd.args[0], cmd.args[1], cmd.args[2], int(cmd.args[3]))
                self.passivate()

    def run_prediction(self, data_center_name: str, fog_server_name: str, dt: datetime.datetime, reps: int):
        """Run prediction for a given data center."""
        logger.info(f"Running prediction for data center: {data_center_name}")
