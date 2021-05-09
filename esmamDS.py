import pathlib
import argparse
import glob
import json

from algorithm import EsmamDS
from datetime import datetime

parser = argparse.ArgumentParser(description='Execute Esmam-DS algorithm.')
parser.add_argument('input', default='actg320', help='The input file path')
parser.add_argument('-noa', default=1000, help='The number of ants')
parser.add_argument('-msg', default=0.05, help='Minimum subgroup size')
parser.add_argument(
    '-nrc', default=5,
    help='Number of sequentially found rules that, if equal, stops execution'
)
parser.add_argument(
    '-its', default=40,
    help='Required number of iterations rendering stagnation'
)
parser.add_argument(
    '-loo', default=10,
    help='?'
)

args = parser.parse_args()
input_path = args.input
PARAMS_GLOBAL = {'no_of_ants': args.noa,
                 'min_size_subgroup': args.msg,
                 'no_rules_converg': args.nrc,
                 'its_to_stagnation': args.its,
                 'logistic_offset': args.loo
                 }

THIS_PATH = (str(pathlib.Path(__file__).parent.absolute()) + '/')

SAVE_PATH = (str(pathlib.Path(__file__).parent.absolute()) +
             '/_results_{}/'.format(datetime.now().strftime('%Y%m%d')))

DATA_PATH = str(pathlib.Path(__file__).parent.absolute()) + '/datasets/'


def run(file, dtypes, sg_baseline, save_path, _save_log, **kwargs):
    esmam = EsmamDS(sg_baseline=sg_baseline, **kwargs)
    esmam.read_data(file, dtypes)
    esmam.fit()
    esmam.save_results(save_path)
    if _save_log:
        esmam.save_logs(save_path)


def stats_results(sg_baseline, _it_init=0, _dbs_list=None, _save_log=False):
    """Execute a ESMAMDS experiments.

    Args:
        sg_baseline: ?
        _it_init: ?
        _dbs_list: Datasets to be processed
        _save_log: ?
    """
    print('\n\n>>>>> ESMAM-SD_{}'.format(sg_baseline))

    if not _dbs_list:
        csv_files = [f for f in glob.glob(DATA_PATH+'*.xz')]
        csv_files = [f.replace('\\', '/') for f in csv_files]
    else:
        csv_files = [DATA_PATH+'{}_disc.xz'.format(db) for db in _dbs_list]
        csv_files = [f.replace('\\', '/') for f in csv_files]

    for file in csv_files:
        db_name = file.split('/')[-1].split('_')[0]

        json_file = file.split('.')[0] + '_dtypes.json'
        with open(json_file, 'r') as f:
            dtypes = json.load(f)

        for exp in range(_it_init, 1):
            if sg_baseline == 'population':
                comp = 'pop'
            else:
                comp = 'cpm'

            save_name = SAVE_PATH + \
                'EsmamDS-{}_{}_exp{}'.format(comp, db_name, exp)

            run(file=file, dtypes=dtypes, sg_baseline=sg_baseline,
                save_path=save_name, _save_log=_save_log, **PARAMS_GLOBAL)

        _it_init = 0
    return


stats_results(sg_baseline='population', _save_log=True,
              _it_init=0, _dbs_list=input_path)
