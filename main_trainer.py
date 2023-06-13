import pandas as pd
import time
from forecaster.src.trainer import Trainer

if __name__ == "__main__":
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


