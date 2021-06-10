import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame


class Dataset:
    # usando vetor de bits
    # https://numpy.org/doc/stable/reference/generated/numpy.packbits.html
    """Take original data as a DataFrame and store data (except for target columns)
    as an array of observations where each observation is an array of its attributes'
    values (except for target attributes)"""
    # interface do programa com o disco/bd/raw_data

    def __init__(self, data_path, attr_survival_name, attr_event_name):
        # pandas dataframe pra armazenar dados originais, np.array
        # para o restante do programa

        self.data_path = data_path

        self.DataFrame = None

        self.item_map = {}

        # name of column storing survival times
        self._surv_col_name = attr_survival_name

        # name of column storing censoring info
        self._event_col_name = attr_event_name

    def save_dataframe(self) -> None:
        """Read data from data_path and store it into a pandas DataFrame.
        Every value in the dataset is converted to string type."""
        self.DataFrame = pd.read_csv(self.data_path, dtype=str)

    def map_items(self) -> None:
        """Map unique items from the dataset to a int vector"""
        attribute_columns = list(self.DataFrame.columns)
        attribute_columns.remove(self._surv_col_name)
        attribute_columns.remove(self._event_col_name)

        # (?) turn into some kind of map/comprehension (?)
        mapped_int = 0
        for attribute in attribute_columns:
            for value in self.DataFrame[attribute].unique():
                self.item_map[str(attribute)+'%'+str(value)] = mapped_int
                mapped_int += 1
        # (?) turn into some kind of map/comprehension (?)

    def make_transaction_bit_array(self, verbose=False) -> np.array:
        """Make binary representation of a dataset row's attribute values"""
        self.DataFrame['bArray'] = ''
        sample_transaction = np.random.randint(0, 100)
        for item in self.item_map:
            attribute, value = item.split('%')            

            self.DataFrame.loc[self.DataFrame[attribute]
                               == value, 'bArray'] += '1'
            self.DataFrame.loc[self.DataFrame[attribute]
                               != value, 'bArray'] += '0'
            if verbose:
                print(10*'*' + ' Current Iteration ' + 10*'*')
                print()
                print("Setting bit if {} == {}".format(attribute, value))
                print()
                print(10*'*' + ' Value Count ' + 10*'*')
                print()
                print(self.DataFrame[attribute].value_counts())
                print()
                print(10*'*' + ' Sample Row ' + 10*'*')
                print()
                print(ds.DataFrame.iloc[sample_transaction])
                print(3*'\n')
                input()



if __name__ == "__main__":
    ds = Dataset("datasets/breast-cancer_disc.xz",
                 "survival_time", "survival_status")
    ds.save_dataframe()
    ds.map_items()
    ds.make_transaction_bit_array(verbose=False)

    print(ds.DataFrame)

    # sandbox
