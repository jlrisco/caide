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
        self.iport_ap1 = Port(CommandEvent, "ap1")
        self.add_in_port(self.iport_ap1)
        self.iport_ap3 = Port(CommandEvent, "ap3")
        self.add_in_port(self.iport_ap3)
        