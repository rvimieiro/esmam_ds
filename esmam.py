import math
import os
import numpy as np

from algorithm import Algorithm
import dataset
import rule
from enum import Enum


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Esmam(Algorithm):
    """Exceptional Survival Model Ant Miner"""

    def __init__(self, dataset, baseline, alpha,
                 n_ants: int, max_uncovered_cases: int,
                 n_rules_converg: int) -> None:
        super().__init__(dataset, baseline, alpha)
        self.__n_ants: int = n_ants
        self.__max_uncovered_cases: int = max_uncovered_cases
        self.__n_rules_converg: int = n_rules_converg
        self.__pheromone: np.array = None
        self.__heuristic: np.array = None
        self.__uncovered_cases: set = None
        self.__currentColony: int = 0

    def run(self) -> None:
        """Execute ESMAM Algorithm."""
        # posso passar a inicializacao do uncov cases pro init?
        self.__uncovered_cases = set(self._dataset.DataFrame.index.values)
        self._searchInitialisation()
        while self.canCreateColony():
            new_rule = self._subgroupSearch()
            # essa estrutura aqui de baixo talvez seja polemica
            if not self._subgroupUpdate(new_rule):
                break
        return

    def canCreateColony(self):
        """Return true if conditions for a new colony are satisfied."""
        first_condition = len(
            self.__uncovered_cases) > self.__max_uncovered_cases
        second_condition = self.__currentColony < self.__n_ants
        if first_condition or second_condition:
            return True
        else:
            return False

    def _searchInitialisation(self):
        """Initialize pheromone and heuristic vectors."""
        n_items = self._dataset.get_number_of_items()
        self.__pheromone = np.ones(n_items) / n_items

        # Entropy related
        self.__heuristic = np.zeros(n_items)
        survival = self._dataset.survival
        average_survival = survival.mean()
        for item in range(self._dataset.get_number_of_items()):
            items = set()
            items.add(item)
            transactions = self._dataset.get_transactions(items)
            number_of_transactions = len(transactions)
            transactions_below_avg = 0
            transactions_above_avg = 0
            for transaction in transactions:
                if survival[transaction] < average_survival:
                    transactions_below_avg += 1
                else:
                    transactions_above_avg += 1
            entropy = 0
            prob1 = transactions_above_avg / number_of_transactions
            prob2 = transactions_below_avg / number_of_transactions
            if prob1 != 0:
                entropy -= prob1 * math.log2(prob1)
            if prob2 != 0:
                entropy -= prob2 * math.log2(prob2)
            self.__heuristic[item] = 1 - entropy
        return


    def _subgroupSearch(self):
        """loop da colonia"""
        # ConstructRule()
        #ant = 1
        #convergence = 1
        # self.__searchInitialisation()
        #last_rule = None
        # while ant < self.n_ants or convergence <= self.n_rules_converg:
        #last_rule = rule
        #rule = self.__subgroupSearch()
        # if last_rule == rule:
        #convergence += 1
        # else:
        #convergence = 1
        #ant += 1
        # PruneRule()
        # PheromoneUpdating()
        # return super()._subgroupSearch()

    def _subgroupUpdate(self, new_rule) -> bool:
        """Update list of rules with or without the new rule.
        If discovered rule cannot be added, break the colony of ants."""
        can_add_rule = True
        for rule in self._rules:
            if rule == new_rule:
                can_add_rule = False
        if can_add_rule:
            self._rules.append(new_rule)
            self.__uncovered_cases -= new_rule.cover
            return True
        else:
            return False

    def _updateUncoveredCases(self) -> None:
        return super()._updateUncoveredCases()


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = dataset.Dataset(path, "survival_time", "survival_status")
    # Fazer com que essas funcoes sejam executadas automaticamente
    # ao instanciar classe dataset?
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    e = Esmam(ds, Baseline.COMPLEMENT, 0.5, 100, 100, 10)
    e._searchInitialisation()
