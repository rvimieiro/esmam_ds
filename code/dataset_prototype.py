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

        self._event_col_name = attr_event_name
        # status mudar

        self.attribute_columns = None

    def save_dataframe(self) -> None:
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
        return self.DataFrame[self._event_col_name].values

    def map_items(self) -> None:
        """Map unique items from the dataset to a int vector"""
        self.attribute_columns = list(self.DataFrame.columns)
        self.attribute_columns.remove(self._surv_col_name)
        self.attribute_columns.remove(self._event_col_name)

        mapped_int = 0

        for attribute in self.attribute_columns:
            for value in self.DataFrame[attribute].unique():

                item_reference = (attribute, value)
                self.item_map[item_reference] = mapped_int
                self.indexed_keys.append(item_reference)
                mapped_int += 1

    def deprecated_make_transaction_bit_array(self, verbose=False):
        """Make binary representation of a dataset row's attribute values"""
        skip = 'placeholder'
        construction_iteration = 0

        self.DataFrame['bArray'] = ''
        sample_transaction = np.random.randint(0, 100)

        for attribute, value in self.item_map:
            construction_iteration += 1

            self.DataFrame.loc[self.DataFrame[attribute]
                               == value, 'bArray'] += '1'
            self.DataFrame.loc[self.DataFrame[attribute]
                               != value, 'bArray'] += '0'

            if verbose and skip != 's':
                lines_to_print = int(15)
                print(lines_to_print*'\n')
                print(
                    10*'*' + f' Iteration {construction_iteration} ' + 10*'*')
                print()
                print("Setting bit if {} == {}".format(attribute, value))
                print()
                print(10*'*' + ' Value Count ' + 10*'*')
                print()
                print(self.DataFrame[attribute].value_counts())
                print()
                print(10*'*' + ' Sample Row ' + 10*'*')
                print()
                print(self.DataFrame.iloc[sample_transaction])
                print()
                print(int(lines_to_print / 2) * '\n')
                skip = input(
                    "Enter 's' to stop printing this dataset transactions array construction..."
                )

        self.DataFrame['bArray'] = self.DataFrame['bArray'].apply(
            lambda x: (list(map(int, x)))
        )

        self.binary_transactions = np.array(self.DataFrame['bArray'].tolist())
        # self.binary_transactions = np.array(self.DataFrame['bArray'].values)
        self.DataFrame = self.DataFrame.drop('bArray', axis=1)

    def transaction_as_binary(self, transaction: pd.Series) -> None:
        """Append representation of transaction as binary array
        to binary_transactions list. Bits are set for the observed items
        at indexes set by the original mapping.
        """
        transaction_items_indexes = [
            self.item_map[(attribute, transaction[attribute])]
            for attribute in self.attribute_columns
        ]

        transaction_array = np.zeros(len(self.item_map), dtype=int)
        transaction_array.put(transaction_items_indexes, 1)
        # self.binary_transactions.append(np.packbits(transaction_array))
        return np.packbits(transaction_array)
        # self.binary_transactions.append(np.packbits(transaction_array))

    def make_transaction_array(self) -> None:
        """Construct binary matrix of transactions.
        Shape is number of transactions by the number of different items.
        """
        a = self.DataFrame.apply(
            self.transaction_as_binary, axis=1
        )
        print(type(a.values))
        # self.binary_transactions = np.array(self.binary_transactions)
        self.binary_transactions = np.stack(a.values, axis=0)

    # def get_indexes_of_transactions_covered_by_item(self, item: tuple) -> np.array:
    def get_transactions(self, item: tuple) -> np.array:
        """Just to show that it works."""

        item_idx = self.item_map[item]

        binary_mask = np.zeros(len(self.item_map), dtype=int)
        binary_mask.put(item_idx, 1)
        binary_mask = np.packbits(binary_mask)

        covered_transactions = np.bitwise_and(
            binary_mask, ds.binary_transactions)
        return np.nonzero(covered_transactions)[0]

    # def get_items_covered_by_transactions(self, transactions: np.array) -> np.array:
    def get_items(self, transactions: np.array) -> np.array:
        """Get set of items covered by a set of transactions."""
        return np.nonzero(np.unpackbits(np.bitwise_or.reduce(self.binary_transactions[transactions])))[0]


if __name__ == "__main__":
    path = 'datasets/{}_disc.xz'.format('actg320')
    ds = Dataset(path, "survival_time", "survival_status")
    ds.save_dataframe()
    ds.map_items()
    ds.make_transaction_array()
    print('\nActg320 dataset original shape (with survival data):', ds.DataFrame.shape)
    print('Total number of items:', len(ds.item_map))
    print('Binary data shape:', ds.binary_transactions.shape, '\n')
    print('Binary transactions:\n')
    print(ds.binary_transactions, '\n')

    print(ds.status)

    # with open('simple_log.txt', 'a') as file:
    #     for item in ds.item_map:
    #         file.write(
    #             'Item {} covers {} transactions.\n'.format(
    #                 item, len(
    #                     ds.get_indexes_of_transactions_covered_by_item(item))
    #             )
    #         )

    # with open('fancy_log.txt', 'a') as file:
    #     for item in ds.item_map:
    #         file.write(
    #             str(ds.get_indexes_of_transactions_covered_by_item(item))
    #         )
