import os
import numpy as np
from enum import Enum
import statsmodels.api as sm
import dataset


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:
    """Implement a rule. A rule is composed of an antecedent. This antecedent
    covers a subgroup with an associated cover_survival function.
    """

    def __init__(self, Dataset, Baseline):
        self._antecedent: set = set()
        self.baseline: Baseline = Baseline
        self.Dataset: Dataset = Datase
        self._is_updated = True
        self._cover = np.arange(self.Dataset.DataFrame.shape[0])

    @property
    def antecedent(self) -> set:
        return self._antecedent

    @antecedent.setter
    def antecedent(self, new_antecedent: set):
        self._antecedent = new_antecedent

    def __eq__(self, o: object) -> bool:
        """Compare two rules for equality."""
        if not isinstance(o, Rule):
            return NotImplemented
        return self._antecedent == o._antecedent

    def add_item(self, item: int) -> None:
        """Add item to antecedent. The item is referred by its integer index
        in the Dataset's class item_map.
        """
        self._antecedent.add(item)
        self._is_updated = False

    def remove_item(self, item: tuple) -> None:
        """Remove item of the antecedent. The item is referred by its
        integer-valued index in the Dataset's class item_map.
        """
        self._antecedent.remove(item)
        self._is_updated = False

    def set_cover(self) -> None:
        """Set the rule cover. A rule's cover is defined as the set of
        tx where each tx contain, at least,
        every item of the antecedent."""
        self._cover = self.Dataset.get_tx(self.antecedent)
        self._is_updated = True

    def get_cover(self):
        """Return Rule's cover."""
        if self._is_updated:
            return self._cover
        else:
            self.set_cover()
            return self._cover

    def get_cover_size(self) -> int:
        """Return size of a Rule's cover."""
        if self._is_updated:
            return len(self._cover)
        else:
            self.set_cover()
            return len(self._cover)

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
        if self.get_cover_size() == 0:
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

    # Path related trickery
    pwd = os.getcwd()
    path = pwd + '/datasets/breast-cancer_disc.xz'

    # Initialize dataset class and load the data
    # once again, should it not load everything up when __init__ happens?
    ds = dataset.Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_tx_array()

    # Instatiate a rule object
    rule = Rule(ds, Baseline.COMPLEMENT)
    # We add a item to it
    rule.add_item(6)

    # Now another rule object
    another_rule = Rule(ds, Baseline.COMPLEMENT)
    # We add the same item to it
    another_rule.add_item(6)
    another_rule.add_item(10)

    rule.set_cover()
    another_rule.set_cover()

    print(rule)
    print(another_rule)

    print("Are the rules different?", rule != another_rule)
