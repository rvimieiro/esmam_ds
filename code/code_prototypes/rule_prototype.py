import numpy as np

from enum import Enum
from dataset_prototype import Dataset


class Baseline(Enum):
    POPULATION = 1
    COMPLEMENT = 2


class Rule:
    """
    funcionalidades:
    3. calcular a qualidade
    """

    def __init__(self, Dataset, Baseline):

        # melhor deixar somente como List
        self.antecedent: set = set()
        self.cover = None
        self.baseline = Baseline
        self.Dataset = Dataset  # referencia, correto?
        self.quality = 0.0


    def get_antecedent(self) -> set:
        return self.antecedent

    def add_item_to_antecedent(self, item: int) -> None:
        self.antecedent.add(item)

    def remove_item_from_antecedent(self, item: tuple) -> None:
        self.antecedent.remove(item)

    def get_cover(self):
        return self.Dataset.get_transactions_by_items(self.antecedent_items)

    def get_cover_size(self):
        return len(self.Dataset.get_transactions_by_items(self.antecedent_items))

    def __repr__(self):
        formatted = str(self.antecedent)
        formatted = str(self.antecedent_items)
        formatted += '\n'
        formatted += str(self.baseline)
        return formatted

    def __str__(self):
        formatted = str(self.antecedent)
        formatted = str(self.antecedent_items)
        formatted += '\n'
        formatted += str(self.baseline)
        return formatted


if __name__ == "__main__":
    # Criando dataset
    path = '/home/pedro/code/esmam/esmam_algorithm/esmam_ds/code/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    ds.save_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    # Criando uma regra
    regra = Rule(ds, Baseline.POPULATION)
    regra.add_item_to_antecedent(('tx', '0'))
    regra.add_item_to_antecedent(('karnof', '90'))
    regra.add_item_to_antecedent(('age', '[32.00,35.00)'))

    ds.get_transactions_by_mask(regra.antecedent)

    # print(regra)
    # print(regra.get_cover())
    # print(regra.get_cover_size())
