import datetime
import logging
import tables as tb
from xdevs import get_logger
from xdevs.models import Atomic, Port
from lib.util import CommandEvent, CommandEventId, SensorEvent

logger = get_logger(__name__, logging.DEBUG)


class FogServer(Atomic):
    """Simulated fog server"""

    def __init__(self, name: str, sensor_names: list):
        super().__init__(name)
        self.sensor_names = sensor_names
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
            if cmd.cmd == CommandEventId.CMD_TO_H5:
                logger.info(f"Fog server received command to generate the H5 file with arguments: {cmd.args[0:-1]} ...")
                start_dt: datetime = datetime.datetime.strptime(cmd.args[2], "%Y-%m-%d %H:%M:%S")
                stop_dt: datetime = datetime.datetime.strptime(cmd.args[3], "%Y-%m-%d %H:%M:%S")
                step = int(cmd.args[4])
                self.generate_h5_file(cmd.args[0], cmd.args[1], start_dt, stop_dt, step)
                self.passivate()

    def generate_h5_file(self, data_center_name: str, fog_server_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, step: int):
        """Generate h5 file with the data for the prediction."""
        # TODO: Continue here
        current_dt = start_dt
        sensor_files = {}
        for sensor_name in self.sensor_names:
            sensor_files[sensor_name] = open(f"data/output/{data_center_name}/{fog_server_name}/{sensor_name}.csv", mode='r')
        while current_dt < stop_dt:

            current_dt += datetime.timedelta(seconds=step)
