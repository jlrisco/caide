import os, time, re
import numpy as np
import pandas as pd
import tables as tb
from scipy.interpolate import griddata
import datetime as dt
import warnings
import forecaster.src.modelUtils as modelUtils
import argparse

class Deployer():
    '''
    Class that encapsulates the model deployer.
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
            sensor = df.min(axis=0).astype(float).idxmin()
            point_index = df.min(axis=1).astype(float).idxmin()
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
   
    def forecast(self, now, save_maps = False, return_data=False, reps=1):
        tic = time.time()
        model = self.load_model(mod_name = self.mod_name)
        # It is assumed that now is a datetime
        # base should be the same day at the first recorded time
        
        for r in range(reps):
            
            id_now = self.__datetime_to_idx(now)
            if id_now < self.n_x or id_now > self.__datetime_to_idx(self.last_hour) - self.forecast_horizon[-1]:
                x = self.first_hour + dt.timedelta(minutes=self.n_x)
                y = self.last_hour - dt.timedelta(minutes=self.forecast_horizon[-1])
                print('Unable to forecast at times before {:02}:{:02} and after {:02}:{:02}'.format(x.hour,x.minute,y.hour,y.minute))
                return
            # Not sure how to handle the shift

            # 1) Read 1d data for each sensor at current time (consider that 1st column is time_since_epoch)
            with tb.open_file(self.input_path, 'r') as h5_data:
                data = np.array(h5_data.root.DataCenter[self.server]['{:02}-{:02}-{:02}'.format(now.year,now.month,now.day)][id_now - self.n_x:id_now, 1:])

            # 2) Standardize
            for idx,col in enumerate(self.columns[1:]):
                data[:,idx] = (data[:,idx] - self.mean_map[col])/self.std_map[col]        
                # print(np.nanmean(data[...,idx]),mean_map[col])
                # print(np.nanstd(data[...,idx]),std_map[col])

            # 3) Interpolate to mesh-grid (and probably save it to a h5)
            grid = self.interpolate(data=data, now=now, save_maps=save_maps)
            grid = grid.reshape(1,*grid.shape)
            
            # 4) Forecast using the new mesh-grid alongside the previous n_x - 1    
            grid_pred = model.predict_on_batch(grid)

            # 5) De-interpolate to obtain one value per sensor
            grid_shape = list(map(int,self.kind.split(sep='x')))
            grid_pred_ = grid_pred.reshape(len(self.forecast_horizon), grid_shape[0]*grid_shape[1])
            pred_data = np.array([grid_pred_[:,self.pairs[sensor]] for sensor in self.sensors])
            
            # 6) De-standardize
            for idx,col in enumerate(self.columns[1:]):
                pred_data[idx] = (pred_data[idx] * self.std_map[col]) + self.mean_map[col]

            # Testing
            if self.testing:
                if return_data: return data, pred_data
                return grid, grid_pred

            # 7) Save result in ../data/predictions (same structure as the input?)
            dtype = tb.Float32Atom()
            mode = 'w' if r==0 else 'a'
            with tb.open_file(self.output_path, mode) as h5_out,\
                warnings.catch_warnings() as w:
                warnings.simplefilter('ignore', tb.NaturalNameWarning)
                if 'DataCenter/{}/{:02}-{:02}-{:02}'.format(self.server,now.year,now.month,now.day) not in h5_out.root:
                    group = h5_out.create_group(where='/DataCenter/{}'.format(self.server),name='{:02}-{:02}-{:02}'.format(now.year,now.month,now.day),createparents=True)
                else: group = '/DataCenter/{}/{:02}-{:02}-{:02}'.format(self.server,now.year,now.month,now.day)
                time_stamp = '{:02}:{:02}:00'.format(now.hour,now.minute)
                if time_stamp not in h5_out.root[str(group).split()[0]]:
                    h5_out.create_carray(where=group, name=time_stamp, atom=dtype, obj=pred_data)
                h5_out.root.DataCenter[self.server]._v_attrs['columns'] = self.columns[1:]
            now = now - dt.timedelta(minutes=1)
                    
        return 'Prediction successful, it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic)))
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate data predictions for the given timestamps.')
    parser.add_argument('server', help='Server name in which the model is deployed (eg: FogServer01)')
    parser.add_argument('input', help='Input data file (h5 extension)')
    parser.add_argument('now', nargs=2, help='Timestamp from which predictions are made (format: yyyy/mm/day hh:mm)')
    parser.add_argument('-n','--npreds', type=int,default=1 ,help='Number of successive predictions for the N minutes following \'now\'')
    parser.add_argument('-wk','--work_path', default='..', help='Relative route to main directory')
    parser.add_argument('-fh','--first_hour', default='07:30:00', help='First hour of input data (format: hh:mm:ss)')
    parser.add_argument('-lh','--last_hour', default='17:30:00', help='Last hour of input data (format: hh:mm:ss)')
    args = parser.parse_args()
    now = pd.to_datetime(args.now[0]+' '+args.now[1])
    # now = pd.to_datetime()

    tic = time.time() 
    d = Deployer(work_path=args.work_path, dataset=args.input, server=args.server, 
                 first_hour=args.first_hour, last_hour=args.last_hour)
    d.forecast(now=now, reps=args.npreds)
    print('Prediction successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
