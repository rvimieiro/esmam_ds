import os
from dataset import Dataset
from algorithm import Algorithm
from rule import Baseline


class Esmam(Algorithm):
    """Exceptional Survival Model Ant Miner"""

    def __init__(self, dataset, baseline, alpha,
                 n_ants: int, max_uncovered_cases: int,
                 n_rules_converg: int) -> None:
        super().__init__(dataset, baseline, alpha)
        self.n_ants: int = n_ants
        self.max_uncovered_cases = max_uncovered_cases
        self.n_rules_converg = n_rules_converg

    def run(self) -> None:
        uncovered_cases = self.dataset.DataFrame.index.values
        # return a numpy array with all indices
        # DiscoveredRuleList is already represented by self.rule_set
        it = 0
        while uncovered_cases > self.max_uncovered_cases or it < self.n_ants:
            ant = 1
            convergence = 1
            self.__searchInitialisation()
            last_rule = None
            while ant < self.n_ants or convergence <= self.n_rules_converg:
                last_rule = rule
                rule = self.__subgroupSearch()
                if last_rule == rule:
                    convergence += 1
                else:
                    convergence = 1
                ant += 1

    def _searchInitialisation(self):
        """Initialize all trails with the same amount of pheromone."""
        return super()._searchInitialisation()

    def _subgroupSearch(self):
        """loop da colonia"""
        # ConstructRule()
        # PruneRule()
        # PheromoneUpdating()
        return super()._subgroupSearch()

    def _subgroupUpdate(self) -> None:
        """CanAddSubgroup"""
        return super()._subgroupUpdate()


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    i = ds.DataFrame.index.values
    print(i)

    e = Esmam(ds, Baseline.COMPLEMENT, 0.5, 100)
