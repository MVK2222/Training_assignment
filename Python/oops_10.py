"""
Logic:
    - Define a BankAccount class with private balance.
    - Implement deposit and withdraw methods with validation.
    - Provide a method to retrieve the current balance.
"""

class BankAccount:
    def __init__(self, account_holder, balance=0):
        self.account_holder = account_holder
        self.__balance = balance
    def deposit(self, amount):
        if amount > 0:
            self.__balance +=amount
            print(f"Deposited: {amount}. New Balance: {self.__balance}")
        else:
            print("Deposit amount must be positive.")
    def withdraw(self, amount):
        if 0 < amount < self.__balance:
            self.__balance -= amount
            print(f"Withdrew: {amount}. New Balance: {self.__balance}")
        else:
            print("Insufficient funds or invalid withdrawal amount.")
    def get_balance(self):
        return self.__balance

acc1=BankAccount("Mohan", 1000)
acc1.deposit(500)
acc1.withdraw(20)
acc1.get_balance()