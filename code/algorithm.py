import copy
import json
import math
import pandas as pd
import numpy as np
import sys
import statsmodels.api as sm
from itertools import combinations_with_replacement
from itertools import chain
from lifelines import KaplanMeierFitter
from datetime import datetime

from utils import NoIndent, MyEncoder
from terms_manager import TermsManager
from rule import Rule
from dataset import Dataset
from pruner_prototype import Pruner
# from pruner import Pruner

# DEFAULT parameters
NUM_OF_ANTS = 1000  # number of iterations for each colony
MIN_SIZE_SUBGROUP = 0.1
RULES_TO_CONVERGENCE = 5  # consecutive generated rules found to be equal
# threshold on iterations: iterations that no new cases were covered
ITS_TO_STAGNATION = 40
WEIGH_SCORE = 0.9
F_LOGISTIC_OFFSET = 5
ALPHA = 0.05

# global variables
JACCARD_DSCPT_THRESHOLD = 0.5


class EsmamDS:
    """Exceptional model mining ant miner diverse search.
    Discover subgroups with exceptional KM curves."""

    def __init__(self, sg_baseline='population',
                 no_of_ants=NUM_OF_ANTS,
                 min_size_subgroup=MIN_SIZE_SUBGROUP,
                 no_rules_converg=RULES_TO_CONVERGENCE,
                 its_to_stagnation=ITS_TO_STAGNATION,
                 weigh_score=WEIGH_SCORE,
                 logistic_offset=F_LOGISTIC_OFFSET,
                 alpha=ALPHA,
                 seed=0,
                 **kwargs):
        # subgroup comparison (population/complement)
        self.sg_comp = sg_baseline
        self.no_of_ants = no_of_ants
        self.min_size_subgroup = min_size_subgroup
        # ?intracolonial (consecutive rules must be equal)
        self.no_rules_converg = no_rules_converg
        # no iterations in which no uncovered cases were covered by the discovered rule
        self.its_to_stagnation = its_to_stagnation
        # Heuristic related
        self.weigh_score = weigh_score
        self.logistic_offset = logistic_offset
        # Logrank test / subgroup selection related
        self.alpha = alpha
        ###
        self._seed = seed

        # print(3*'-', "execution's parameters", 3*'-')
        # print("sg_baseline:", sg_baseline)
        # print("no_of_ants:", no_of_ants)
        # print("min_size_subgroup:", min_size_subgroup)
        # print("no_rules_converg:", no_rules_converg)
        # print("its_to_stagnation:", its_to_stagnation)
        # print("logistic_offset:", logistic_offset)
        # print()

        self.discovered_rule_list = []
        self._Dataset = None
        self._TermsManager = None
        self._Pruner = None
        self._data_path = None
        self._population_survModel = None
        self._no_of_uncovered_cases = None
        self._stagnation = 0
        self._iterations = 0
        self._log_iterations = {}
        self._log_heuristic_table = {}
        self._log_term_count = {}
        self._log_logistic_count = {}
        self._time = None

    @property
    def min_case_per_rule(self):
        """Calculate the minimum number of cases that a rule must cover."""
        return math.ceil(self.min_size_subgroup * self._Dataset.size)

    def _get_population_Survival(self):

        kmf = KaplanMeierFitter()
        kmf.fit(self._Dataset.survival_times[1], self._Dataset.events[1],
                label='KM estimates for population', alpha=self.alpha)
        self._population_survModel = kmf
        return

    def _global_stopping_condition(self) -> bool:
        """End algorithm execution if there are no uncovered cases or stagnation
        threshold is achieved.
        """
        if self._no_of_uncovered_cases == 0 or self._stagnation > self.its_to_stagnation:
            return True
        return False

    def _local_stopping_condition(self, ant_index: int, converg_test_index: int) -> bool:
        """End a colony of ants if it surpasses the ant count limit or there were
        no_rules_converg consecutive equal rules created by the ants.
        """
        if ant_index >= self.no_of_ants:
            return True
        elif converg_test_index >= self.no_rules_converg:
            return True
        return False

    def get_list(self):
        """Return a deep copy of the list of discovered rules."""
        return copy.deepcopy(self.discovered_rule_list)

    def _add_rule(self, rule: Rule):
        """Append rule to the list of discovered rules and update the number of
        total covered cases with the number of cases covered by this rule.
        """
        self.discovered_rule_list.append(rule)
        self._Dataset.update_covered_cases(rule.sub_group_cases)
        return

    def _remove_rule(self, rule_idx: int):
        """Remove rule (by its index) from list of discovered rules and update 
        the number of total covered cases removing the cases covered by removed
        rule.
        """
        rule = self.discovered_rule_list.pop(rule_idx)
        self._Dataset.remove_covered_cases(rule.sub_group_cases)
        return

    def _can_add_rule(self, new_rule: Rule, rule_list: list) -> bool:
        """Return true if rule new_rule can be added to the list of discovered
        rules.
        """

        # CASE: new rule is not exceptional
        if new_rule.p_value >= self.alpha:
            return False

        # compare new_rule with rules already in the list
        for rule_idx, rule in enumerate(rule_list):

            # CASE: equal rules
            if new_rule.equals(rule):
                return False

            # CASE: similar models
            if not new_rule.is_exceptional(rule, self.alpha):

                # CASE: no intersections btw rules' descriptions
                attr_intersec = new_rule.get_attributes().intersection(rule.get_attributes())
                if not attr_intersec:
                    continue

                # CASE: new_rule is more specific than rule
                elif new_rule.is_in(rule):
                    return False

                # CASE: new_rule is more general than rule
                elif rule.is_in(new_rule):
                    del rule_list[rule_idx]
                    if self._can_add_rule(new_rule, rule_list):
                        self._remove_rule(rule_idx)
                        return True
                    else:
                        return False

                # CASE: unificate rule (they are not subset of one-another)
                else:
                    has_root = new_rule.has_root(rule)
                    has_merge = new_rule.has_merge(rule)

                    # CASE: no root neither merge (there is no way of generalization)
                    if not has_root and not has_merge:
                        continue

                    # CASE: there is only root or merge
                    elif has_root != has_merge:
                        modif_rule = Rule(self._Dataset, self.sg_comp)
                        if has_root:
                            modif_rule.root(new_rule, rule, self._TermsManager)
                        else:
                            modif_rule.merge(
                                new_rule, rule, self._TermsManager)

                        # modif_rule can be added
                        if self._can_add_rule(modif_rule, self.get_list()):
                            self._add_rule(modif_rule)
                            if new_rule.is_exceptional(modif_rule, self.alpha):
                                continue
                            else:
                                return False
                        else:   # modif_rule cannot be added
                            continue

                    # CASE: there is both root and merge
                    else:
                        root_rule = Rule(self._Dataset, self.sg_comp)
                        root_rule.root(new_rule, rule, self._TermsManager)
                        merged_rule = Rule(self._Dataset, self.sg_comp)
                        merged_rule.merge(new_rule, rule, self._TermsManager)

                        # case: root and merge have similar models
                        if not root_rule.is_exceptional(merged_rule, self.alpha):
                            # root_rule can be added
                            if self._can_add_rule(root_rule, self.get_list()):
                                self._add_rule(root_rule)
                                if new_rule.is_exceptional(root_rule, self.alpha):
                                    continue
                                else:
                                    return False
                            else:  # root_rule cannot be added
                                continue
                        # case: root and merge have different models
                        else:
                            add_merge = self._can_add_rule(
                                merged_rule, self.get_list())
                            if add_merge:
                                self._add_rule(merged_rule)

                            add_root = self._can_add_rule(
                                root_rule, self.get_list())
                            if add_root:
                                self._add_rule(root_rule)

                            if not add_root and not add_merge:
                                continue
                            elif add_root and not add_merge:
                                if new_rule.is_exceptional(root_rule, self.alpha):
                                    continue
                                else:
                                    return False
                            elif not add_root and add_merge:
                                if new_rule.is_exceptional(merged_rule, self.alpha):
                                    continue
                                else:
                                    return False
                            else:
                                if new_rule.is_exceptional(root_rule, self.alpha) and new_rule.is_exceptional(merged_rule, self.alpha):
                                    continue
                                else:
                                    return False
        return True

    def read_data(self, data_path, dtypes=None,
                  attr_survival_name='survival_time',
                  attr_event_name='survival_status'):
        # should be Dataset's function
        """Read ~.xz file at data_path and set _Dataset to a Dataset object"""

        self._data_path = data_path
        if not dtypes:
            data = pd.read_csv(data_path, delimiter=',',
                               header=0, index_col=False, compression='xz')
        else:
            data = pd.read_csv(data_path, delimiter=',', header=0,
                               index_col=False, compression='xz', dtype=dtypes)
        data.reset_index(drop=True, inplace=True)
        self._Dataset = Dataset(data, attr_survival_name, attr_event_name)
        return

    def fit(self):
        """Algorithm's main procedure. Generate a dictionary of rules created
        and pruned through ant-colony covering-based approach.
        """
        no_colonies: int = 0

        # Initialization
        self._TermsManager = TermsManager(
            self._Dataset,
            self.min_case_per_rule,
            self._seed
        )
        self._Pruner = Pruner(
            self._Dataset,
            self._TermsManager,
            self.sg_comp
        )
        self._no_of_uncovered_cases = self._Dataset.get_no_of_uncovered_cases()
        self._get_population_Survival()

        # Algorithm's main loop
        begin = datetime.now()
        while not self._global_stopping_condition():
            colony_birth = datetime.now()
            no_colonies += 1

            # local variables
            # print("Initializing colony no.", no_colonies, '\n')
            ant_index = 0
            converg_test_index = 1

            # initialize pheromone table for this colony
            self._TermsManager.pheromone_init()
            # update global heuristic
            has_update = self._TermsManager.heuristics_updating(
                self._Dataset, self.weigh_score, self.logistic_offset
            )
            if not has_update:
                break

            # Initialize rules
            previous_rule = Rule(self._Dataset, self.sg_comp)
            best_rule = copy.deepcopy(previous_rule)

            # Local search, each iteration represents an colony.
            log_ants = {}
            while not self._local_stopping_condition(ant_index, converg_test_index):
                log_ants[ant_index] = {}

                # ant creates an empty rule
                current_rule = Rule(self._Dataset, self.sg_comp)
                current_rule.construct(
                    self._TermsManager, self.min_case_per_rule
                )
                log_ants[ant_index]['r_const'] = current_rule.antecedent
                log_ants[ant_index]['r_const_ft'] = current_rule.fitness

                # print("---Ant", ant_index, "found:")
                # print("\tRaw rule:", current_rule.antecedent)
                current_rule = self._Pruner.prune(current_rule)
                log_ants[ant_index]['r_pr'] = current_rule.antecedent
                log_ants[ant_index]['r_pr_ft'] = current_rule.fitness
                # print("\tPruned rule:", current_rule.antecedent)

                if current_rule.equals(previous_rule):
                    converg_test_index += 1
                else:
                    converg_test_index = 1
                    if current_rule.fitness > best_rule.fitness:
                        # best_rule = copy.deepcopy(current_rule)
                        best_rule = current_rule

                log_ants[ant_index]['pheromone_table'] = self._TermsManager.get_pheromone_table(
                )

                self._TermsManager.pheromone_updating(
                    current_rule.antecedent, current_rule.fitness
                )
                previous_rule = copy.deepcopy(current_rule)
                ant_index += 1

            # End-of-colony: att rule-list and covered cases
            prev_uncover = self._no_of_uncovered_cases
            ## prev_uncover: casos nao cobertos pelas regras geradas ate a iteracao atual que estao na lista de regras ##
            if self._can_add_rule(best_rule, self.get_list()):
                self._add_rule(best_rule)
                self._no_of_uncovered_cases = self._Dataset.get_no_of_uncovered_cases()

            # check stagnation of the data set
            if (prev_uncover - self._no_of_uncovered_cases) == 0:
                self._stagnation += 1
            else:
                self._stagnation = 0

            # saves iteration logs
            self._log_iterations[self._iterations] = log_ants.copy()
            # needs to be saved before pheromone_init()
            self._log_term_count[self._iterations] = self._TermsManager.get_counts_table(
            )
            self._log_heuristic_table[self._iterations] = self._TermsManager.get_heuristic_table(
            )
            # updates
            self._TermsManager.att_discovered_terms(best_rule.antecedent)
            # needs to be saveed after att_discovered_terms()
            self._log_logistic_count[self._iterations] = self._TermsManager.get_logistic_table(
            )

            self._iterations += 1
            colony_death = datetime.now()
            # print(2*'\n')
            # print("--> Colony's life:", colony_death - colony_birth)
            # print("--> Colony's number of ants:", ant_index)
            # print(2*'\n')

        # end-algorithm (some savings)
        self._time = datetime.now() - begin
        self.print_ant()        

        # generates the rules representative strings
        # print(10*'*',' RESULTS ', 10*'*')
        # print('- Total number of observations:', len(current_rule._Dataset.data))
        # print('- Average survival time:', current_rule._Dataset.average_survival)
        for index, rule in enumerate(self.discovered_rule_list):
            rule.set_string_repr(index)
            print("Rule", index, '->', rule._string_repr)
            print()
            print('\t antecedent:', rule.antecedent)
            print('\t covered cases:', rule.no_covered_cases,)
            print('\t fitness:', rule.fitness)
            print('\t p-value:', rule.p_value)
            print()
            rule.set_KMmodel(alpha=self.alpha)
            # rule._KMmodel['subgroup'].plot()

        return

    def save_results(self, save_path):
        # LOG FILE FOR SURVIVAL MODELS
        self._save_SurvivalFunctions(save_path)
        # LOG FILE FOR RULE-MODEL
        self._save_RuleModel(save_path)
        # LOG FILE FOR FINAL RULESET (organized)
        self._save_RuleSet(save_path)
        return

    def _save_SurvivalFunctions(self, save_name):

        index = self._population_survModel.survival_function_.index.copy()
        columns = ['times', 'population'] + \
            [rule.id for rule in self.discovered_rule_list]
        df = pd.DataFrame(columns=columns)
        df.times = index.values
        df.population = self._population_survModel.survival_function_.values

        for rule in self.discovered_rule_list:
            survival_fnc = rule._KMmodel['subgroup'].survival_function_.reindex(
                index)
            survival_fnc.fillna(method='ffill', inplace=True)
            df[rule.id] = survival_fnc.values

        log_file = '{}_SurvivalModels.csv'.format(save_name)
        df.to_csv(log_file, index=False, header=True)
        # print('... saved: {}'.format(log_file))
        return

    def _save_RuleModel(self, save_name):
        dic = {
            'id': list(map(lambda rule: rule.id, self.discovered_rule_list)),
            'sg': list(map(lambda rule: rule.description, self.discovered_rule_list)),
            'baseline': [self.sg_comp]*len(self.discovered_rule_list),
            'fitness': list(map(lambda rule: rule.fitness, self.discovered_rule_list)),
            'pvalue': list(map(lambda rule: rule.p_value, self.discovered_rule_list)),
            'mean_sg': list(map(lambda rule: rule.mean_survival, self.discovered_rule_list)),
            'mean_pop': [self._Dataset.average_survival]*len(self.discovered_rule_list),
            'mean_cpm': list(map(lambda rule: rule.complement_mean_survival, self.discovered_rule_list)),
            'size_sg': list(map(lambda rule: rule.no_covered_cases, self.discovered_rule_list)),
            'size_pop': [self._Dataset.size]*len(self.discovered_rule_list),
            'size_cpm': list(map(lambda rule: len(rule._complement_cases), self.discovered_rule_list))
        }

        df = pd.DataFrame(dic)
        log_file = '{}_RuleModel.csv'.format(save_name)
        df.to_csv(log_file, float_format='%f', index=False)
        # print('... saved: {}'.format(log_file))
        return

    def _save_RuleSet(self, save_name):
        log_file = '{}_RuleSet.txt'.format(save_name)

        # calc matrix functions: pval and description (True values for similarity)
        def sim_model_matrix(rule_list, db, VAR_TIME_NAME='survival_time', VAR_EVENT_NAME='survival_status'):
            rules_idx = list(range(len(rule_list)))
            matrix = pd.DataFrame(
                data=None, index=rules_idx, columns=rules_idx)
            for r1_pos, r2_pos in combinations_with_replacement(rules_idx, 2):
                r1_cases = rule_list[r1_pos].sub_group_cases
                r2_cases = rule_list[r2_pos].sub_group_cases

                times = db[VAR_TIME_NAME][r1_cases].to_list(
                ) + db[VAR_TIME_NAME][r2_cases].to_list()
                events = db[VAR_EVENT_NAME][r1_cases].to_list(
                ) + db[VAR_EVENT_NAME][r2_cases].to_list()
                group_id = ['r1'] * db[VAR_TIME_NAME][r1_cases].shape[0] + \
                    ['r2'] * db[VAR_TIME_NAME][r2_cases].shape[0]
                try:
                    _, p_value = sm.duration.survdiff(
                        time=times, status=events, group=group_id)
                except:  # apparently, get error when rules are equal
                    p_value = 1.0

                if r1_pos == r2_pos:
                    matrix.loc[r1_pos, r1_pos] = p_value
                else:
                    matrix.loc[r1_pos, r2_pos] = p_value
                    matrix.loc[r2_pos, r1_pos] = p_value

            matrix_bool = matrix >= self.alpha
            np.fill_diagonal(matrix_bool.values, False)
            return matrix_bool

        def sim_dscpt_matrix(rule_list, small=False):
            rules_idx = list(range(len(rule_list)))
            matrix = pd.DataFrame(
                data=None, index=rules_idx, columns=rules_idx)
            for r1_pos, r2_pos in combinations_with_replacement(rules_idx, 2):
                r1_terms = rule_list[r1_pos].get_terms()
                r2_terms = rule_list[r2_pos].get_terms()

                if small:
                    minor = min([len(r1_terms), len(r2_terms)])
                    intersection = set(r1_terms).intersection(r2_terms)
                    jaccard_index = len(intersection) / minor
                else:
                    union = r1_terms.union(r2_terms)
                    intersection = set(r1_terms).intersection(r2_terms)
                    jaccard_index = len(intersection) / len(union)

                if r1_pos == r2_pos:
                    matrix.loc[r1_pos, r1_pos] = jaccard_index
                else:
                    matrix.loc[r1_pos, r2_pos] = jaccard_index
                    matrix.loc[r2_pos, r1_pos] = jaccard_index

            matrix_bool = matrix >= JACCARD_DSCPT_THRESHOLD
            np.fill_diagonal(matrix_bool.values, False)
            return matrix_bool

        # print all rules representatives
        f = open(log_file, "a+")
        f.write('DISCOVERED SUBGROUPS')
        f.close()

        printed_rules = []
        sim_models = sim_model_matrix(
            self.discovered_rule_list, self._Dataset.get_data())
        sim_descript = sim_dscpt_matrix(self.discovered_rule_list)

        for index, rule in enumerate(self.discovered_rule_list):

            if rule.id in printed_rules:
                continue

            # print rule
            r_id, r_desc, r_info = rule.get_full_description()
            with open(log_file, "a+") as f:
                f.write('\n\n{}: {} {}'.format(r_id, r_desc, r_info))
            printed_rules.append(r_id)

            # similar models:
            if sim_models[index].any():
                similar = list(sim_models[index][sim_models[index]].index)
                for idx in similar:
                    r_sim = self.discovered_rule_list[idx]
                    if r_sim.id in printed_rules:
                        continue
                    r_id, r_desc, r_info = r_sim.get_full_description(rule)
                    with open(log_file, "a+") as f:
                        f.write('\n[SM] {}: {} {}'.format(
                            r_id, r_desc, r_info))
                    printed_rules.append(r_id)

            # similar descriptions:
            if sim_descript[index].any():
                similar = list(sim_descript[index][sim_descript[index]].index)
                for idx in similar:
                    r_sim = self.discovered_rule_list[idx]
                    if r_sim.id in printed_rules:
                        continue
                    r_id, r_desc, r_info = r_sim.get_full_description(rule)
                    with open(log_file, "a+") as f:
                        f.write('\n[SD] {}: {} {}'.format(
                            r_id, r_desc, r_info))
                    printed_rules.append(r_id)

        # print legend for disjunction/similar symbols
        f = open(log_file, "a+")
        f.write('\n\n---------\n[SM] similar model\n[SD] similar description')
        f.write(
            '\n[jaccard-c] jaccard index over coverage\n[jaccard-d] jaccard index over description')
        f.close()
        # print('... saved: {}'.format(log_file))
        return

    def save_logs(self, save_path):
        # JSON LOG FILE
        # rule model
        rules = {}
        covered_cases = {}
        size = 0
        for _, rule in enumerate(self.discovered_rule_list):
            idx, dic = rule.get_result()
            rules[idx] = dic.copy()
            covered_cases[idx] = rule.sub_group_cases
            size += len(rule.antecedent)

        # metrics
        metrics = {}
        if len(covered_cases) == 0:
            ruleCoverage = 0
        else:
            ruleCoverage = sum([len(item) for key, item in covered_cases.items(
            )]) / len(covered_cases) / self._Dataset.data.shape[0]
        ruleCoverageSTD = np.std(
            [len(item) for key, item in covered_cases.items()]) / self._Dataset.data.shape[0]
        setCovered = list(set(chain(*covered_cases.values())))
        setCoverage = len(setCovered) / self._Dataset.data.shape[0]
        metrics['num_rules'] = len(self.discovered_rule_list)
        if len(self.discovered_rule_list) == 0:
            metrics['length'] = 0
        else:
            metrics['length'] = size / len(self.discovered_rule_list)
        metrics['rule_coverage'] = ruleCoverage
        metrics['rule_coverageSTD'] = ruleCoverageSTD
        metrics['set_coverage'] = setCoverage

        # params
        params = {
            'sg_baseline': self.sg_comp,
            'sg_min_percent': self.min_size_subgroup,
            'cover_weigh': self.weigh_score,
            'f_logistic_x0': self.logistic_offset,
            'alpha': self.alpha,
            'its_to_stagnation': self.its_to_stagnation,
            'no_of_ants': self.no_of_ants,
            'no_rules_converg': self.no_rules_converg
        }

        # run log
        run = {
            'timestamp': str(datetime.now()),
            'data_path': self._data_path,
            'data_shape': NoIndent(self._Dataset.get_data().shape),
            'num_of_terms': self._TermsManager.get_num_terms(),
            'run_time': str(self._time),
            'num_iterations': self._iterations,
            'np_seed': self._seed,
            'uncovered_cases': NoIndent(self._Dataset.get_uncovered_cases()),
            'log_iterations': NoIndent(self._log_iterations),
            'log_heuristics': NoIndent(self._log_heuristic_table),
            'log_count_execution': NoIndent(self._log_term_count),
            'log_count_discover': NoIndent(self._log_logistic_count)
        }

        # unified log for json
        log = {
            'params': params,
            'metrics': metrics,
            'model': rules,
            'run': run
        }
        log_file = '{}_log.json'.format(save_path)
        with open(log_file, 'w') as f:
            f.write(json.dumps(log, indent=2, cls=MyEncoder))
        # print('... saved log-file: {}'.format(log_file))
        return

    def print_ant(self):
        print(r"""
              "=.                                       
             "=. \                                      
                \ \
             _,-=\/=._        _.-,_
            /         \      /=-._ "-.
           |=-./~\___/~\    /     `-._\
           |   \o/   \o/   /  ESMAM   /
            \_   `~~~;/    |  rules  |
              `~,._,-'    /          /
                 | |      =-._      /
             _,-=/ \=-._     /|`-._/
           //           \\   )\
          /|             |)_.'/
         //|             |\_."   _.-\
        (|  \           /    _.`=    \
        ||   ":_    _.;"_.-;"   _.-=.:
     _-."/    / `-."\_."        =-_.;\
    `-_./   /             _.-=.    / \\
           |              =-_.;\ ."   \\
           \                   \\/     \\
           /\_                .'\\      \\
          //  `=_         _.-"   \\      \\
         //      `~-.=`"`'       ||      ||
         ||    _.-_/|            ||      |\_.-_
     _.-_/|   /_.-._/            |\_.-_  \_.-._\
    /_.-._/                      \_.-._\
        """)
