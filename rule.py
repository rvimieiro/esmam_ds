from enum import Enum

from numpy.lib.function_base import cov
from dataset import Dataset
import statsmodels.api as sm
import numpy as np
import os


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:
    """Implement a rule. A rule is composed of an antecedent. This antecedent
    covers a subgroup and a this subgroup has an associated cover_survival
    function.
    """

    def __init__(self, Dataset, Baseline):

        self._antecedent: set = set()
        self._cover = None
        self.quality: float = None
        self.baseline: Baseline = Baseline
        self.Dataset: Dataset = Dataset

    @property
    def antecedent(self) -> set:
        """Get the Rule antecedent."""
        return self._antecedent

    @antecedent.setter
    def antecedent(self, new_antecedent: set):
        self._antecedent = new_antecedent

    def add_item(self, item: int) -> None:
        """Add item to antecedent. The item is referred by its integer index in
        the Dataset's class item_map.
        """
        self._antecedent.add(item)

    def remove_item(self, item: tuple) -> None:
        """Remove item of the antecedent. The item is referred by its
        integer-valued index in the Dataset's class item_map.
        """
        self._antecedent.remove(item)

    def set_cover(self):
        """Set the rule cover. A rule's cover is defined as the set of
        transactions where each transaction contain, at least,
        every item of the antecedent."""
        self.cover = self.Dataset.get_transactions(self.antecedent)

    def get_cover(self):
        """Return Rule's cover."""
        return self.cover

    def get_cover_size(self):
        """Return the size of a Rule's cover."""
        return len(self.cover)

    def population_quality(self):
        """Calculate rule's quality based on population comparison."""
        population_identifier = np.zeros(shape=len(self.Dataset.DataFrame))

        subgroup_identifier = np.ones(shape=len(self.get_cover()))

        group = np.concatenate((population_identifier,
                                subgroup_identifier))

        subgroup_times = self.Dataset.survival[self.get_cover()]
        subgroup_status = self.Dataset.status[self.get_cover()]

        time = np.concatenate((self.Dataset.survival, subgroup_times))
        status = np.concatenate((self.Dataset.status, subgroup_status))

        _, pvalue = sm.duration.survdiff(time, status, group)
        return 1 - pvalue

    def complement_quality(self):
        """Calculate rule's quality based on complement comparison."""
        group = np.zeros(shape=len(self.Dataset.DataFrame))
        np.put(group, self.get_cover(), 1)

        time = self.Dataset.survival
        status = self.Dataset.status
        _, pvalue = sm.duration.survdiff(time, status, group)
        return 1 - pvalue

    def calculate_quality(self):
        """Calculate the Rule's quality according to Logrank test."""
        # Discussao:
        # 1. E se a cobertura eh vazia, onde isso deve ser testado?
        #    Por enquanto coloquei qualidade = 0 se cobertura vazia.
        # 2. Quais possiveis testes podemos fazer?
        # 3. Etapas cruciais que devem ser verificadas ao longo do caminho
        #    ateh aqui.

        self.set_cover()
        if len(self.cover) == 0:
            self.quality = 0
        else:
            if self.baseline == Baseline.COMPLEMENT:
                self.quality = self.complement_quality()
            else:
                self.quality = self.population_quality()
        return

    def __repr__(self):
        """Pretty-prints the rule."""
        return " \u2227 ".join(map(lambda x: "{} = {}".format(
            *self.Dataset.items_list[x]), self.antecedent)
        ) + " \u2192 " + str(self.quality)


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'

    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    rule = Rule(ds, Baseline.COMPLEMENT)
    for i in [1, 6, 16, 28, 38]:
        rule.add_item(i)
        rule.calculate_quality()
        print(rule)
