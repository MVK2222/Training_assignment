"""
Logic:
    - Accept a space-separated string from the user.
    - Convert the string into a tuple.
    - Convert the tuple into a set and sort it.
"""

str_list = input("Enter the string: ").split()
print(type(str_list))

tup=tuple(str_list)
print("\n")
print(type(tup))
print("\n")
print("================================")
print("Tuple:", tup)
print("================================")
set1=set(tup)
print("\n")
print(type(set1))
print("\n")
print("================================")
print("Set:", sorted(set1))
print("================================")
