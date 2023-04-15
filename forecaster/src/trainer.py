
import os, time, re
import numpy as np
import pandas as pd
import tables as tb
from scipy.interpolate import griddata
import datetime as dt
import warnings
import forecaster.src.modelUtils as modelUtils
import forecaster.src.trainUtils as trainUtils
import argparse

class Trainer():
    '''
    Class that encapsulates the model trainer.
    Relevant parameters:
        work_path: root directory in which 'data' and 'models' directories must exist.
        dataset: name of the input dataset (h5 extension).
        server: name of the server that runs this code (eg FogServer01)
        first_hour/last_hour: first/last hour of expected data for the input
    The forecast method:
        Takes as input the 'now' parameter, a dt.datetime object that carries the date and hour of 
        the desired forecast time. It generates a h5 file in the predictions directory (if it does not exist),
        and adds a node to the file with the n_y predictions.
    Additional parameters are left in the code for testing and future work purposes.
    IMPORTANT:
        The following directory structure is needed for a proper deployment of the model (this structure may be changed in the future):
        
        |work_path
            |data
                |input
                    |input_file.h5
                |predictions
            |models
                |model_name
                    |model_name.h5
    '''
    
    def __init__(self, models_folder, input_path, output_path, time_gran='01m', #dset='stand_map10',
                 server='FogServer01', kind='10x10', offset=0.001, scaling='stand', interp='nearest', 
                 n_x=10, forecast_horizon=[1, 11, 31, 61], first_hour = '07:30:00', last_hour='17:30:00',
                 mod_name = 'stand_map10_ts10_convLstm0', testing = False                
                ):
        # For files and paths
        self.models_folder = models_folder
        self.input_path = input_path
        self.output_path = output_path
        self.time_gran = time_gran
        self.mod_name = mod_name
        # self.other_path = os.path.join(self.work_path, 'data', site, 'other')
        # self.dataset_raw = '{}_{}_{}.h5'.format(time_gran, 'flat', 'raw')
        # self.dataset_raw_path = os.path.join(self.data_path, self.dataset_raw)
        #self.experiment = experiment
        self.server = server
        self.kind, self.scaling, self.interp = kind, scaling, interp
        # For the model
        self.n_x = n_x
        self.offset = offset
        #self.n_y = n_y
        #self.shift = shift
        self.forecast_horizon = forecast_horizon
        self.initial_dt = dt.datetime(year=2010, month=3, day=20)
        with tb.open_file(self.input_path, mode='r') as h5_file:
            self.lat_map = h5_file.root.DataCenter[self.server]._v_attrs['sc_lat_map']
            self.lon_map = h5_file.root.DataCenter[self.server]._v_attrs['sc_lon_map']
            self.mean_map = h5_file.root.DataCenter[self.server]._v_attrs['sc_mean_map']
            self.std_map = h5_file.root.DataCenter[self.server]._v_attrs['sc_std_map']
            self.columns = h5_file.root.DataCenter[self.server]._v_attrs['columns']
        self.lat_map = {k:float(self.lat_map[k]) for k in self.lat_map.keys()}
        self.lon_map = {k:float(self.lon_map[k]) for k in self.lon_map.keys()}
        self.mean_map = {k:float(self.mean_map[k]) for k in self.mean_map.keys()}
        self.std_map = {k:float(self.std_map[k]) for k in self.std_map.keys()}

        self.sensor_locs = pd.DataFrame(data=[self.lon_map,self.lat_map], index=['lon','lat']).T #this asumes a 'sensor_locs extructure such as {sXX:(lat,lon),...}'
        self.sensors = list(self.columns[1:])
        self.pairs = self.__pair_sensors()
        self.first_hour = pd.to_datetime(first_hour)
        self.last_hour = pd.to_datetime(last_hour)
        
        self.models = modelUtils.Models(n_x = self.n_x, n_horizons = len(forecast_horizon), n_sensors = len(self.sensors))

        self.testing = testing

    def __idx_to_datetime(self, idx, base=None, freq=1):
        # Frequency expressed in minutes
        if base is None:
            base = self.initial_dt
        return base + dt.timedelta(hours=self.first_hour.hour, minutes=(freq * idx +self.first_hour.minute))

    def __datetime_to_idx(self, date, base=None, freq=1):
        # Frequency expressed in minutes
        if base is None:
            base = self.first_hour
        return int(((date - base).total_seconds()/60%(24*60)))

    def load_model(self, mod_name):
        mod_path = os.path.join(self.models_folder, mod_name + '.h5')
        model = self.models.load_model(mod_path)
        model.mod_name = mod_name
        # model.summary()
        return model
    
    def __pair_sensors(self):
        pairs = {}
        grid_shape = list(map(int,self.kind.split(sep='x')))
        xrange = (self.sensor_locs.lon.min(), self.sensor_locs.lon.max())
        yrange = (self.sensor_locs.lat.min(), self.sensor_locs.lat.max())
        xnew = np.linspace(xrange[0] - self.offset , xrange[1] + self.offset, grid_shape[0])
        ynew = np.linspace(yrange[0] - self.offset , yrange[1] + self.offset, grid_shape[1])
        X, Y = np.meshgrid(xnew, ynew)
        grid_points = np.stack((X.ravel(), Y.ravel())).T

        df = pd.DataFrame(columns=self.sensors, index=range(grid_shape[0]*grid_shape[1]))
        for s in self.sensors:
            for idx, point in enumerate(grid_points):
                df[s].loc[idx] = np.linalg.norm(np.array([self.sensor_locs.lon.loc[s],self.sensor_locs.lat.loc[s]]) - grid_points[idx])

        # display(df)
        for _ in range(len(self.sensors)):
            sensor = df.min().astype(float).idxmin()
            point_index = df.min(axis=1).idxmin()
            pairs[sensor] = point_index
            df.drop(sensor,axis=1, inplace=True)
            df.drop(point_index,axis=0, inplace=True)
            # print(sensor, point_index, grid_points[point_index])

        return pairs

    def interpolate(self, data, now, save_maps = False):
        # Prepare coordinates for interpolation
        grid_shape = list(map(int,self.kind.split(sep='x')))
        xrange = (self.sensor_locs.lon.min(), self.sensor_locs.lon.max())
        yrange = (self.sensor_locs.lat.min(), self.sensor_locs.lat.max())
        xnew = np.linspace(xrange[0] - self.offset , xrange[1] + self.offset, grid_shape[0])
        ynew = np.linspace(yrange[0] - self.offset , yrange[1] + self.offset, grid_shape[1])
        X, Y = np.meshgrid(xnew, ynew) 

        sensor_data = pd.DataFrame(data, columns = self.sensors)
        grid = griddata(self.sensor_locs[['lon','lat']].values, sensor_data.T, (X, Y), method='nearest').transpose((2, 0, 1))

        if save_maps:
            dtype = tb.Float64Atom()
            with tb.open_file(self.dataset_maps_path, 'a') as h5,\
                 warnings.catch_warnings() as w:
                warnings.simplefilter('ignore', tb.NaturalNameWarning)
                if 'DataCenter/{}/{:02}-{:02}-{:02}'.format(self.server,now.year,now.month,now.day) not in h5.root:
                    group = h5.create_group(where='/DataCenter/{}'.format(self.server),name='{:02}-{:02}-{:02}'.format(now.year,now.month,now.day),createparents=True)
                else: group = '/DataCenter/{}/{:02}-{:02}-{:02}'.format(self.server,now.year,now.month,now.day)
                time_stamp = '{:02}:{:02}:00'.format(now.hour,now.minute)
                if time_stamp not in h5.root[str(group).split()[0]]:
                    h5.create_carray(where=group, name=time_stamp, atom=dtype, obj=grid)

        return grid
    
    def train(self, beg_date, end_date, epochs=30, save_maps=False):
        model = self.models.model("convLstm0")
        
        new_days = pd.date_range(beg_date,end_date)

        # 1) Read new data for each sensor (consider that 1st column is time_since_epoch)
        with tb.open_file(self.input_path, 'r') as h5_data:
            shape = h5_data.root.DataCenter[self.server]['{:02}-{:02}-{:02}'.format(beg_date.year,beg_date.month,beg_date.day)][:,1:].shape
            new_data = np.empty((shape[0]*len(new_days), shape[1]))
            for idx,day in enumerate(new_days):
                new_data[idx*shape[0]:(idx+1)*shape[0]] = h5_data.root.DataCenter[self.server]['{:02}-{:02}-{:02}'.format(day.year,day.month,day.day)][:, 1:]

        # 2) Standardize
        for idx,col in enumerate(self.columns[1:]):
            new_data[...,idx] = (new_data[...,idx] - self.mean_map[col])/self.std_map[col]        
            # print(np.nanmean(data[...,idx]),mean_map[col])
            # print(np.nanstd(data[...,idx]),std_map[col])

        # 3) Interpolate to mesh-grid (and probably save it to a h5)
        grid = self.interpolate(data=new_data)
        # grid = grid.reshape(1,*grid.shape)

        bs = grid.shape[0] - (self.n_x + self.forecast_horizon[-1]) + 1

        # 4) Train the model with the new data
        # Reshape, copying slices of lenght = timestep
        X = np.empty((bs, self.n_x,*grid.shape[1:]))
        
        for i in range(bs):
            X[i] = grid[i:i + self.n_x]
        Y = np.empty((bs, len(self.forecast_horizon), *grid.shape[1:]))
        for id_h, horizon in enumerate(self.forecast_horizon):
            idx_y = [idx + self.n_x + horizon - 1 for idx in np.arange(bs)]
            Y[:, id_h, :] = grid[idx_y]
            
        log_file = os.path.join(self.models_folder, self.mod_name + '_logs.txt') 
        model.fit(x=X, y=Y,
                  epochs=epochs,
                  callbacks=[trainUtils.HistoryCallback(mod_name=model.mod_name,
                                             log_file=log_file,
                                             )],
                  use_multiprocessing=True, workers=0)
        model.save(os.path.join(self.models_folder, self.mod_name + '_updated({:02}-{:02}-{:02}).h5'.format(end_date.year,end_date.month,end_date.day)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train the model with new available data')
    parser.add_argument('model', help='Model to retrain (eg: stand_map10_ts10_convLstm0)')
    parser.add_argument('input', help='Input data file (h5 extension)')
    parser.add_argument('beg_date', help='First day of data used for training (format: yyyy/mm/day)')
    parser.add_argument('end_date', help='Last day of data used for training (format: yyyy/mm/day)')
    parser.add_argument('-epochs', default=30, help='Number of epochs')
    parser.add_argument('-wk','--work_path', default='..', help='Relative route to main directory')
    args = parser.parse_args()
    # now = pd.to_datetime(args.now[0]+' '+args.now[1])
    # now = pd.to_datetime()
    beg, end = pd.to_datetime(args.beg_date),pd.to_datetime(args.end_date)

    tic = time.time() 
    t = Trainer(work_path=args.work_path, dataset=args.input, mod_name=args.model)
    # d.forecast(now=now, reps=args.npreds)
    t.train(beg,end,int(args.epochs))
    print('Training successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
