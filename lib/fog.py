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
        # Initialize variables
        current_dt = start_dt
        current_day = -1
        sensor_files = {}
        current_data = {}
        # Open files
        for sensor_name in self.sensor_names:
            sensor_files[sensor_name] = open(f"data/output/{data_center_name}/{sensor_name}.csv", mode='r')
            # Read the header
            sensor_files[sensor_name].readline()
            current_data[sensor_name] = 0
        # Prepare the H5 file
        h5 = tb.open_file('data/output/example.h5', 'w')
        group_fog = h5.create_group("/", data_center_name)
        group_fog = h5.create_group(group_fog, fog_server_name)
        # Loop over the time
        while current_dt < stop_dt:
            aux_day = current_dt.day
            if aux_day != current_day:
                current_day = aux_day
                group_day = h5.create_group(group_fog, current_dt.strftime("%Y-%m-%d"))
            # Read data from files
            for sensor_name in self.sensor_names:
                sensor_dt = datetime.datetime.strptime("1900-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
                while sensor_dt<current_dt:
                    line = sensor_files[sensor_name].readline()
                    if line != '':
                        sensor_dt = datetime.datetime.strptime(line.split(',')[1], "%Y-%m-%d %H:%M:%S")
                    else:
                        break
                if line != '':
                    current_data[sensor_name] = float(line.split(',')[2])
            # Prepare the new row
            row: list = []
            row.append(current_dt.timestamp)
            for sensor_name in self.sensor_names:
                row.append(current_data[sensor_name])
            # Append the new row to the group_day
            h5.get_node(group_fog, group_day).append(row)
            current_dt += datetime.timedelta(seconds=step)
        # Close files
        for sensor_name in self.sensor_names:
            sensor_files[sensor_name].close()
        # Close the H5 file
        h5.close()
