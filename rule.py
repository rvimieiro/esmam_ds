from enum import Enum
from dataset import Dataset
import statsmodels.api as sm
import os


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:
    """Implement a rule. A rule is composed of an antecedent. This antecedent
    covers a subgroup and a this subgroup has an associated cover_survival function.
    """

    def __init__(self, Dataset, Baseline):

        self._antecedent: set = set()
        self._cover = None  # Poderia ser propriedade?
        self.quality: float = None
        self.baseline: Baseline = Baseline
        self.Dataset: Dataset = Dataset

    @property
    def antecedent(self) -> set:
        """Get the Rule antecedent."""
        return self._antecedent

    @antecedent.setter
    def antecedent(self, new_antecedent: set):
        """Aqui eu poderia colocar a funcionalidade de acionar um item
        ao antecedente ou deveria ser substituicao total do antecedente?"""
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
        """Set the rule cover. A rule's cover is defined as the set of transactions
        where each transaction contain, at least, every item of the antecedent."""
        self.cover = self.Dataset.get_transactions(self.antecedent)

    def get_cover(self):
        """Return Rule's cover."""
        return self.cover

    def get_cover_size(self):
        """Return the size of a Rule's cover."""
        return len(self.cover)

    def calculate_quality(self):
        """Calculate the Rule's quality according to Logrank test."""
        self.set_cover()
        cover = self.get_cover()

        cover_survival = self.Dataset.survival
        cover_survival = cover_survival[cover]

        cover_status = self.Dataset.status
        cover_status = cover_status[cover]

        if self.baseline == Baseline.POPULATION:
            pass
        else:
            pass

        print('\nCover\n')
        print(cover)
        print('\nSurvival\n')
        print(cover_survival)
        print('\nStatus\n')
        print(cover_status)
        pass

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

    # Criando uma regra
    regra = Rule(ds, Baseline.POPULATION)
    regra.add_item(ds.item_map[('tx', '0')])
    regra.add_item(ds.item_map[(('karnof', '90'))])
    regra.add_item(ds.item_map[('age', '[32.00,35.00)')])

    print(regra)

    regra.calculate_quality()