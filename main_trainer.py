import datetime
import os
import pandas as pd
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
    current_dt = start_dt
    current_day = -1
    sensor_rows = {}
    current_data = {}
    table = []
    base_folder = os.path.join('data', 'output', data_center_name, farm_name)
    h5_input = tb.open_file(os.path.join(base_folder, input_filename), 'r')
    # Initialize the row iterators        
    for sensor_name in sensor_names:
        sensor_table = h5_input.get_node(f"/{data_center_name}/{farm_name}/{sensor_name}")
        sensor_rows[sensor_name] = next(sensor_table.where(f"(timestamp >= {start_dt.timestamp()}) & (timestamp <= {stop_dt.timestamp()})"))
        current_data[sensor_name] = 0
    # Prepare the H5 output file
    h5_output = tb.open_file(os.path.join(base_folder, output_filename), 'w')
    group_farm = h5_output.create_group("/", data_center_name)
    group_farm = h5_output.create_group(group_farm, farm_name)
    # Write latitudes and longitudes        
    h5_add_lat_lon(group_farm, sensor_names, sensor_lat, sensor_lon)
    # Write means and stdevs
    h5_add_means_stdevs(group_farm, sensor_names, sensor_means, sensor_stdevs)







    current_dt = sensor_rows[sensor_names[0]]['timestamp']
    while current_dt < stop_dt:
        # Read data from sensors:
        row: list = []
        row.append(current_dt.timestamp())
        for sensor_name in sensor_names:
            row.append(sensor_rows[sensor_name]['radiation'])
        # Append the new row to the table
        table.append(row)


        # Save the table?
        aux_day = current_dt.day
        if aux_day != current_day:
            if current_day != -1:
                h5_output.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
                table = []
            current_day = aux_day
        # Read data
        for sensor_name in sensor_names:
            try:
                next(sensor_rows[sensor_name])
            except StopIteration:
                print(f"Sensor {sensor_name} has no data")
                continue





    # Loop over the time
    while current_dt < stop_dt:
        aux_day = current_dt.day
        if aux_day != current_day:
            if current_day != -1:
                # Save the table
                h5_output.create_array(group_farm, current_dt.strftime("%Y-%m-%d"), table)
                table = []
            current_day = aux_day
        # Read data from files
        for sensor_name in sensor_names:
            sensor_dt = sensor_rows[sensor_name]['timestamp']
            while sensor_dt<current_dt.timestamp():
                next(sensor_rows[sensor_name])
                sensor_dt = sensor_rows[sensor_name]['timestamp']
            current_data[sensor_name] = sensor_rows[sensor_name]['radiation']
        # Prepare the new row
        row: list = []
        row.append(current_dt.timestamp())
        for sensor_name in sensor_names:
            row.append(current_data[sensor_name])
        # Append the new row to the table
        table.append(row)
        current_dt += datetime.timedelta(seconds=step)
    # Check the last table
    if len(table) > 0:
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
    sensor_means = [369.5834609830342,371.67680280876823,370.76669098489083,374.4298641209037,376.3284942856716,375.61977942496674,370.2512986951063,371.36847690730417,377.2113228530946,370.58987227704154,374.5228818471059,375.17179612957113,376.5765075185596,371.38645481246544,375.34323650530564,374.9008210106542,371.6109395573938]
    sensor_stdevs = [347.8603522253601,351.3471034733037,348.7762834269417,355.133494051483,355.93551735948995,357.2219486117755,349.58499017577765,351.748549155852,363.10020704222654,350.4837024103112,354.85642801401656,354.72589053441334,356.31119569112786,351.57445886922625,363.0534413979577,353.1444320719626,351.12601315651744]
    # Prepare training data
    start_dt = datetime.datetime(2010, 3, 1)
    stop_dt = datetime.datetime(2010, 3, 31)
    generate_h5_file(data_center_name, farm_name, sensor_names, sensor_lat, sensor_lon, start_dt, stop_dt, 60, 'oahu.h5', 'training-input.h5')
    h5_input.close()
    # Train the model:
    models_folder=f'data/output/{data_center_name}/{farm_name}/models'
    os.makedirs(models_folder, exist_ok=True)
    trainer = Trainer(input_path=f'data/output/{data_center_name}/{farm_name}/training-input.h5', 
                      time_gran='01m',                       
                      models_folder=models_folder, 
                      server=farm_name,
                      kind='10x10', offset=0.001, scaling='stand', interp='nearest', 
                      n_x=10, forecast_horizon=[1, 11, 31, 61], first_hour = '07:30:00', last_hour='17:30:00',
                      mod_name = 'stand_map10_ts10_convLstm0_', testing = False)
    trainer.train(start_dt,stop_dt)
"""
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
