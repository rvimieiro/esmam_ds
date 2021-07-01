import numpy as np

from enum import Enum
from dataset_prototype import Dataset


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:

    def __init__(self, Dataset, Baseline):

        self.antecedent: set = set()
        self.cover = None
        self.baseline: Baseline = Baseline
        self.Dataset: Dataset = Dataset
        self.quality: int = None

    def get_antecedent(self) -> set:
        return self.antecedent

    def add_item_to_antecedent(self, item: int) -> None:
        self.antecedent.add(item)

    def remove_item_from_antecedent(self, item: tuple) -> None:
        self.antecedent.remove(item)

    def set_cover(self):
        self.cover = self.Dataset.get_transactions(self.antecedent)

    def get_cover(self):
        return self.cover

    def get_cover_size(self):
        return len(self.cover)

    def __repr__(self):
        formatted = str(self.antecedent)
        return formatted

    def __str__(self):
        formatted = str(self.antecedent)
        return formatted


if __name__ == "__main__":
    # Criando dataset
    path = '/home/pedro/code/esmam/esmam_algorithm/esmam_ds/code/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    # Criando uma regra
    regra = Rule(ds, Baseline.POPULATION)
    regra.add_item_to_antecedent(ds.item_map[('tx', '0')])
    regra.add_item_to_antecedent(ds.item_map[(('karnof', '90'))])
    regra.add_item_to_antecedent(ds.item_map[('age', '[32.00,35.00)')])
    regra.set_cover()

    print(regra)
    print(regra.get_cover())
