import glob
import json
import pathlib
import os
import errno

from algorithm import EsmamDS

THIS_PATH = str(pathlib.Path(__file__).parent.absolute())+'/'
SAVE_PATH = str(pathlib.Path(__file__).parent.absolute())+'/_results/'
DATA_PATH = str(pathlib.Path(__file__).parent.absolute()) + '/datasets/'
DB_NAMES = ['actg320','breast-cancer','cancer','carcinoma','gbsg2','lung','melanoma','mgus2','mgus','pbc','ptc','uis','veteran','whas500']

# creates directory for saving results and logs
if not os.path.exists(os.path.dirname(SAVE_PATH)):
    try:
        os.makedirs(os.path.dirname(SAVE_PATH))
    except OSError as exc: # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
# read the seeds
with open(THIS_PATH+'_seeds.json', 'r') as f:
    SEEDS = json.load(f)


def stats_results(sg_baseline, _it_init=0, _dbs_list=None, _save_log=False):

    print('\n>> call to <stats_results()>')
    print('.. this call will execute the ESMAM-DS algorithm for <sg_baseline={complement,population}> on 14dbs/30exp')
    print('\n\n>>>>> ESMAM-SD_{}'.format(sg_baseline))

    if not _dbs_list:
        csv_files = [f for f in glob.glob(DATA_PATH+'*.xz')]
        csv_files = [f.replace('\\', '/') for f in csv_files]
    else:
        csv_files = [DATA_PATH+'{}_disc.xz'.format(db) for db in _dbs_list]
        csv_files = [f.replace('\\', '/') for f in csv_files]

    for file in csv_files:
        print('\n> FILE: {}'.format(file))
        db_name = file.split('/')[-1].split('_')[0]
        print('..database: {}'.format(db_name))

        json_file = file.split('.')[0] + '_dtypes.json'
        with open(json_file, 'r') as f:
            dtypes = json.load(f)
        seeds = SEEDS[db_name]

        for exp in range(_it_init, 30):  # statistical experiments
            print('..exp {}'.format(exp))
            if sg_baseline == 'population': comp = 'pop'
            else: comp = 'cpm'
            save_name = SAVE_PATH + 'EsmamDS-{}_{}_exp{}'.format(comp, db_name, exp)

            run(file=file, dtypes=dtypes, sg_baseline=sg_baseline, seed=seeds[exp], save_path=save_name, _save_log=_save_log)

        _it_init = 0

    return


def run(file, dtypes, sg_baseline, seed, save_path, _save_log):
    # ANT-MINER ALGORITHM: list of rules generator
    esmam = EsmamDS(sg_baseline=sg_baseline, seed=seed)
    esmam.read_data(file, dtypes)
    esmam.fit()
    esmam.save_results(save_path)
    if _save_log:
        esmam.save_logs(save_path)


if __name__ == '__main__':
    stats_results(sg_baseline='complement', _save_log=True, _it_init=0, _dbs_list=None)
    stats_results(sg_baseline='population', _save_log=True, _it_init=0, _dbs_list=None)
