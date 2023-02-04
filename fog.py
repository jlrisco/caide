import datetime
import logging
import numpy as np
import tables as tb
import time
from xdevs import get_logger
from xdevs.models import Atomic, Port
from forecaster.src.deployer import Deployer
from util import CommandEvent, CommandEventId

logger = get_logger(__name__, logging.DEBUG)


class FarmServer(Atomic):
    """Simulated farm server"""

    def __init__(self, name: str, sensor_names: list, sensor_latitudes: list, sensor_longitudes: list, sensor_means: list, sensor_stdevs: list):
        super().__init__(name)
        self.sensor_names = sensor_names
        self.sensor_latitudes = sensor_latitudes
        self.sensor_longitudes = sensor_longitudes
        self.sensor_means = sensor_means
        self.sensor_stdevs = sensor_stdevs
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
            if cmd.cmd == CommandEventId.CMD_RUN_PREDICTION:
                logger.info(f"Fog server received command to generate prediction with arguments: {cmd.args[0:-1]} ...")
                start_dt: datetime = datetime.datetime.strptime(cmd.args[2], "%Y-%m-%d %H:%M:%S")
                stop_dt: datetime = datetime.datetime.strptime(cmd.args[3], "%Y-%m-%d %H:%M:%S")
                now_dt: datetime = datetime.datetime.strptime(cmd.args[4], "%Y-%m-%d %H:%M:%S")
                n_times: int = int(cmd.args[5])
                self.run_prediction(cmd.args[0], cmd.args[1], start_dt, stop_dt, now_dt, n_times)
                self.passivate()

    def generate_h5_file(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, step: int):
        """Generate h5 file with the data for the prediction."""
        # Initialize variables
        current_dt = start_dt
        current_day = -1
        sensor_files = {}
        current_data = {}
        table = []
        # Open files
        for sensor_name in self.sensor_names:
            sensor_files[sensor_name] = open(f"data/output/{data_center_name}/{farm_name}/{sensor_name}.csv", mode='r')
            # Read the header
            sensor_files[sensor_name].readline()
            current_data[sensor_name] = 0
        # Prepare the H5 file
        h5 = tb.open_file(f'data/output/{data_center_name}/{farm_name}/prediction-input.h5', 'w')
        group_farm = h5.create_group("/", data_center_name)
        group_farm = h5.create_group(group_farm, farm_name)
        # Write latitudes and longitudes        
        self.h5_add_lat_lon(h5, group_farm)
        # Write means and stdevs
        self.h5_add_means_stdevs(h5, group_farm)
        # Loop over the time
        while current_dt < stop_dt:
            aux_day = current_dt.day
            if aux_day != current_day:
                if current_day != -1:
                    # Save the table
                    h5.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
                    table = []
                current_day = aux_day
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
            row.append(current_dt.timestamp())
            for sensor_name in self.sensor_names:
                row.append(current_data[sensor_name])
            # Append the new row to the table
            table.append(row)
            current_dt += datetime.timedelta(seconds=step)
        # Close files
        for sensor_name in self.sensor_names:
            sensor_files[sensor_name].close()
        # Close the H5 file
        h5.close()

    def run_prediction(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, now_dt: datetime.datetime, n_times):
        forecaster = Deployer(models_folder=f'data/input/{data_center_name}/{farm_name}/models', input_path=f'data/output/{data_center_name}/{farm_name}/prediction-input.h5', output_path=f'data/output/{data_center_name}/{farm_name}/prediction-output.h5', server='Oahu', first_hour=start_dt.strftime('%H:%M:%S'), last_hour=stop_dt.strftime('%H:%M:%S'))
        tic = time.time() 
        forecaster.forecast(now=now_dt, reps=n_times)
        print('Prediction successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))

    def h5_add_lat_lon(self, h5, group_farm):
        # node_farm = h5.get_node(group_farm)
        columns = ["time_since_epoch"]
        sc_lat_map = {}
        sc_lon_map = {}
        for i in range(len(self.sensor_names)):
            columns.append(self.sensor_names[i])
            sc_lat_map[self.sensor_names[i]] = self.sensor_latitudes[i]
            sc_lon_map[self.sensor_names[i]] = self.sensor_longitudes[i]
        group_farm._v_attrs["sc_lat_map"] = sc_lat_map
        group_farm._v_attrs["sc_lon_map"] = sc_lon_map
        group_farm._v_attrs["columns"] = columns

    def h5_add_means_stdevs(self, h5, group_farm):
        sc_mean_map = {}
        sc_std_map = {}
        for i in range(len(self.sensor_names)):
            sc_mean_map[self.sensor_names[i]] = self.sensor_means[i]
            sc_std_map[self.sensor_names[i]] = self.sensor_stdevs[i]
        group_farm._v_attrs["sc_mean_map"] = sc_mean_map
        group_farm._v_attrs["sc_std_map"] = sc_std_map
