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
                 n_rules_converg: int, min_cover_per_rule: float) -> None:

        super().__init__(dataset, baseline, alpha)

        self.__n_ants: int = n_ants
        self.__max_uncovered_cases: int = max_uncovered_cases
        self.__n_rules_converg: int = n_rules_converg
        self.__deltaUncovered: int = 0
        self.__currentColony: int = 0
        self.__pheromone: np.array = None
        self.__heuristic: np.array = None
        self.__min_cover_per_rule: float = min_cover_per_rule
        self.__uncovered_cases = np.arange(self._dataset.DataFrame.shape[0])

    def run(self) -> None:
        """Execute ESMAM Algorithm."""
        # Heuristic is calculated only once
        self._heuristicInitialisation()
        self._stagnation = 0

        while self.canCreateColony():
            # Pheromone is initialised for each colony
            self._pheromoneInitialisation()

            # New rule is found by colony
            # subgroup search is responsible for:
            #   1. Rule construction from probabilities
            #   2. Rule pruning
            new_rule = self._subgroupSearch()

            # Discutir essa estrutura aqui:
            self.__deltaUncovered = len(self.__uncovered_cases) 
            self._subgroupSetUpdate(new_rule)
            self.__deltaUncovered -= len(self.__uncovered_cases)
            if self.__deltaUncovered == 0:
                self._stagnation += 1
            if self._stagnation == self.__n_rules_converg:
                break
        return

    def canCreateColony(self):
        """Return true if conditions for a new colony are satisfied."""
        # Conversar sobre mudança do critério de parada. Me ajude a lembrar?
        # Implementar o delta U, que eh se mudou o numero de casos cobertos
        # de uma colonia pra outra
        # numero de iteracoes em que delta U eh zero chegando em stag, break
        return len(self.__uncovered_cases) > self.__max_uncovered_cases or \
            self.__currentColony < self.__n_ants

    def _pheromoneInitialisation(self):
        """Initialize pheromone vector."""
        n_items = self._dataset.get_number_of_items()
        self.__pheromone = np.ones(n_items) / n_items
        return

    def _searchInitialisation(self):
        pass

    def _heuristic_map(self):
        """Initialise the heuristic values vector."""
        n_items = self._dataset.get_number_of_items()
        self.__heuristic = np.zeros(n_items)
        for i in (map(self._calculate_item_heuristic, range(self._dataset.get_number_of_items()))):
            print('Entropy:', i)

    def _calculate_item_heuristic(self, item) -> float:
        survival = self._dataset.survival
        average_survival = survival.mean()

        items = set()
        items.add(item)
        transactions = self._dataset.get_transactions(items)

        input()
        print('Item transactions:', len(transactions))
        print('Minimum cover per rule:', self.__min_cover_per_rule * self._dataset.DataFrame.shape[0])
        if len(transactions) < self.__min_cover_per_rule * self._dataset.DataFrame.shape[0]:
            return 0
        else:
            number_of_transactions = len(transactions)
            transactions_above_avg = np.sum(
                survival[transactions] >= average_survival)
            entropy = 0
            prob1 = transactions_above_avg / number_of_transactions
            prob2 = (number_of_transactions -
                     transactions_above_avg) / number_of_transactions
            print('Probability 1st class:', prob1)
            print('Probability 2st class:', prob2)
            # checar se prob1 ou prob2 sao 0, porque log2(0) -> inf
            # caso positivo, entropy = 0
            if prob1 != 0:
                # entropy -= prob1 * math.log2(prob1)
                entropy -= prob1 * np.log2(prob1)
            if prob2 != 0:
                # entropy -= prob2 * math.log2(prob2)
                entropy -= prob2 * np.log2(prob2)

            return 1 - entropy

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

    def _subgroupSetUpdate(self, new_rule) -> bool:
        """Update list of rules with or without the new rule.
        If discovered rule cannot be added, break the colony of ants.
        """
        if new_rule.quality() > 1 - self._alpha:
            can_add_rule = True
            for rule in self._rules:
                if rule == new_rule:
                    can_add_rule = False
            if can_add_rule:
                self._rules.append(new_rule)

                # atualizacao do delta uncovered
                # verificar melhor aqui, passar essas etapas
                # para fora da funcao _subgroupSetUpdate
                # self.__deltaUncovered = len(self.__uncovered_cases)

                self.__uncovered_cases = np.setdiff1d(
                    self.__uncovered_cases, new_rule.get_cover())
                # self.__deltaUncovered -= len(self.__uncovered_cases)
            return True
        else:
            return False


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = dataset.Dataset(path, "survival_time", "survival_status")
    # Fazer com que essas funcoes sejam executadas automaticamente
    # ao instanciar classe dataset?
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()
    #############################################################

    e = Esmam(ds, Baseline.COMPLEMENT, 0.5, 100, 100, 10, min_cover_per_rule=.1)
    e._heuristic_map()
    # e._subgroupSetUpdate(new_rule=r)
