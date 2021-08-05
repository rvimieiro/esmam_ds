import os
import numpy as np

from algorithm import Algorithm
from data import dataset
from data import baseline
from util import rule


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

    def run(self) -> None:
        uncovered_cases = set(self._dataset.DataFrame.index.values)
        it = 0
        heuristic, pheromone = self._searchInitialisation()
        while len(uncovered_cases) > self.__max_uncovered_cases or it < self.__n_ants:
            rule = self._subgroupSearch(heuristic, pheromone)
            if rule.quality >= (1 - self._alpha):
                self._rule_set = self._subgroupUpdate(rule)
                uncovered_cases -= rule.cover
            else:
                break
            it += 1
        return

    def _searchInitialisation(self):
        n_items = self._dataset.get_number_of_items()
        self.pheromone = np.ones(n_items) / n_items
        # heuristic = ??????

    def _subgroupSearch(self):
        """loop da colonia"""
        # ConstructRule()
            #ant = 1
            #convergence = 1
            #self.__searchInitialisation()
            #last_rule = None
            #while ant < self.n_ants or convergence <= self.n_rules_converg:
                #last_rule = rule
                #rule = self.__subgroupSearch()
                #if last_rule == rule:
                        #convergence += 1
                    #else:
                        #convergence = 1
                    #ant += 1
        ## PruneRule()
        ## PheromoneUpdating()
        #return super()._subgroupSearch()

    def _subgroupUpdate(self, rule) -> None:
        """CanAddSubgroup"""
        return super()._subgroupUpdate()

    def _updateUncoveredCases(self) -> None:
        return super()._updateUncoveredCases()


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = dataset.Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()

    e = Esmam(ds, baseline.Baseline.COMPLEMENT, 0.5, 100, 100, 10)
    e._searchInitialisation()
