import datetime
import numpy as np
import os
import tables as tb
import time
from forecaster.src.trainer import Trainer


def h5_add_lat_lon(group_farm, sensor_names, sensor_lat, sensor_lon):
    # node_farm = h5.get_node(group_farm)
    columns = ["time_since_epoch"]
    sc_lat_map = {}
    sc_lon_map = {}
    for i in range(len(sensor_names)):
        columns.append(sensor_names[i])
        sc_lat_map[sensor_names[i]] = sensor_lat[i]
        sc_lon_map[sensor_names[i]] = sensor_lon[i]
    group_farm._v_attrs["sc_lat_map"] = sc_lat_map
    group_farm._v_attrs["sc_lon_map"] = sc_lon_map
    group_farm._v_attrs["columns"] = columns

def h5_add_means_stdevs(group_farm, sensor_names, sensor_means, sensor_stdevs):
    sc_mean_map = {}
    sc_std_map = {}
    for i in range(len(sensor_names)):
        sc_mean_map[sensor_names[i]] = sensor_means[i]
        sc_std_map[sensor_names[i]] = sensor_stdevs[i]
    group_farm._v_attrs["sc_mean_map"] = sc_mean_map
    group_farm._v_attrs["sc_std_map"] = sc_std_map

def generate_h5_file(data_center_name: str, farm_name: str, sensor_names, sensor_lat, sensor_lon, start_dt: datetime.datetime, stop_dt: datetime.datetime, step: int, input_filename: str, output_filename: str):
    """Generate h5 file with the data for the training."""
    # Initialize variables
    current_dt = []
    sensor_rows = {}
    current_data = {}
    sensor_means = []
    sensor_stdevs = []
    table = []
    base_folder = os.path.join('data', 'output', data_center_name, farm_name)
    h5_input = tb.open_file(os.path.join(base_folder, input_filename), 'r')
    # Initialize the row iterators        
    for sensor_name in sensor_names:
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
    h5_output = tb.open_file(os.path.join(base_folder, output_filename), 'w')
    group_farm = h5_output.create_group("/", data_center_name)
    group_farm = h5_output.create_group(group_farm, farm_name)
    # Write latitudes and longitudes        
    h5_add_lat_lon(group_farm, sensor_names, sensor_lat, sensor_lon)
    # Write means and stdevs
    h5_add_means_stdevs(group_farm, sensor_names, sensor_means, sensor_stdevs)

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
            for sensor_name in sensor_names:
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
            for sensor_name in sensor_names:
                row.append(current_data[sensor_name])
            # Append the new row to the table
            table.append(row)
            current_dt += datetime.timedelta(seconds=step)
    except StopIteration:
        print(f'No more data on {current_dt.strftime("%Y-%m-%d %H:%M:%S")} for sensor {farm_name}/{sensor_name} in {input_filename}')        
    if len(table) > 0: # Save the current date
        print(f'Saving data for {current_dt.strftime("%Y-%m-%d")}: {len(table)} rows')
        h5_output.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
        table = []
    # Close files
    h5_input.close()
    h5_output.close()

if __name__ == "__main__":
    # Global variables
    data_center_name = 'DataCenter'
    farm_name = 'Oahu'
    h5_input = tb.open_file(f'data/input/{farm_name}/sensors_data.h5', 'r')
    info_group = h5_input.get_node('/', 'info')
    sensor_names: tb.Array = h5_input.get_node(info_group, 'sensor_names')
    sensor_names = [name.decode() for name in sensor_names]
    sensor_lat: tb.Array = h5_input.get_node(info_group, 'sensor_latitudes')
    sensor_lon: tb.Array = h5_input.get_node(info_group, 'sensor_longitudes')
    # Prepare training data
    start_dt = datetime.datetime(2010, 6, 1, 0, 0, 0)
    stop_dt = datetime.datetime(2010, 6, 28, 0, 0, 0)
    generate_h5_file(data_center_name, farm_name, sensor_names, sensor_lat, sensor_lon, start_dt, stop_dt, 60, 'oahu.h5', 'training-input.h5')
    h5_input.close()
    # Train the model:
    tic = time.time() 
    models_folder=f'data/output/{data_center_name}/{farm_name}/models'
    os.makedirs(models_folder, exist_ok=True)
    trainer = Trainer(input_path=f'data/output/{data_center_name}/{farm_name}/training-input.h5', 
                      time_gran='01m',                       
                      models_folder=models_folder, 
                      server=farm_name,
                      kind='10x10', offset=0.001, scaling='stand', interp='nearest', 
                      n_x=10, forecast_horizon=[1, 11, 31, 61], first_hour = '06:30:00', last_hour='16:30:00',
                      mod_name = 'stand_map10_ts10_convLstm0_25days', testing = False)
    trainer.train(start_dt + datetime.timedelta(days=1), stop_dt-datetime.timedelta(days=1, seconds=1))
    print('Training successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
"""
    Last 5 days: 00:01:12
    h5_filepath = 'data/output/DataCenter/Oahu/oahu_tmp.h5'
    models_folder = 'data/output'
    beg_date = '2010/03/22'
    end_date = '2010/03/23'
    epochs = '30'
    beg, end = pd.to_datetime(beg_date),pd.to_datetime(end_date)
    tic = time.time() 
    t = Trainer(input_path=h5_filepath, models_folder=models_folder)
    t.train(beg,end,int(epochs))
    print('Training successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
"""
