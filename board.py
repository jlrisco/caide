# Let's create a data frame with three lists of data

import pandas as pd
import tables as tb
import numpy as np
import datetime

sensor_names = ["ap1","ap3","ap4","ap5","ap6","ap7","dh1","dh2","dh3","dh4","dh5","dh6","dh7","dh8","dh9","dh10","dh11"]
sensor_latitudes = [21.31276, 21.31281, 21.31141, 21.30983, 21.30812, 21.31478, 21.31533, 21.31451, 21.31236, 21.31303, 21.31357, 21.31179, 21.31418, 21.31034, 21.31268, 21.31183, 21.31042]
sensor_longitudes = [-158.08389, -158.08163, -158.07947, -158.08249, -158.07935, -158.07785, -158.087, -158.08534, -158.08463, -158.08505, -158.08424, -158.08678, -158.08685, -158.08675, -158.08688, -158.08554, -158.0853]

# Create the dataframe with the three lists
d = {'sensor_name': sensor_names, 'sensor_latitude': sensor_latitudes, 'sensor_longitude': sensor_longitudes}
df = pd.DataFrame(d)
df = df.astype({"sensor_name": str, "sensor_latitude": float, "sensor_longitude": float})
print(df)

# Let's write this information into a H5 file
df.to_hdf('sensor_locations.h5', key='/DataCenter/Oahu', mode='w')

# I don't like the way the data frame is saved in the H5 file
# Let's read the H5 file and save it in a different way
h5file = tb.open_file('sensor_locations.h5', mode='w')
dc_group= h5file.create_group('/', 'DataCenter', 'Main data center')
farm_group= h5file.create_group(dc_group, 'Oahu', 'Oahu Farm')
h5file.create_array(farm_group, 'sensor_names', sensor_names, 'Sensor names')
h5file.create_array(farm_group, 'sensor_latitudes', np.array(sensor_latitudes), 'Sensor latitudes')
h5file.create_array(farm_group, 'sensor_longitudes', np.array(sensor_longitudes), 'Sensor longitudes')
h5file.close()

# Let's read some rows from the H5 output file
h5file = tb.open_file('data/output/DataCenter/Oahu/prediction-input.h5', mode='r')
table = h5file.get_node('/DataCenter/Oahu', '2010-03-22')
row = table[-1]
print(datetime.datetime.fromtimestamp(row[0]))
row = table[-2]
print(datetime.datetime.fromtimestamp(row[0]))
h5file.close()