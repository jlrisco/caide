import datetime
import logging
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import paramiko
import plotly.express as px
import seaborn as sns
import tables as tb
import time
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
from xdevs import get_logger
from xdevs.models import Atomic, Port
from forecaster.src.deployer import Deployer
from forecaster.src.trainer import Trainer
from util import CommandEvent, CommandEventId, FarmReportService, SensorEvent

logger = get_logger(__name__, logging.DEBUG)


class FarmServer(Atomic):
    """Simulated farm server"""

    def __init__(self, name: str, sensor_names: list, sensor_latitudes: list, sensor_longitudes: list, root_data_folder: str):
        super().__init__(name)
        self.sensor_names = sensor_names
        self.sensor_latitudes = sensor_latitudes
        self.sensor_longitudes = sensor_longitudes
        self.root_data_folder = root_data_folder
        # Ports
        self.iport_cmd = Port(CommandEvent, "cmd")
        self.add_in_port(self.iport_cmd)
        self.iports = {}
        for sensor_name in self.sensor_names:
            self.iports[sensor_name] = Port(SensorEvent, sensor_name)
            self.add_in_port(self.iports[sensor_name])

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
            if cmd.cmd == CommandEventId.CMD_ACTIVATE_SENSORS and cmd.args[0] == self.parent.name and cmd.args[1] == self.name:
                base_folder = os.path.join(self.root_data_folder, 'output', self.parent.name, self.name)
                os.makedirs(base_folder, exist_ok=True)
                # TODO: For the moment, we do not allow commands between the activation and the passivation of the sensors.
                # This is a serious limitation.
                self.db = tb.open_file(os.path.join(base_folder, f'{cmd.args[2]}.h5'), 'w')
                self.tables = {}
                dc_group = self.db.create_group('/', self.parent.name)
                farm_group = self.db.create_group(dc_group, self.name)
                for sensor_name in self.sensor_names:
                    self.tables[sensor_name] = self.db.create_table(farm_group, sensor_name, SensorEvent, sensor_name)
                super().passivate(CommandEventId.CMD_ACTIVATE_SENSORS.value)
            if cmd.cmd == CommandEventId.CMD_PASSIVATE_SENSORS and cmd.args[0] == self.parent.name and cmd.args[1] == self.name:
                self.db.close()
                report: FarmReportService = FarmReportService(self.parent.name, self.name, os.path.join(self.root_data_folder, 'output', self.parent.name, self.name))
                report.generate_introduction_report(self.sensor_names, self.sensor_latitudes, self.sensor_longitudes)
                super().passivate(CommandEventId.CMD_PASSIVATE_SENSORS.value)
            if cmd.cmd == CommandEventId.CMD_FIX_OUTLIERS and cmd.args[0] == self.parent.name and cmd.args[1] == self.name:
                logger.info(f"Fog server received command to fix outliers with arguments: {cmd.args[0:-1]} ...")
                sensor_name: str = cmd.args[2]
                start_dt: datetime = datetime.datetime.strptime(cmd.args[3], "%Y-%m-%d %H:%M:%S")
                stop_dt: datetime = datetime.datetime.strptime(cmd.args[4], "%Y-%m-%d %H:%M:%S")
                method: str = cmd.args[5]
                self.fix_outliers(cmd.args[0], cmd.args[1], sensor_name, start_dt, stop_dt, method, f'{cmd.args[6]}.h5')
                self.passivate(CommandEventId.CMD_FIX_OUTLIERS.value)
            if cmd.cmd == CommandEventId.CMD_TRAIN_MODEL and cmd.args[0] == self.parent.name and cmd.args[1] == self.name:
                logger.info(f"Fog server received command to train the model with arguments: {cmd.args[0:-1]} ...")
                start_dt: datetime = datetime.datetime.strptime(cmd.args[2], "%Y-%m-%d %H:%M:%S")
                stop_dt: datetime = datetime.datetime.strptime(cmd.args[3], "%Y-%m-%d %H:%M:%S")
                host = cmd.args[6]
                if host == 'localhost':
                    self.prepare_training(cmd.args[0], cmd.args[1], start_dt, stop_dt, f'{cmd.args[4]}.h5')
                    self.run_training(cmd.args[0], cmd.args[1], start_dt, stop_dt, f'{cmd.args[4]}.h5', cmd.args[5])
                else:
                    self.remote_training(cmd.args[0], cmd.args[1], start_dt, stop_dt, cmd.args[4], cmd.args[5], cmd.args[6], cmd.args[7], cmd.args[8])
                self.passivate(CommandEventId.CMD_TRAIN_MODEL.value)
            if cmd.cmd == CommandEventId.CMD_RUN_PREDICTION and cmd.args[0] == self.parent.name and cmd.args[1] == self.name:
                logger.info(f"Fog server received command to generate prediction with arguments: {cmd.args[0:-1]} ...")
                start_dt: datetime = datetime.datetime.strptime(cmd.args[2], "%Y-%m-%d %H:%M:%S")
                stop_dt: datetime = datetime.datetime.strptime(cmd.args[3], "%Y-%m-%d %H:%M:%S")
                now_dt = stop_dt
                minutes_back: int = int(datetime.timedelta.total_seconds(stop_dt - start_dt) / 60)
                self.prepare_prediction(cmd.args[0], cmd.args[1], start_dt - datetime.timedelta(days=1), stop_dt + datetime.timedelta(days=1), 60, f'{cmd.args[4]}.h5', "prediction-input.h5")
                # self.run_prediction(cmd.args[0], cmd.args[1], start_dt - datetime.timedelta(minutes=10), stop_dt + datetime.timedelta(hours=1, minutes=1), now_dt, minutes_back, "prediction-input.h5", f'{cmd.args[5]}.h5')
                self.run_prediction(cmd.args[0], cmd.args[1], datetime.datetime(start_dt.year, start_dt.month, start_dt.day), datetime.datetime(stop_dt.year, stop_dt.month, stop_dt.day, 23, 59), now_dt, minutes_back, "prediction-input.h5", f'{cmd.args[5]}.h5')
                self.passivate(CommandEventId.CMD_RUN_PREDICTION.value)
        if self.phase == CommandEventId.CMD_ACTIVATE_SENSORS.value:
            for sensor_name in self.sensor_names:
                if self.iports[sensor_name].empty() is False:
                    event: SensorEvent = self.iports[sensor_name].get()
                    new_row = self.tables[sensor_name].row
                    new_row['timestamp'] = event.timestamp
                    new_row['radiation'] = event.radiation
                    new_row.append()

    def prepare_prediction(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, step: int, input_filename: str, output_filename: str):
        """Generate h5 file with the data for the prediction."""
        # Initialize variables
        current_dt = []
        sensor_rows = {}
        current_data = {}
        sensor_means = []
        sensor_stdevs = []
        table = []
        base_folder = os.path.join(self.root_data_folder, 'output', data_center_name, farm_name)
        h5_input = tb.open_file(os.path.join(base_folder, input_filename), 'r')
        # Initialize the row iterators        
        for sensor_name in self.sensor_names:
            sensor_table = h5_input.get_node(f"/{data_center_name}/{farm_name}/{sensor_name}")
            sensor_rows[sensor_name] = next(sensor_table.where(f"(timestamp >= {start_dt.timestamp()}) & (timestamp <= {stop_dt.timestamp()})"))
            sensor_radiation = [row["radiation"] for row in sensor_table.where(f"(timestamp >= {start_dt.timestamp()}) & (timestamp <= {stop_dt.timestamp()})")]
            sensor_means.append(np.mean(sensor_radiation))
            sensor_stdevs.append(np.std(sensor_radiation))
            current_dt.append(sensor_rows[sensor_name]['timestamp'])
            current_data[sensor_name] = 0
        # Prepare the H5 output file
        h5_output = tb.open_file(os.path.join(base_folder, output_filename), 'w')
        group_farm = h5_output.create_group("/", data_center_name)
        group_farm = h5_output.create_group(group_farm, farm_name)
        # Write latitudes and longitudes        
        self.h5_add_lat_lon(group_farm)
        # Write means and stdevs
        self.h5_add_means_stdevs(group_farm, sensor_means, sensor_stdevs)
        # Loop over the time
        try:
            # Translate from timestamp to datetime
            current_dt = datetime.datetime.fromtimestamp(np.max(current_dt))
            previous_dt = current_dt
            while current_dt < stop_dt:
                if current_dt.day != previous_dt.day:
                    # Save the previous day
                    h5_output.create_array(group_farm, previous_dt.strftime("%Y-%m-%d"), table)
                    table = []
                    previous_dt = current_dt
                # Read data from files
                for sensor_name in self.sensor_names:
                    sensor_ts = sensor_rows[sensor_name]['timestamp']
                    sensor_dt = datetime.datetime.fromtimestamp(sensor_ts)
                    while sensor_dt<current_dt:
                        next(sensor_rows[sensor_name])
                        sensor_ts = sensor_rows[sensor_name]['timestamp']
                        sensor_dt = datetime.datetime.fromtimestamp(sensor_ts)
                    current_data[sensor_name] = sensor_rows[sensor_name]['radiation']
                # Prepare the new row
                row: list = []
                row.append(current_dt.timestamp())
                for sensor_name in self.sensor_names:
                    row.append(current_data[sensor_name])
                # Append the new row to the table
                table.append(row)
                current_dt += datetime.timedelta(seconds=step)
        except StopIteration:
            print(f'No more data on {current_dt.strftime("%Y-%m-%d %H:%M:%S")} for sensor {farm_name}/{sensor_name} in {input_filename}')        

        # Check the last table
        if len(table) > 0:
            h5_output.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
            table = []
        # Close files
        h5_input.close()
        h5_output.close()

    def run_prediction(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, now_dt: datetime.datetime, n_times, input_filename: str, output_filename: str):
        models_folder = os.path.join(self.root_data_folder, 'input', farm_name, 'models')
        baseop_folder = os.path.join(self.root_data_folder, 'output', data_center_name, farm_name)
        forecaster = Deployer(models_folder=models_folder, input_path=f'{baseop_folder}/{input_filename}', output_path=f'{baseop_folder}/{output_filename}', server=farm_name, first_hour=start_dt.strftime('%H:%M:%S'), last_hour=stop_dt.strftime('%H:%M:%S'))
        # tic = time.time() 
        forecaster.forecast(now=now_dt, reps=n_times)
        # print('Prediction successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
        # report: FarmReportService = FarmReportService(data_center_name, farm_name, baseop_folder)
        # report.generate_prediction_report(now_dt)

    def h5_add_lat_lon(self, group_farm):
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

    def h5_add_means_stdevs(self, group_farm, sensor_means, sensor_stdevs):
        sc_mean_map = {}
        sc_std_map = {}
        for i in range(len(self.sensor_names)):
            sc_mean_map[self.sensor_names[i]] = sensor_means[i]
            sc_std_map[self.sensor_names[i]] = sensor_stdevs[i]
        group_farm._v_attrs["sc_mean_map"] = sc_mean_map
        group_farm._v_attrs["sc_std_map"] = sc_std_map

    def prepare_training(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, input_filename: str):
        """Generate h5 file with the data for the training."""
        # Fix the interval:
        start_dt = start_dt - datetime.timedelta(days=1)
        stop_dt = stop_dt + datetime.timedelta(days=1, seconds=1)
        # Initialize variables
        current_dt = []
        sensor_rows = {}
        current_data = {}
        sensor_means = []
        sensor_stdevs = []
        table = []
        base_folder = os.path.join(self.root_data_folder, 'output', data_center_name, farm_name)
        h5_input = tb.open_file(os.path.join(base_folder, input_filename), 'r')
        # Initialize the row iterators        
        for sensor_name in self.sensor_names:
            sensor_table = h5_input.get_node(f"/{data_center_name}/{farm_name}/{sensor_name}")
            try:
                sensor_rows[sensor_name] = next(sensor_table.where(f"(timestamp >= {start_dt.timestamp()}) & (timestamp <= {stop_dt.timestamp()})"))
                sensor_radiation = [row["radiation"] for row in sensor_table.where(f"(timestamp >= {start_dt.timestamp()}) & (timestamp <= {stop_dt.timestamp()})")]
                sensor_means.append(np.mean(sensor_radiation))
                sensor_stdevs.append(np.std(sensor_radiation))
            except StopIteration:
                h5_input.close()
                print(f"No data for {farm_name}/{sensor_name} in {input_filename}")
                return
            current_dt.append(sensor_rows[sensor_name]['timestamp'])
            current_data[sensor_name] = 0
        # Prepare the H5 output file
        h5_output = tb.open_file(os.path.join(base_folder, "training-input.h5"), 'w')
        group_farm = h5_output.create_group("/", data_center_name)
        group_farm = h5_output.create_group(group_farm, farm_name)
        # Write latitudes and longitudes        
        self.h5_add_lat_lon(group_farm)
        # Write means and stdevs
        self.h5_add_means_stdevs(group_farm, sensor_means, sensor_stdevs)

        try:
            # Translate from timestamp to datetime
            current_dt = datetime.datetime.fromtimestamp(np.max(current_dt))
            previous_dt = current_dt
            # Loop over the time
            while current_dt < stop_dt:
                if current_dt.day != previous_dt.day:
                    # Save the previous day
                    print(f'Saving data for {previous_dt.strftime("%Y-%m-%d")}: {len(table)} rows')
                    h5_output.create_array(group_farm, previous_dt.strftime("%Y-%m-%d"), table)
                    table = []
                    previous_dt = current_dt
                # Read data from files
                for sensor_name in self.sensor_names:
                    sensor_ts = sensor_rows[sensor_name]['timestamp']
                    sensor_dt = datetime.datetime.fromtimestamp(sensor_ts)
                    while sensor_dt<current_dt:
                        next(sensor_rows[sensor_name])
                        sensor_ts = sensor_rows[sensor_name]['timestamp']
                        sensor_dt = datetime.datetime.fromtimestamp(sensor_ts)
                    current_data[sensor_name] = sensor_rows[sensor_name]['radiation']
                # Prepare the new row
                row: list = []
                row.append(current_dt.timestamp())
                for sensor_name in self.sensor_names:
                    row.append(current_data[sensor_name])
                # Append the new row to the table
                table.append(row)
                current_dt += datetime.timedelta(seconds=60)
        except StopIteration:
            print(f'No more data on {current_dt.strftime("%Y-%m-%d %H:%M:%S")} for sensor {farm_name}/{sensor_name} in {input_filename}')        
        if len(table) > 0: # Save the current date
            print(f'Saving data for {current_dt.strftime("%Y-%m-%d")}: {len(table)} rows')
            h5_output.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
            table = []
        # Close files
        h5_input.close()
        h5_output.close()

    def run_training(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, input_filename: str, model_name: str):
        models_folder=f'{self.root_data_folder}/output/{data_center_name}/{farm_name}/models'
        os.makedirs(models_folder, exist_ok=True)
        trainer = Trainer(input_path=f'{self.root_data_folder}/output/{data_center_name}/{farm_name}/training-input.h5', 
                        time_gran='01m',                       
                        models_folder=models_folder, 
                        server=farm_name,
                        kind='10x10', offset=0.001, scaling='stand', interp='nearest', 
                        n_x=10, forecast_horizon=[1, 11, 31, 61], first_hour = '05:00:00', last_hour='20:00:00',
                        mod_name = model_name, testing = False)
        trainer.train(start_dt, stop_dt)

    def remote_training(self, data_center_name: str, farm_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, input_filename: str, model_name: str, host: str, username: str, key_path: str):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, key_filename=key_path)
        command = f'nohup python /git/caide/main_trainer.py --data_center_name={data_center_name} --farm_name={farm_name} --start_dt={start_dt} --stop_dt={stop_dt} --db_name={input_filename} --model_name={model_name} --host={host} --username={username} --key_path={key_path} > main_trainer.log 2>&1 &'
        ssh.exec_command(command)
        ssh.close()

    def fix_outliers(self, data_center_name: str, farm_name: str, sensor_name: str, start_dt: datetime.datetime, stop_dt: datetime.datetime, method: str, input_output_filename: str):
        logger.info("Reading H5 data ...")
        base_folder = os.path.join(self.root_data_folder, 'output', data_center_name, farm_name)
        h5 = tb.open_file(os.path.join(base_folder, input_output_filename), 'r')
        sensor_table = h5.get_node(f'/{data_center_name}/{farm_name}/{sensor_name}')
        # Continue here: transform the table to dataframe
        df = pd.DataFrame.from_records(sensor_table.read_where(f"(timestamp>={start_dt.timestamp()}) & (timestamp<{stop_dt.timestamp()})"))
        # Convert the date column to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        # Save the plotly figure:
        fig0 = px.line(df, x="timestamp", y="radiation")
        fig0.write_html(f'{base_folder}/fig_outliers-1.html')

        logger.info("Preparing the model ...")
        # Change column names
        data = df.rename(columns={"timestamp": "ds", "radiation": "y"})
        model = Prophet(interval_width=0.99)
        model.fit(data)

        fig, ax = plt.subplots(2,2, figsize=(14,10))
        fig.suptitle(f'{farm_name}: outliers detection for {sensor_name}', fontsize=16)
        ax[0,0].set_title(f'{sensor_name} irradiance data')
        ax[0,0].plot(df.timestamp, df.radiation)
        if farm_name == 'Oahu':
            ax[0,0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        else:
            ax[0,0].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax[0,0].grid()
        ax[0,0].set_ylabel('GHI $[W/m^2]$')
        if farm_name == 'Oahu':
            ax[0,0].set_xlabel('Hour') #, fontsize=12)
        else:
            ax[0,0].set_xlabel('Day') #, fontsize=12)

        # Making prediction ...
        forecast = model.predict(data)
        model.plot(forecast, ax=ax[0,1])
        ax[0,1].set_title('Prediction')
        if farm_name == 'Oahu':
            ax[0,1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        else:
            ax[0,1].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax[0,1].set_ylabel('GHI $[W/m^2]$')
        if farm_name == 'Oahu':
            ax[0,1].set_xlabel('Hour') #, fontsize=12)
        else:
            ax[0,1].set_xlabel('Day') #, fontsize=12)

        # Merge actual and predicted values, show MAE and MAPE
        performance = pd.merge(data, forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], on='ds')
        performance_MAE = mean_absolute_error(performance['y'], performance['yhat'])
        logger.info(f'The MAE for the model is {performance_MAE}')
        performance_MAPE = mean_absolute_percentage_error(performance['y'], performance['yhat'])
        logger.info(f'The MAPE for the model is {performance_MAPE}')
        
        # Create an anomaly indicator. Visualize
        performance['anomaly'] = performance.apply(lambda rows: 1 if ((rows.y<rows.yhat_lower)|(rows.y>rows.yhat_upper)) else 0, axis = 1)
        num_outliers = performance['anomaly'].value_counts()[1]
        sns.scatterplot(x='ds', y='y', data=performance, hue='anomaly', ax=ax[1,0])
        sns.lineplot(x='ds', y='yhat', data=performance, color='black', ax=ax[1,0])
        ax[1,0].set_title(f'{num_outliers} outliers detected')
        if farm_name == 'Oahu':
            ax[1,0].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        else:
            ax[1,0].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax[1,0].grid()
        ax[1,0].set_ylabel('GHI $[W/m^2]$')
        if farm_name == 'Oahu':
            ax[1,0].set_xlabel('Hour') #, fontsize=12)
        else:
            ax[1,0].set_xlabel('Day') #, fontsize=12)

        
        # Compute fixed values
        df_fixed = df.copy()
        df_fixed.reset_index(inplace=True)
        idx = performance.index[performance['anomaly'] == 1].tolist()
        for id in idx:
            df_fixed.loc[id, 'radiation'] = np.nan
        df_fixed['radiation'].interpolate(method="linear", inplace=True)
        sns.scatterplot(x='timestamp', y='radiation', data=df, label='Original', ax=ax[1,1])
        sns.lineplot(x='timestamp', y='radiation', data=df_fixed, color='orange', label='Fixed', ax=ax[1,1])
        ax[1,1].set_title(f'Outliers fixed')
        if farm_name == 'Oahu':
            ax[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        else:
            ax[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
        ax[1,1].grid()
        ax[1,1].set_ylabel('GHI $[W/m^2]$')
        if farm_name == 'Oahu':
            ax[1,1].set_xlabel('Hour') #, fontsize=12)
        else:
            ax[1,1].set_xlabel('Day') #, fontsize=12)


        fig.savefig(f'{base_folder}/{farm_name}-outliers.png', dpi=400, bbox_inches='tight')        
        h5.close()
        # Generate the report
        # report: FarmReportService = FarmReportService(data_center_name, farm_name, base_folder)
        # report.generate_outliers_report()
