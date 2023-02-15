import datetime
import logging
import tables as tb
from util import CommandEvent, CommandEventId, SensorEvent
from xdevs import get_logger
from xdevs.models import Atomic, Port

logger = get_logger(__name__, logging.INFO)

class VirtualNode(Atomic):
    '''Simulated sensor'''

    PHASE_NEXT_DATA:str = "NEXT_DATA"

    def __init__(self, name: str, dc_name: str, farm_name: str, h5: tb.File):
        super().__init__(name)
        self.dc_name: str = dc_name
        self.farm_name: str = farm_name
        data_group: tb.Group = h5.get_node("/", "data")
        self.table: tb.Table = h5.get_node(data_group, name)
        # Ports
        self.iport_cmd = Port(CommandEvent, "cmd")   # Event includes the command
        self.add_in_port(self.iport_cmd)
        self.oport_out = Port(SensorEvent, "out")   # Event includes the measurements
        self.add_out_port(self.oport_out)

    def initialize(self):
        """Initialization function."""
        self.passivate()

    def exit(self):
        """Exit function."""
        pass

    def lambdaf(self):
        """DEVS output function."""
        sensor_event: SensorEvent = SensorEvent()
        sensor_event.timestamp = self.current_input['timestamp']
        sensor_event.radiation = self.current_input['radiation']
        self.oport_out.add(sensor_event)

    def deltint(self):
        """DEVS internal transition function."""
        current_datetime = datetime.datetime.fromtimestamp(self.current_input['timestamp'])
        if current_datetime.day != self.current_day:
            logger.info(f"Sensor {self.name}: Processing data from {current_datetime.strftime('%Y-%m-%d')} ...")
            self.current_day = current_datetime.day
        current_timestamp = self.current_input['timestamp']
        try:
            next_input = next(self.current_input)
            sigma_aux: float = next_input['timestamp'] - current_timestamp
            self.hold_in(self.PHASE_NEXT_DATA, sigma_aux)
        except StopIteration:
            # There is no more data for this sensor
            self.passivate()

    def deltext(self, e):
        self.continuef(e)
        """DEVS external transition function."""
        if self.iport_cmd.empty() is False:
            cmd: CommandEvent = self.iport_cmd.get()
            # TODO: Check if the command is for this sensor
            if cmd.cmd == CommandEventId.CMD_ACTIVATE_SENSORS and cmd.args[0] == self.dc_name and cmd.args[1] == self.farm_name:
                if (self.name == "sensor1"):
                    print("We are at Almeria")
                start = cmd.date.timestamp()
                self.current_day:int = -1
                self.current_input = next(self.table.where(f'(timestamp >= {start})'))
                sigma_aux: float = self.current_input['timestamp'] - start
                self.hold_in(self.PHASE_NEXT_DATA, sigma_aux)
            if cmd.cmd == CommandEventId.CMD_PASSIVATE_SENSORS and cmd.args[0] == self.dc_name and cmd.args[1] == self.farm_name:
                self.passivate()
