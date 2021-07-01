import errno
import glob
import json
import math
import os
import pathlib
import random
import cProfile
import pstats
import snakeviz

from algorithm import EsmamDS
from datetime import datetime

THIS_PATH = (str(pathlib.Path(__file__).parent.absolute()) + '/')

SAVE_PATH = (str(pathlib.Path(__file__).parent.absolute()) +
             '/_results_{}/'.format(datetime.now().strftime('%Y%m%d')))

DATA_PATH = str(pathlib.Path(__file__).parent.absolute()) + '/datasets/'

# Files in /datasets folder to be processed.
DB_NAMES = ['actg320']
# ... 'breast-cancer' ,'cancer','carcinoma',
# 'gbsg2','lung','melanoma','mgus2','mgus','pbc',
# 'ptc','uis','veteran','whas500']

# Algorithm parameters
PARAMS_GLOBAL = {'no_of_ants': 1000,
                 'min_size_subgroup': 0.05,
                 'no_rules_converg': 5,
                 'its_to_stagnation': 40,
                 'logistic_offset': 10}

# creates directory for saving results and logs
if not os.path.exists(os.path.dirname(SAVE_PATH)):
    try:
        os.makedirs(os.path.dirname(SAVE_PATH))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
# read the seeds
with open(THIS_PATH+'_seeds.json', 'r') as f:
    SEEDS = json.load(f)


def randomised_search_parameters():
    """ This needs doc;
    *guess* -> function to control and run standalone experiments.
    """

    print('\n>> call to {}'.format(randomised_search_parameters))
    # print('.. this call will execute a ramdomized search for parameters \
    #       configuration of the ESMAM-DS algorithm for \
    #       <sg_baseline={complement,population}>')

    dbs = ['actg320', 'breast-cancer', 'ptc']
    no_of_ants = [100, 200, 500, 1000, 3000]
    min_size_subgroup = [0.01, 0.02, 0.05, 0.1]
    no_rules_converg = [5, 10, 30]
    its_to_stagnation = [20, 30, 40, 50]
    # weigh_score = [0.25, 0.5, 0.9, 1]
    logistic_offset = [1, 3, 5, 10]

    n_pool = 0.1

    params = ['no_of_ants', 'min_size_subgroup', 'no_rules_converg',
              'its_to_stagnation', 'logistic_offset']

    pool = [(ants, size, converg, stag, log) for ants in no_of_ants
            for size in min_size_subgroup
            for converg in no_rules_converg
            for stag in its_to_stagnation
            for log in logistic_offset]
    with open(SAVE_PATH + '_pool_params.json', 'w') as f:
        json.dump(pool, f)

    sample_size = math.ceil(len(pool) * n_pool)
    print('.. pool of configurations: #{}'.format(len(pool)))
    print('.. sample size: #{}'.format(sample_size))

    # iterates over params config samples
    for i, sample in enumerate(random.sample(pool, sample_size)):

        # adjust params and select files path
        config = dict(zip(params, sample))
        csv_files = [DATA_PATH + '{}_disc.xz'.format(db) for db in dbs]
        csv_files = [f.replace('\\', '/') for f in csv_files]

        # creates directory for saving results and logs
        save_path = SAVE_PATH + 'esmamds_sample{}/'.format(i)
        if not os.path.exists(os.path.dirname(save_path)):
            try:
                os.makedirs(os.path.dirname(save_path))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(save_path + '_params.json', 'w') as f:
            json.dump(config, f)

        print('\n\n>> SAMPLE {}'.format(i))
        print('.. config params: {}'.format(list(zip(params, sample))))

        # iterates over datasets
        for file in csv_files:
            db_name = file.split('/')[-1].split('_')[0]
            print('..database: {}'.format(db_name))

            json_file = file.split('.')[0] + '_dtypes.json'
            with open(json_file, 'r') as f:
                dtypes = json.load(f)
            seeds = SEEDS[db_name]

            # run POPULATION-baseline
            sg_baseline = 'population'
            comp = 'pop'
            save_name = save_path + 'EsmamDS-{}_{}'.format(comp, db_name)
            run(file=file, dtypes=dtypes, sg_baseline=sg_baseline, seed=seeds[0], save_path=save_name,
                _save_log=True, **config)

            # run COMPLEMENT-baseline
            sg_baseline = 'complement'
            comp = 'cpm'
            save_name = save_path + 'EsmamDS-{}_{}'.format(comp, db_name)
            run(file=file, dtypes=dtypes, sg_baseline=sg_baseline, seed=seeds[0], save_path=save_name,
                _save_log=True, **config)
    return


def stats_results(sg_baseline, _it_init=0, _dbs_list=None, _save_log=False):
    """Execute a batch of ESMAMDS experiments.

    Args:
        sg_baseline: ?
        _it_init: ?
        _dbs_list: Datasets to be processed
        _save_log: ?
    """

    # print('\n>> call to <stats_results()>')
    # print('.. this call will execute the ESMAM-DS algorithm for <sg_baseline={complement,population}> on 14dbs/30exp')
    print('\n\n>>>>> ESMAM-SD_{}'.format(sg_baseline))

    if not _dbs_list:
        csv_files = [f for f in glob.glob(DATA_PATH+'*.xz')]
        csv_files = [f.replace('\\', '/') for f in csv_files]
    else:
        csv_files = [DATA_PATH+'{}_disc.xz'.format(db) for db in _dbs_list]
        csv_files = [f.replace('\\', '/') for f in csv_files]

    for file in csv_files:
        # print('\n> FILE: {}'.format(file))
        db_name = file.split('/')[-1].split('_')[0]
        # print('..database: {}'.format(db_name))

        json_file = file.split('.')[0] + '_dtypes.json'
        with open(json_file, 'r') as f:
            dtypes = json.load(f)
        seeds = SEEDS[db_name]

        for exp in range(_it_init, 1):  # statistical experiments
            # print('..exp {}'.format(exp))
            if sg_baseline == 'population':
                comp = 'pop'
            else:
                comp = 'cpm'
            save_name = SAVE_PATH + \
                'EsmamDS-{}_{}_exp{}'.format(comp, db_name, exp)

            if sg_baseline == 'complement':
                run(file=file, dtypes=dtypes, sg_baseline=sg_baseline,
                    seed=seeds[exp], save_path=save_name,
                    _save_log=_save_log, **PARAMS_GLOBAL)
            else:
                # run(file=file, dtypes=dtypes, sg_baseline=sg_baseline,
                #     seed=seeds[exp], save_path=save_name,
                #     _save_log=_save_log, **PARAMS_GLOBAL)
                # removed seed
                run(file=file, dtypes=dtypes, sg_baseline=sg_baseline,
                save_path=save_name, _save_log=_save_log, **PARAMS_GLOBAL)

        _it_init = 0

    return

#def run(file, dtypes, sg_baseline, seed, save_path, _save_log, **kwargs):
def run(file, dtypes, sg_baseline, save_path, _save_log, **kwargs):
    # ANT-MINER ALGORITHM: list of rules generator
    # esmam = EsmamDS(sg_baseline=sg_baseline, seed=seed, **kwargs)
    esmam = EsmamDS(sg_baseline=sg_baseline, **kwargs)
    esmam.read_data(file, dtypes)
    esmam.fit()
    esmam.save_results(save_path)
    if _save_log:
        esmam.save_logs(save_path)


if __name__ == '__main__':

    stats_results(sg_baseline='population', _save_log=True,
                  _it_init=0, _dbs_list=DB_NAMES)

    # pipeline for randomised search of algorithm's parameters
    # randomised_search_parameters()
