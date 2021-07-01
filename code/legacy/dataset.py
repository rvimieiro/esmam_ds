import pandas as pd
import numpy as np
from collections import OrderedDict


class Dataset:
    # usando vetor de bits https://numpy.org/doc/stable/reference/generated/numpy.packbits.html
    """Take original data as a DataFrame and store data (except for target columns)
    as an array of observations where each observation is an array of its attributes'
    values (except for target attributes)"""
    # interface do programa com o disco/bd/raw_data

    # def __init__(self, file_path, attr_survival_name, attr_event_name)
    # idealmente
    # pandas dataframe pra armazenar dados originais, np.array para o restante do programa

    def __init__(self, data, attr_survival_name, attr_event_name):
        # to be removed, get through function
        self.survival_times = ()    # a tuple containing survival times of every observation

        # to be removed, get through function
        self.average_survival = None    # average survival time of all observations

        # to be removed, get through function
        self.events = ()    # array of bool describing survival status of observations

        # to be removed
        self.attr_values = {}   # {'attribute': ['val_1', ..., 'val_n']}

        self.data = None    # A[n_observations][n_attributes]
        # self.__data = None -> DF

        # to be removed, access through index
        self._col_index = {}

        # to be removed, should be in algorithm, np.array
        # initially, all observations are uncovered
        self._uncovered_cases = [True]*data.shape[0]

        # to be removed
        self._original_data = data.copy()   # DataFrame --- Redundante ---

        # should stay
        self._surv_name = attr_survival_name  # name of column storing survival times
        # self._surv_time_col, handle censoring definitions in docs

        self._event_name = attr_event_name  # name of column storing censoring info
        # self._surv_name_col

        # self._count = [0]*data.shape[0] - deveria estar provavelmente no Terms Manager
        self._count = [0]*data.shape[0]

        self._constructor(attr_survival_name, attr_event_name)

    def _constructor(self, attr_survival_name, attr_event_name):

        data = self._original_data.copy()

        self.survival_times = (attr_survival_name, data[attr_survival_name])
        # lixo self.survival_times = (attr_survival_name, data[attr_survival_name])
        self.average_survival = data[attr_survival_name].mean()
        # lixo self.average_survival = data[attr_survival_name].mean()
        self.events = (attr_event_name, data[attr_event_name])
        # lixo self.events = (attr_event_name, data[attr_event_name])

        # também manter essas colunas no Dataframe principal
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

    # @property
    def get_items(self):
        """Retorna o mapa de itens (attr,valor) para inteiros"""
        # Pode ser armazenado para evitar recalcular
        # Implementar usando comprehension
        return {("attr", "valor"): 1}

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
