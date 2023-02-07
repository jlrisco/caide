import datetime as dt
import logging
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tables as tb
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

    CMD_ACTIVATE_SENSORS = "ACTIVATE_SENSORS"
    CMD_PASSIVATE_SENSORS = "PASSIVATE_SENSORS"
    CMD_TO_H5 = "TO_H5"
    CMD_RUN_PREDICTION = "RUN_PREDICTION"
    CMD_FIX_OUTLIERS = "FIX_OUTLIERS"
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
            self.args = parts[2:]

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
            if cmd.cmd == CommandEventId.CMD_ACTIVATE_SENSORS:
                self.base_file = open(self.base_folder + "/" + self.name + ".csv", "w")    
                for pos, field in enumerate(self.fields):
                    if(pos > 0):
                        self.base_file.write(",")
                    self.base_file.write(field)
                self.base_file.write("\n")
                super().passivate(DevsCsvFile.PHASE_WRITING)
            if cmd.cmd == CommandEventId.CMD_PASSIVATE_SENSORS:
                if(self.base_folder is not None):
                    self.base_file.close()
                super().passivate()
        if (self.iport_data.empty() is False and self.phase == DevsCsvFile.PHASE_WRITING):
            data: DataEvent = self.iport_data.get()
            self.base_file.write(data.to_string() + "\n")
            super().passivate(DevsCsvFile.PHASE_WRITING)


class FarmReportService:
    """Class to generate farm reports."""

    def __init__(self, data_center_name, farm_name):
        self.data_center_name = data_center_name
        self.farm_name = farm_name
        self.base_folder = f'data/output/DataCenter/{self.farm_name}'

    def generate_prediction_report(self, now_dt):
        logger.debug("FarmReportService::generate_prediction_report()")
        self.prepare_prediction_data(now_dt)
        self.prepare_prediction_figure1()
        self.prepare_prediction_figure2()
        self.prepare_prediction_figure3()
        f = open(f'data/output/{self.data_center_name}/{self.farm_name}/farm_prediction_report.html', 'w')
        f.write(self.prepare_prediction_html_code())
        f.close()

    def prepare_prediction_data(self, now_dt):
        # Now we extract input data and predictions (filepaths are always the same):
        data_path = f'{self.base_folder}/prediction-input.h5'
        prediction_path = f'{self.base_folder}/prediction-output.h5'
        n_sensors = 17
        n_horizons = 4
        n = now_dt.strftime('%Y-%m-%d')
        with tb.open_file(prediction_path, 'r') as h5_preds, tb.open_file(data_path, 'r') as h5_data:
            timestamps = h5_preds.root.DataCenter[self.farm_name][n]._v_children.keys()
            timestamps = list(timestamps)
            self.preds = np.empty((len(timestamps), n_sensors, n_horizons))
            persistence = np.empty((len(timestamps), n_sensors, n_horizons))
            self.data = np.empty((len(timestamps), n_sensors))
            for idx, t in enumerate(timestamps):
                self.preds[idx] = h5_preds.root.DataCenter[self.farm_name][n][t][:]
                self.data[idx] = h5_data.root.DataCenter[self.farm_name][n][idx,1:]
                for hh,h in enumerate([1,11,31,61]):
                    if idx-h > 0: persistence[idx,:,hh] = h5_data.root.DataCenter[self.farm_name][n][idx-h,1:]
                    else: persistence[idx,:,hh] = np.nan
            self.sensors = h5_data.root.DataCenter[self.farm_name]._v_attrs['columns'][1:]
        self.times = [pd.to_datetime(d) for d in timestamps]

    def prepare_prediction_figure1(self):
        sensor = 0
        fig, ax = plt.subplots(2,2, figsize=(10,8),constrained_layout = True)
        fig.suptitle('Predictions and real values for sensor {} at each horizon'.format(self.sensors[sensor]), fontsize=16)
        for idx,h in enumerate(['1 min','11 min','31 min','61 min']):
            ax[idx//2,idx%2].set_title(label='h = {}'.format(h))
            ax[idx//2,idx%2].plot(self.times, self.data[:,sensor], label='simulated')
            ax[idx//2,idx%2].plot(self.times, self.preds[:,sensor,idx], label='predicted')
            ax[idx//2,idx%2].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax[idx//2,idx%2].grid()
            ax[idx//2,idx%2].legend()
            ax[idx//2,idx%2].set_ylabel('GHI $[W/m^2]$')
            ax[idx//2,idx%2].set_xlabel('Hour') #, fontsize=12)
        plt.savefig(self.base_folder + "/figure1.png", dpi=400, bbox_inches='tight')

    def prepare_prediction_figure2(self):
        horizons = {0:1,1:11,2:31,3:61}
        h = 2
        n_sensors = 17
        fig, ax = plt.subplots(6,3, figsize=(15,20),constrained_layout = True)
        fig.suptitle('Predictions and real values for each sensor (horizon {} min)'.format(horizons[h]), fontsize=16)
        for i in range(n_sensors):
            ax[i//3,i%3].set_title(label=self.sensors[i])
            ax[i//3,i%3].plot(self.times, self.data[:,i], label='truth')
            ax[i//3,i%3].plot(self.times, self.preds[:,i,h], label='preds')
            ax[i//3,i%3].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax[i//3,i%3].grid()
            ax[i//3,i%3].legend()
            ax[i//3,i%3].set_ylabel('GHI $[W/m^2]$')
            ax[i//3,i%3].set_xlabel('Hour') #, fontsize=12)
        plt.savefig(self.base_folder + "/figure2.png", dpi=400, bbox_inches='tight')

    def prepare_prediction_figure3(self):
        horizons = {0:1,1:11,2:31,3:61}
        h=1
        fig, ax = plt.subplots(6,3, figsize=(15,20),constrained_layout = True)
        fig.suptitle('Difference between predicted and real values for each sensor (horizon {} min)'.format(horizons[h]), fontsize=16)
        for i in range(17):
            ax[i//3,i%3].set_title(label=self.sensors[i])
            ax[i//3,i%3].plot(self.times, np.abs(self.preds[:,i,h] - self.data[:,i]), label='preds - truth')
            ax[i//3,i%3].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax[i//3,i%3].grid()
            ax[i//3,i%3].legend()
            ax[i//3,i%3].set_ylabel('GHI $[W/m^2]$')
            ax[i//3,i%3].set_xlabel('minutes since first prediction')
        plt.savefig(self.base_folder + "/figure3.png", dpi=400, bbox_inches='tight')
    
    def prepare_prediction_html_code(self):
        html = f'''
            <html>
                <head>
                    <title>Prediction Report</title>
                </head>
                <body>
                    <h1>Plot predictions and real data for sensor ap1</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="figure1.png" width="70%" alt="ap1 data">
                    </p>
                    <h1>Plot predictions and real data for all the sensors</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="figure2.png" width="70%" alt="ap1 data">
                    </p>
                    <h1>Difference between predicted and real values for each sensor (horizon 11 min)</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="figure3.png" width="70%" alt="ap1 data">
                    </p>
                </body>
            </html>'''
        return html

    def generate_outliers_report(self):
        logger.debug("FarmReportService::generate_outliers_report()")
        f = open(f'data/output/{self.data_center_name}/{self.farm_name}/farm_outliers_report.html', 'w')
        f.write(self.prepare_outliers_html_code())
        f.close()

    def prepare_outliers_html_code(self):
        html = f'''
            <html>
                <head>
                    <title>Outliers Report</title>
                </head>
                <body>
                    <h1>Real data for sensor ap1</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <iframe id="outlier-figure1" scrolling="no" style="border:none;" seamless="seamless" src="fig_outliers-1.html" height="525" width="100%"></iframe>
                    </p>
                    <h1>Plot model</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="fig_outliers-2.png" width="70%" alt="ap1 model">
                    </p>
                    <h1>Plot real-data vs. model anomalies</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="fig_outliers-3.png" width="70%" alt="ap1 data">
                    </p>
                    <h1>Plot real-data vs. fixed data (after interpolation)</h1>
                    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit ...</p>
                    <p style="text-align:center;">
                        <img src="fig_outliers-4.png" width="70%" alt="ap1 data">
                    </p>
                </body>
            </html>'''
        return html
