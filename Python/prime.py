"""
Logic:
    Provide a small `is_prime` function that returns True for prime numbers
    and False otherwise. The script reads an integer from input and prints
    the boolean result.
"""

def is_prime(n):
    if n <= 1:
        return False
    else:
        for i in range(2, int((n**0.5)) + 1):
            if n % i == 0:
                return False
        else:
            return True
print(is_prime(int(input("Enter the number: "))))