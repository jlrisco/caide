import argparse
import datetime
import os
import random
import time

from models import SingleFarm
from xdevs import INFINITY
from xdevs.sim import Coordinator

if __name__ == "__main__":
    # Get the arguments:
    parser = argparse.ArgumentParser()
    """
    parser.add_argument("--data_center_name", type=str, default="DataCenter")
    parser.add_argument("--farm_name", type=str, default="Oahu")
    parser.add_argument("--start_dt", type=str, default="2010-06-02 00:00:00")
    parser.add_argument("--stop_dt", type=str, default="2010-06-26 23:59:59")
    parser.add_argument("--db_name", type=str, default="oahu")
    parser.add_argument("--model_name", type=str, default="model")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--username", type=str, default="your_username")
    parser.add_argument("--key_path", type=str, default="your_private_key_path")
    """
    parser.add_argument("--data_center_name", type=str, default="DataCenter")
    parser.add_argument("--farm_name", type=str, default="Almeria")
    parser.add_argument("--start_dt", type=str, default="2020-03-02 00:00:00")
    parser.add_argument("--stop_dt", type=str, default="2020-03-26 23:59:59")
    parser.add_argument("--db_name", type=str, default="almeria")
    parser.add_argument("--model_name", type=str, default="model")
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--username", type=str, default="your_username")
    parser.add_argument("--key_path", type=str, default="your_private_key_path")
    cmd = parser.parse_args()
    # Create a txt file and write the arguments:
    root_data_folder = 'data'
    trainer_filename = "trainer.txt"
    simulation_filepath = os.path.join(root_data_folder, 'input', 'simulations', trainer_filename)
    with open(simulation_filepath, 'w') as f:
        f.write('DATETIME;COMMAND;ARGUMENTS\n')
        f.write(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")};CMD_TRAIN_MODEL;')
        f.write(f'{cmd.data_center_name};{cmd.farm_name};{cmd.start_dt};{cmd.stop_dt};')
        f.write(f'{cmd.db_name};{cmd.model_name};{cmd.host};{cmd.username};{cmd.key_path}\n')
    f.close()
    tic = time.time() 
    random.seed(1975)    
    coupled = SingleFarm(trainer_filename, cmd.farm_name, root_data_folder)
    coord = Coordinator(coupled)
    coord.initialize()
    coord.simulate_time(INFINITY)
    coord.exit()
    print('Simulation successful! it took {} in total'.format(time.strftime('%H:%M:%S', time.gmtime(time.time() - tic))))
