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
        self._cover = None
        self._antecedent: set = set()
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
        """Add item to antecedent. The item is referred by its integer index
        in the Dataset's class item_map.
        """
        self._antecedent.add(item)

    def remove_item(self, item: tuple) -> None:
        """Remove item of the antecedent. The item is referred by its
        integer-valued index in the Dataset's class item_map.
        """
        self._antecedent.remove(item)
        # recalcular qualidade

    def set_cover(self) -> None:
        """Set the rule cover. A rule's cover is defined as the set of
        transactions where each transaction contain, at least,
        every item of the antecedent."""
        self.cover = self.Dataset.get_transactions(self.antecedent)

    def get_cover(self):
        """Return Rule's cover."""
        return self.cover

    def get_cover_size(self) -> int:
        """Return the size of a Rule's cover."""
        return len(self.cover)

    def __population_quality(self) -> float:
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

    def __complement_quality(self) -> float:
        """Calculate rule's quality based on complement comparison."""
        group = np.zeros(shape=len(self.Dataset.DataFrame))
        np.put(group, self.get_cover(), 1)

        time = self.Dataset.survival
        status = self.Dataset.status
        _, pvalue = sm.duration.survdiff(time, status, group)
        return 1 - pvalue

    def quality(self) -> float:
        """Calculate the Rule's quality according to Logrank test."""
        self.set_cover()
        if len(self.cover) == 0:
            return 0
        else:
            if self.baseline == Baseline.COMPLEMENT:
                return self.__complement_quality()
            else:
                return self.__population_quality()

    def __repr__(self) -> str:
        """Pretty-prints the rule."""
        return " \u2227 ".join(map(lambda x: "{} = {}".format(
            *self.Dataset.items_list[x]), self.antecedent)
        ) + " \u2192 " + str(self.quality())


if __name__ == "__main__":

    pwd = os.getcwd()
    path = pwd + '/datasets/breast-cancer_disc.xz'

    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    rule = Rule(ds, Baseline.COMPLEMENT)
    # for i in [1, 6, 16, 28, 38]:
    # rule.add_item(i)
    # print(rule)
    rule.add_item(6)
    print(rule)