"""
Logic:
    - Accept a list of integers from the user.
    - Check each number to determine if it is even.
    - Collect all even numbers and sort them in descending order.
"""

def is_even(n):
        if n % 2 == 0:
            return True
        else:
            return False

n=list(map(int, input("Enter numbers separated by spaces: ").split()))
even_list=[]
for num in n:
    if is_even(num):
        even_list.append(num)
print("Even numbers are:", sorted(even_list, reverse=True))