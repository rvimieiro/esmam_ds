import json as json
import os

import numpy as np
import pandas as pd


class Dataset:
    """Take original data as a DataFrame and store data (except for target columns)
    as an array of observations where each observation is an array of its attributes'
    values (except for target attributes).
    """

    def __init__(self, data_path: str, attr_survival_name: str, attr_event_name: str):
        self.data_path = data_path
        self.DataFrame = None
        self.item_map = {}
        self.items_list = []
        self.binary_tx = []
        self._surv_col_name = attr_survival_name
        self._status_col_name = attr_event_name
        self.attribute_columns = None

    @property
    def survival(self) -> np.array:
        return self.DataFrame[self._surv_col_name].values

    @property
    def status(self) -> np.array:
        return self.DataFrame[self._status_col_name].values

    @property
    def size(self) -> int:
        return len(self.DataFrame)

    def load_dataframe(self) -> None:
        """Read data from data_path and store it into a pandas DataFrame.
        Every value in the dataset is converted to string type.
        """
        with open(self.data_path.split('.')[0] + '_dtypes.json', 'r') as f:
            dtypes = json.load(f)
        self.DataFrame = pd.read_csv(self.data_path, dtype=dtypes)
        self.map_items()

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
                self.items_list.append(item_reference)
                mapped_int += 1

    def get_item_index(self, item):
        """Return the mapped value for a item."""
        return self.item_map[item]

    def get_number_of_items(self):
        """Return number of items in the items' map."""
        return len(self.item_map)

    def tx_as_binary(self, tx: pd.Series) -> np.array:
        """Return tx as binary array. 
        Bits are set for the observed items at indexes set by the original mapping.
        """
        tx_items_indexes = [
            self.item_map[(attribute, tx[attribute])]
            for attribute in self.attribute_columns
        ]
        tx_array = np.zeros(len(self.item_map), dtype=int)
        tx_array.put(tx_items_indexes, 1)
        return np.packbits(tx_array)

    def make_tx_array(self) -> None:
        """Construct binary matrix of tx.
        Shape is number of tx by the number of different items.
        """
        a = self.DataFrame.apply(
            self.tx_as_binary, axis=1
        )
        self.binary_tx = np.stack(a.values, axis=0)

    def get_tx(self, items: set()) -> np.array:
        """Return all tx covered by a set of items."""
        mask = np.zeros(len(self.item_map), dtype=int)
        mask.put(list(items), 1)

        binary_mask = np.packbits(mask)
        covered_tx = np.bitwise_and(
            binary_mask, self.binary_tx
        )

        return np.nonzero(
            np.apply_along_axis(
                lambda x: np.all(np.equal(x, binary_mask)), 1,
                covered_tx
            )
        )[0]

    def get_items(self, tx: np.array) -> np.array:
        """Get set of items covered by a set of tx."""
        return np.nonzero(np.unpackbits(
            np.bitwise_or.reduce(self.binary_tx[tx])
        ))[0]


if __name__ == "__main__":
    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    ds.load_dataframe()
    ds.map_items()
    ds.make_tx_array()
    print('all good')
