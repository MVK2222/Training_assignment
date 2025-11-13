import numpy as np

num=np.arange(1,26)
met=np.matrix(num.reshape(5,5))
print("numners from 1 to 25",num)
print("\n")
print("===========5x5 matrix============")
print(met)

print("\n")
print("Diagonal elements are:",met.diagonal())
print("\n")
print("Sum of all diagonal elements:",met.diagonal().sum())