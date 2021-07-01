from enum import Enum
from dataset_prototype import Dataset
import os


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:
    """Implement a rule. A rule is composed of an antecedent. This antecedent
    covers a subgroup and a this subgroup has an associated survival function.
    """

    def __init__(self, Dataset, Baseline):

        self._antecedent: set = set()
        self._cover = None # Poderia ser propriedade?
        self.baseline: Baseline = Baseline
        self.Dataset: Dataset = Dataset
        self.quality: float = None

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

    def __repr__(self):
        """Pretty-prints the rule."""
        str_repr = 10*'-' + ' rule ' + 10*'-'
        str_repr += '\n'
        idx = 0
        for item in self.antecedent:
            str_repr += f"${idx}: " + str(self.Dataset.items_list[item])
            str_repr += ", key: " + str(item) + "\n"
            idx += 1
        str_repr += 26*'-' + '\n'
        return str_repr


if __name__ == "__main__":
    # Criando dataset
    current_dir = os.getcwd()
    slice_index = current_dir.find('code_prototypes')
    path = current_dir[:slice_index] + 'datasets/actg320_disc.xz'

    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    # Criando uma regra
    regra = Rule(ds, Baseline.POPULATION)
    regra.add_item(ds.item_map[('tx', '0')])
    regra.add_item(ds.item_map[(('karnof', '90'))])
    regra.add_item(ds.item_map[('age', '[32.00,35.00)')])
    regra.set_cover()

    print(regra)
    print(regra.get_cover())
