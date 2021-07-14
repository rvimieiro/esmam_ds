import json
from algorithm import EsmamDS

def execute(sg_baseline, input_file, output_file,
            parameters, _it_init=0, _save_log=False):
    """Execute a ESMAMDS experiments.

    Args:
        sg_baseline: ?
        _it_init: ?
        _dbs_list: Datasets to be processed
        _save_log: ?
    """
    db_name = input_file.split('/')[-1].split('_')[0]
    json_file = input_file.split('.')[0] + '_dtypes.json'

    with open(json_file, 'r') as f:
        dtypes = json.load(f)

    if sg_baseline == 'population':
        comp = 'pop'
    else:
        comp = 'cpm'

    save_name = output_file + 'EsmamDS-{}_{}'.format(comp, db_name)

    esmam = EsmamDS(sg_baseline=sg_baseline, **parameters)
    esmam.read_data(input_file, dtypes)
    esmam.fit()
    esmam.save_results(save_name)
    if _save_log:
        esmam.save_logs(save_name)

    return
