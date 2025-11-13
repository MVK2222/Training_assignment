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