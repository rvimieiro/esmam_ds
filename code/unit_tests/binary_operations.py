import numpy as np

a = np.zeros(10, dtype=int)
b = np.zeros(10, dtype=int)

a.put(2, 1)
a.put(3, 1)

b.put(3, 1)
b.put(4, 1)

print(a)
print(b)

c = np.bitwise_and(np.packbits(a),
                   np.packbits(b))
print(np.unpackbits(c))
