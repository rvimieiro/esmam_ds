from dataset_prototype import Dataset
import os

datasets_files = os.listdir("datasets")
dataset_paths = []
for file in datasets_files:
    if file[-2:] == "xz":
        dataset_paths.append(file)

for dataset_path in dataset_paths:
    path = "datasets/" + dataset_path
    ds = Dataset(path, "survival_time", "survival_status")
    ds.save_dataframe()
    ds.map_items()
    ds.make_transaction_bit_array_BY_ITEMS(verbose=True)
    print(10*"\n", " -- Dataset {} -- \n".format(dataset_path))
    print(" -- Binary transactions array -- \n")
    print(ds.binary_transactions)
    print("\n $ Binary transactions shape:", ds.binary_transactions.shape)
    print("\n $ Number of transactions in the dataset:", ds.DataFrame.shape[0])
    print("\n $ Number of attributes in the dataset:", ds.DataFrame.shape[1])
    print("\n $ Number of generated  items:", len(ds.indexed_list), 10*"\n")

    input()
