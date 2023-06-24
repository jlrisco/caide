import datetime as dt
import time
from forecaster.src.deployer import Deployer
from util import FarmReportService

if __name__ == "__main__":
    start_dt = dt.datetime.strptime("2010-06-27 00:00:00", "%Y-%m-%d %H:%M:%S")
    stop_dt = dt.datetime.strptime("2010-06-27 23:59:59", "%Y-%m-%d %H:%M:%S")
    now_dt = dt.datetime.strptime("2010-06-27 20:00:00", "%Y-%m-%d %H:%M:%S")
    n_times = 600
    farm_name = 'Oahu'
    models_folder = f'data/input/{farm_name}/models'
    # models_folder = f'data/output/DataCenter/{farm_name}/models'
    baseop_folder = f'data/output/DataCenter/{farm_name}'
    input_path = f'{baseop_folder}/prediction-input.h5'
    output_path = f'{baseop_folder}/prediction-output.h5'
    forecaster = Deployer(models_folder=models_folder, input_path=input_path, output_path=output_path, server=farm_name, first_hour=start_dt.strftime('%H:%M:%S'), last_hour=stop_dt.strftime('%H:%M:%S'))
    tic = time.time() 
    forecaster.forecast(now=now_dt, reps=n_times)
    print('Prediction successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
    report: FarmReportService = FarmReportService('DataCenter', farm_name, baseop_folder)
    report.generate_prediction_report(now_dt)
