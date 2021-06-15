import numpy as np

a = np.array([1, 0, 1, 0, 1, 0, 1, 0])
print(a)

b = np.packbits(a)
print(b)

c = np.unpackbits(np.packbits(a))
print(c)


n_items = 10
tran_x = np.zeros(n_items)