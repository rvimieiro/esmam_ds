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

    def load_dataframe(self) -> None:
        """Read data from data_path and store it into a pandas DataFrame.
        Every value in the dataset is converted to string type."""
        with open(self.data_path.split('.')[0] + '_dtypes.json', 'r') as f:
            dtypes = json.load(f)
        self.DataFrame = pd.read_csv(self.data_path, dtype=dtypes)

    @property
    def survival(self) -> np.array:
        return self.DataFrame[self._surv_col_name].values

    @property
    def status(self) -> np.array:
        return self.DataFrame[self._status_col_name].values

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

    def get_transactions_by_mask(self, mask: np.array) -> np.array:
        """Not functional.
        I would like to make an 'abstract' bit-array-wise-and with an array
        and the transactions array. I would like to get every transaction which
        contains these three items in conjunction."""

        binary_mask = np.packbits(mask)
        print(binary_mask)
        covered_transactions = np.bitwise_and(
            binary_mask, self.binary_transactions
        )
        # print(np.nonzero(covered_transactions)[0])

        return np.nonzero(np.apply_along_axis(lambda x: np.all(
            np.equal(x, binary_mask)),
            1, covered_transactions))[0]

        np.apply_along_axis(lambda x: np.all(
            np.equal(x, binary_mask)), 1, covered_transactions)

    def get_transactions_by_items(self, items: list) -> np.array:
        """Does what I would like to do in 'get_transactions_by_mask
        in a Gambiarra fashion.
        Given a list of items, return every transaction containing these items
        in conjunction."""
        item_idxs = [self.item_map[item] for item in items]

        transactions_sets = []
        # for each item, store a set of its covered transactions

        covered_transactions_by_item_idxs = None
        for item_idx in item_idxs:

            binary_mask = np.zeros(len(self.item_map), dtype=int)
            binary_mask.put(item_idx, 1)
            binary_mask = np.packbits(binary_mask)

            covered_transactions_by_item_idxs = np.bitwise_and(
                binary_mask, self.binary_transactions
            )

            covered_transactions_by_item_idxs = np.nonzero(
                covered_transactions_by_item_idxs
            )[0]

            this_set_of_transactions = set()
            this_set_of_transactions.update(covered_transactions_by_item_idxs)

            transactions_sets.append(this_set_of_transactions)

        resulting_set = set()
        resulting_set.update(transactions_sets.pop())

        # passar intersecao para dentro do laco
        for idx_set in transactions_sets:
            resulting_set = resulting_set.intersection(idx_set)

        return resulting_set

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
    mask = np.zeros(len(ds.item_map), dtype=int)
    mask[0] = 1
    print(ds.indexed_keys[5])
    # mask[20] = 1
    print(ds.get_transactions_by_mask(mask))
    print(ds.DataFrame.query(
            # "tx == '0' and karnof == '90' and age == '[32.00,35.00)'"
            "tx == '0'"
        ))
    # print('\nActg320 dataset original shape (with survival data):', ds.DataFrame.shape)
    # print('Total number of items:', len(ds.item_map))
    # print('Binary data shape:', ds.binary_transactions.shape, '\n')
    # print('Binary transactions:\n')
    # print(ds.binary_transactions, '\n')

    # print(ds.status)

    # with open('simple_log.txt', 'a') as file:
    #     for item in ds.item_map:
    #         file.write(
    #             'Item {} covers {} transactions.\n'.format(
    #                 item, len(
    #                     ds.get_transactions_by_item(item))
    #             )
    #         )

    # with open('fancy_log.txt', 'a') as file:
    #     for item in ds.item_map:
    #         file.write(
    #             str(ds.get_transactions_by_item(item))
    #         )

    with open('item_query.txt', 'w') as file:
        query = ds.DataFrame.query(
            # "tx == '0' and karnof == '90' and age == '[32.00,35.00)'"
            "txgrp == '3'"
        )
        file.write(str(query))
