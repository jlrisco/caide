import os, time, re
import numpy as np
import pandas as pd
import tables as tb
import modelUtils, plotUtils # deep_playground
from trainUtils import HistoryCallback, DataGenerator
from sklearn.metrics import mean_squared_error, r2_score
from scipy.interpolate import griddata
import datetime as dt
#from pandas.plotting import register_matplotlib_converters


class Deployer():
    '''
    Class that encapsulates the model deployer.
    '''

    def __init__(self, work_path='..', time_gran='01m', #dset='stand_map10',
                 site='oahu', kind='10x10', scaling='stand', interp='nearest', group='/gases',
                 n_x=4, forecast_horizon=[1, 11, 31, 61],
                 #batch_size=2**5, batch_size_stateful=2**5, timestep=10, # for time awareness
                 #shuffle_data_gen=False, train_split=0.8, 
                 #test_months=['/2010/04/', '/2010/12/', '/2011/07/'],
                 #n_y=4, shift=1,# batch_size=2**8,# experiment='test',
                 #calendar_aware=False, weather_aware=False
                ):
        # For files and paths
        self.work_path = work_path
        self.time_gran = time_gran
        self.models_path = os.path.join(self.work_path, 'models', site)
        self.data_path = os.path.join(self.work_path, 'data', site, 'clean')
        self.other_path = os.path.join(self.work_path, 'data', site, 'other')
        self.dataset = '{}_{}_{}_{}.h5'.format(time_gran, kind, scaling, interp)
        self.dataset_path = os.path.join(self.data_path, self.dataset)
        self.dataset_raw = '{}_{}_{}.h5'.format(time_gran, 'flat', 'raw')
        self.dataset_raw_path = os.path.join(self.data_path, self.dataset_raw)
        #self.experiment = experiment
        self.group = group
        self.site, self.kind, self.scaling, self.interp = site, kind, scaling, interp
        # For the model
        self.n_x = n_x
        #self.n_y = n_y
        #self.shift = shift
        self.forecast_horizon = forecast_horizon
        self.initial_dt = dt.datetime(year=2010, month=3, day=18)
        with tb.open_file(self.dataset_path, mode='r') as h5_file:
            self.sensors = eval(h5_file.get_node('/2010/04/15')._v_attrs['columns'])[1:]
        self.models = modelUtils.Models(n_x=self.n_x,
                                        n_horizons=len(self.forecast_horizon),
                                        n_sensors=len(self.sensors))
        self.mod_name = '{}_{}_{}_{}_nx{:02}_{}'.format(time_gran, kind, scaling, interp, n_x, 'convLstm0')
        self.model = self.load_model(self.mod_name)

    def __idx_to_datetime(self, idx, base=None, freq=1):
        # Frequency expressed in minutes
        if base is None:
            base = self.initial_dt
        return base + dt.timedelta(minutes=freq * idx)

    def __datetime_to_idx(self, date, base=None, freq=1):
        # Frequency expressed in minutes
        if base is None:
            base = self.initial_dt
        return int((date - base).total_seconds() / (60 * freq))

    def load_model(self, mod_name):
        mod_path = os.path.join(self.models_path, mod_name, mod_name + '.h5')
        model = self.models.load_model(mod_path)
        model.mod_name = mod_name
        model.summary()
        return model

    def forecast(self, now):
        # It is assumed that now is a datetime
        # base should be the same day at the first recorded time
        id_now = self.__datetime_to_idx(now, base=now.date())
        # 1) Read 1d data for each sensor at current time (consider that 1st column is time_since_epoch)
        # 2) Standardize
        # 3) Interpolate to mesh-grid (and probably save it to a h5)
        # 4) Forecast using the new mesh-grid alongside the previous n_x - 1
        # 5) De-interpolate to obtain one value per sensor
        # 6) De-standardize
        # 7) Save result in ../data/oahu/forecasts (same structure as the input?)

if __name__ == "__main__":
    d = Deployer()
