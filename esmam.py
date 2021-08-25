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

    def __init__(self, dataset, baseline, alpha: float,
                 n_ants: int, max_uncovered_cases: int,
                 n_rules_converg: int, min_cover_per_rule: float) -> None:

        super().__init__(dataset, baseline, alpha)
        self.__n_ants: int = n_ants
        self.__max_uncovered_cases: int = max_uncovered_cases
        self.__n_rules_for_convergence: int = n_rules_converg
        self.__delta_uncovered: int = 0
        self.__current_colony: int = 0
        self.__pheromone: np.array = None
        self.__heuristic: np.array = None
        self.__min_cover_per_rule: float = min_cover_per_rule * \
            self._dataset.DataFrame.shape[0]
        self.__uncovered_cases = np.arange(self._dataset.DataFrame.shape[0])
        self.__available_items = np.ones(self._dataset.get_number_of_items())

    def run(self) -> None:
        """Execute ESMAM Algorithm."""

        # Initialize stagnation (would it be better initialising it in __init__?)
        self._stagnation = 0
        while self._can_create_colony():
            self._search_init()

            # New rule is found by colony
            # subgroup search is responsible for:
            #   1. Rule construction from probabilities
            #   2. Rule pruning
            new_rule = self._subgroup_search()

            # Discutir essa estrutura aqui:
            self.__delta_uncovered = len(self.__uncovered_cases)
            self._subgroup_set_update(new_rule)
            self.__delta_uncovered -= len(self.__uncovered_cases)

            if self.__delta_uncovered == 0:
                self._stagnation += 1
            else:
                self._stagnation = 0
                # stagnation - intercolony
                # j - rule convergence - intracolony
                #   j fica dentro do subgroup search

            # Is this right? NO
            # may be mixing stagnation and rules for convergence
            # if self._stagnation == self.__n_rules_for_convergence:
            #    break

        return

    def _can_create_colony(self) -> bool:
        """Return true if conditions for a new colony are satisfied."""

        # Conversar sobre mudança do critério de parada. Me ajude a lembrar?
        # Implementar o delta U, que eh se mudou o numero de casos cobertos
        # de uma colonia pra outra, numero de iteracoes em que delta U eh zero chegando em stag, break

        return len(self.__uncovered_cases) > self.__max_uncovered_cases or \
            self.__current_colony < self.__n_ants

    def _pheromone_init(self) -> None:
        """Initialize pheromone vector."""
        n_items = self._dataset.get_number_of_items()
        self.__pheromone = np.ones(n_items) / n_items
        return

    def _search_init(self):
        """Initialize pheromone and heuristic values
        associated with each item of the dataset.
        """
        if self.__heuristic == None:
            self._heuristic_map()
        self._pheromone_init()
        pass

    def _heuristic_map(self):
        """Initialize the heuristic values vector."""
        n_items = self._dataset.get_number_of_items()
        self.__heuristic = np.fromiter(map(self._calculate_item_heuristic, range(
            self._dataset.get_number_of_items())), dtype=float)

    def _calculate_item_heuristic(self, item) -> float:
        """Calculate the heuristic value for an individual item."""
        survival = self._dataset.survival
        avg_survival = survival.mean()

        # get_tx expect a set of items, even if querying
        # for tx covered by an individual item
        items = set([item])
        tx = self._dataset.get_tx(items)
        n_tx = len(tx)

        # Number of tx covered by the item must be greater
        # then user-set minimum coverage per rule treshold.
        if n_tx < self.__min_cover_per_rule:
            return 0
        else:
            tx_above_avg = np.sum(survival[tx] >= avg_survival)
            entropy = 0
            prob1 = tx_above_avg / n_tx
            prob2 = (n_tx - tx_above_avg) / n_tx
            if prob1 != 0:
                entropy -= prob1 * np.log2(prob1)
            if prob2 != 0:
                entropy -= prob2 * np.log2(prob2)
            return 1 - entropy

    def _subgroup_search(self) -> rule.Rule:
        """Execute a colony of ants resulting in a new rule."""
        ant: int = 0
        convergence: int = 0
        last_rule: rule.Rule = None
        best_rule: rule.Rule = None

        while ant <= self.__n_ants or convergence <= self.__n_rules_for_convergence:
            current_rule = self.build_description()
            current_rule = self.prune_description(current_rule)
            self.pheromone_update(current_rule)
            if current_rule.quality() > best_rule.quality():
                best_rule = current_rule
            if current_rule == last_rule:
                convergence += 1
            else:
                convergence = 0
            last_rule = current_rule
            ant += 1

        return best_rule



    def _item_probability(self, item: int) -> float:
        """Calculate item's probability of being picked up by an ant."""
        numerator = self.__heuristic[item] * self.__pheromone[item]
        denominator = None
        pass

    def _subgroup_set_update(self, new_rule) -> bool:
        """Update list of rules with or without the new rule.
        If discovered rule cannot be added, send a False flag
        to break the current colony of ants.
        """
        if new_rule.quality() > 1 - self._alpha:
            can_add_rule = True
            for rule in self._rules:
                if rule == new_rule:
                    can_add_rule = False
            if can_add_rule:
                self._rules.append(new_rule)
                self.__uncovered_cases = np.setdiff1d(
                    self.__uncovered_cases, new_rule.get_cover())
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
    ds.make_tx_array()
    #############################################################

    e = Esmam(ds, Baseline.COMPLEMENT, 0.5, 100,
              100, 10, min_cover_per_rule=.1)
    e._search_init()
    # e._subgroup_set_update(new_rule=r)
