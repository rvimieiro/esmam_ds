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
        self.__data_path = data_path
        self.__DataFrame = None
        self.__item_map = {}
        self.items_list = []
        self.__binary_tx = []
        self.__surv_col_name = attr_survival_name
        self.__status_col_name = attr_event_name
        self.__attribute_columns = None

        self.load_dataframe()
        self.map_items()
        self.make_tx_array()

    @property
    def survival(self) -> np.array:
        return self.__DataFrame[self.__surv_col_name].values

    @property
    def status(self) -> np.array:
        return self.__DataFrame[self.__status_col_name].values

    @property
    def size(self) -> int:
        return len(self.__DataFrame)

    def load_dataframe(self) -> None:
        """Read data from data_path and store it into a pandas DataFrame.
        """
        with open(self.__data_path.split('.')[0] + '_dtypes.json', 'r') as f:
            dtypes = json.load(f)
        self.__DataFrame = pd.read_csv(self.__data_path, dtype=dtypes)
        self.map_items()

    def map_items(self) -> None:
        """Map unique items from the dataset to a int vector"""
        self.__attribute_columns = list(self.__DataFrame.columns)
        self.__attribute_columns.remove(self.__surv_col_name)
        self.__attribute_columns.remove(self.__status_col_name)

        mapped_int = 0

        for attribute in self.__attribute_columns:
            for value in self.__DataFrame[attribute].unique():
                item_reference = (attribute, value)
                self.__item_map[item_reference] = mapped_int
                self.items_list.append(item_reference)
                mapped_int += 1

    def get_item_index(self, item):
        """Return the mapped value for a item."""
        return self.__item_map[item]

    def get_number_of_items(self):
        """Return number of items in the items' map."""
        return len(self.__item_map)

    def tx_as_binary(self, tx: pd.Series) -> np.array:
        """Return tx as binary array. 
        Bits are set for the observed items at indexes set by the original mapping.
        """
        tx_items_indexes = [
            self.__item_map[(attribute, tx[attribute])]
            for attribute in self.__attribute_columns]

        tx_array = np.zeros(len(self.__item_map), dtype=int)
        tx_array.put(tx_items_indexes, 1)
        return np.packbits(tx_array)

    def make_tx_array(self) -> None:
        """Construct binary matrix of tx.
        Shape is number of tx by the number of different items.
        """
        a = self.__DataFrame.apply(
            self.tx_as_binary, axis=1)

        self.__binary_tx = np.stack(a.values, axis=0)

    def get_tx(self, items: set()) -> np.array:
        """Return all tx covered by a set of items."""
        mask = np.zeros(len(self.__item_map), dtype=int)
        mask.put(list(items), 1)

        binary_mask = np.packbits(mask)
        covered_tx = np.bitwise_and(
            binary_mask, self.__binary_tx)

        return np.nonzero(
            np.apply_along_axis(
                lambda x: np.all(np.equal(x, binary_mask)), 1,
                covered_tx))[0]

    def get_items(self, tx: np.array) -> np.array:
        """Get set of items covered by a set of tx."""
        return np.nonzero(np.unpackbits(
            np.bitwise_or.reduce(self.__binary_tx[tx])))[0]


if __name__ == "__main__":
    pwd = os.getcwd()
    path = pwd + '/datasets/actg320_disc.xz'
    ds = Dataset(path, "survival_time", "survival_status")
    # ds.load_dataframe()
    # ds.map_items()
    # ds.make_tx_array()
    print("Alles gute!")
