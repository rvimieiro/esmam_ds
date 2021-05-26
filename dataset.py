import pandas as pd
import numpy as np
from collections import OrderedDict


class Dataset:
    """Take original data as a DataFrame and store data (except for target columns)
    as an array of observations where each observation is an array of its attributes'
    values (except for target attributes)"""

    def __init__(self, data, attr_survival_name, attr_event_name):
        self.survival_times = ()    # a tuple containing survival times of every observation
        self.average_survival = None    # average survival time of all observations
        self.events = ()    # array of bool describing survival status of observations
        self.attr_values = {}   # {'attribute': ['val_1', ..., 'val_n']}
        self.data = None    # A[n_observations][n_attributes]

        self._col_index = {}
        self._uncovered_cases = [True]*data.shape[0]    # initially, all observations are uncovered
        self._original_data = data.copy()   # DataFrame
        self._surv_name = attr_survival_name # name of column storing survival times
        self._event_name = attr_event_name # name of column storing censoring info
        self._count = [0]*data.shape[0] 

        self._constructor(attr_survival_name, attr_event_name)

    def _constructor(self, attr_survival_name, attr_event_name):

        data = self._original_data.copy()

        self.survival_times = (attr_survival_name, data[attr_survival_name])
        self.average_survival = data[attr_survival_name].mean()
        self.events = (attr_event_name, data[attr_event_name])

        to_drop = [attr_survival_name, attr_event_name]
        data.drop(columns=to_drop, inplace=True)

        col_names = list(data.columns.values)
        self.attr_values = OrderedDict.fromkeys(col_names)
        for name in col_names:
            self.attr_values[name] = sorted(list(set(data[name])))

        self._col_index = dict.fromkeys(col_names)
        for name in col_names:
            self._col_index[name] = data.columns.get_loc(name)


        self.data = np.array(data.values)
        return

    @property
    def size(self):
        return self._original_data.shape[0]

    @property
    def surv_name(self):
        return self._surv_name

    def remove_covered_cases(self, cases):
        for case in cases:
            if self._count[case] <= 1:  # if covered only once > becomes uncovered
                self._count[case] = 0
                self._uncovered_cases[case] = True
            else:                       # if covered more than once > decrements cover count
                self._count[case] -= 1
        return

    def update_covered_cases(self, covered_cases):
        # set flag for rule-covered cases
        for case in covered_cases:
            self._uncovered_cases[case] = False
            self._count[case] += 1
        return

    def get_case_count(self):
        return self._count

    def get_col_index(self, col_name):
        return self._col_index[col_name]

    def get_data(self):
        return self._original_data.copy()

    def get_cases_coverage(self):   # returns a bool list with True for covered cases
        return [covered == False for covered in self._uncovered_cases]

    def get_no_of_uncovered_cases(self):
        return sum(self._uncovered_cases)

    def get_uncovered_cases(self):
        return list(self._original_data[self._uncovered_cases].index)

    def get_instances(self):
        return list(range(len(self.data)))
