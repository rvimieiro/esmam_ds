import argparse
from execution import execute

parser = argparse.ArgumentParser(description='Execute Esmam-DS algorithm.')
parser.add_argument(
    '-input', default='datasets/actg320_disc.xz',
    help='The input file path', type=str
)
parser.add_argument(
    '-output', default='outputs/',
    help='The output file path', type=str
)
parser.add_argument(
    '-noa', default=1000,
    help='The number of ants', type=int
)
parser.add_argument(
    '-msg', default=0.05,
    help='Minimum subgroup size', type=float
)
parser.add_argument(
    '-nrc', default=5,
    help='Number of sequentially found rules that, if equal, stops execution',
    type=int
)
parser.add_argument(
    '-its', default=40,
    help='Required number of iterations rendering stagnation',
    type=int
)
parser.add_argument(
    '-loo', default=10,
    help='?',
    type=int
)

args = parser.parse_args()
input_path = args.input
output_path = args.output
parameters = {'no_of_ants': args.noa,
              'min_size_subgroup': args.msg,
              'no_rules_converg': args.nrc,
              'its_to_stagnation': args.its,
              'logistic_offset': args.loo
              }


execute(sg_baseline='population', _save_log=True,
        _it_init=0, input_file=input_path, output_file=output_path,
        parameters=parameters)
