from numpy.core.fromnumeric import shape
import pandas as pd
import numpy as np
import json as json


class Dataset:
    """Take original data as a DataFrame and store data (except for target columns)
    as an array of observations where each observation is an array of its attributes'
    values (except for target attributes)"""

    def __init__(self, data_path, attr_survival_name, attr_event_name):
        self.data_path = data_path
        self.DataFrame = None
        self.item_map = {}
        self.indexed_keys = []
        self.binary_transactions = []
        self._surv_col_name = attr_survival_name
        self._status_col_name = attr_event_name
        self.attribute_columns = None

    @property
    def survival(self) -> np.array:
        return self.DataFrame[self._surv_col_name].values

    @property
    def status(self) -> np.array:
        return self.DataFrame[self._status_col_name].values

    def load_dataframe(self) -> None:
        """Read data from data_path and store it into a pandas DataFrame.
        Every value in the dataset is converted to string type."""
        with open(self.data_path.split('.')[0] + '_dtypes.json', 'r') as f:
            dtypes = json.load(f)
        self.DataFrame = pd.read_csv(self.data_path, dtype=dtypes)

    def map_items(self) -> None:
        """Map unique items from the dataset to a int vector"""
        self.attribute_columns = list(self.DataFrame.columns)
        self.attribute_columns.remove(self._surv_col_name)
        self.attribute_columns.remove(self._status_col_name)

        mapped_int = 0

        for attribute in self.attribute_columns:
            for value in self.DataFrame[attribute].unique():

                item_reference = (attribute, value)
                self.item_map[item_reference] = mapped_int
                self.indexed_keys.append(item_reference)
                mapped_int += 1

    def get_item_index(self, item):
        return self.item_map[item]

    def get_number_of_items(self):
        return len(self.item_map)

    def transaction_as_binary(self, transaction: pd.Series) -> np.array:
        """Return transaction as binary array. 
        Bits are set for the observed items at indexes set by the original mapping.
        """
        transaction_items_indexes = [
            self.item_map[(attribute, transaction[attribute])]
            for attribute in self.attribute_columns
        ]

        transaction_array = np.zeros(len(self.item_map), dtype=int)
        transaction_array.put(transaction_items_indexes, 1)
        return np.packbits(transaction_array)

    def make_transaction_array(self) -> None:
        """Construct binary matrix of transactions.
        Shape is number of transactions by the number of different items.
        """
        a = self.DataFrame.apply(
            self.transaction_as_binary, axis=1
        )
        self.binary_transactions = np.stack(a.values, axis=0)

    def get_transactions_by_item(self, item: tuple) -> np.array:
        """Return all transactions having the item."""

        item_idx = self.item_map[item]

        binary_mask = np.zeros(len(self.item_map), dtype=int)
        binary_mask.put(item_idx, 1)
        binary_mask = np.packbits(binary_mask)

        covered_transactions = np.bitwise_and(
            binary_mask, self.binary_transactions
        )

        return np.nonzero(covered_transactions)[0]

    def get_transactions(self, items: set()) -> np.array:
        mask = np.zeros(len(self.item_map), dtype=int)
        mask.put(list(items), 1)
        binary_mask = np.packbits(mask)
        covered_transactions = np.bitwise_and(
            binary_mask, self.binary_transactions
        )
        return np.nonzero(
            np.apply_along_axis(lambda x: np.all(np.equal(x, binary_mask)),
                                1, covered_transactions)
        )[0]

    def get_items(self, transactions: np.array) -> np.array:
        """Get set of items covered by a set of transactions."""
        return np.nonzero(np.unpackbits(
            np.bitwise_or.reduce(self.binary_transactions[transactions])
        ))[0]


if __name__ == "__main__":
    path = '/home/pedro/code/esmam/esmam_algorithm/esmam_ds/code/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_transaction_array()

    # print(ds.item_map)
    items = set([0])
    print(len(ds.get_transactions(items)))
    # print(ds.DataFrame.iloc[1])
    print(ds.DataFrame.query("tx == '0'"))
