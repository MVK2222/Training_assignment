"""
Synopsis: Create an employee DataFrame and filter by salary percentage.

Purpose:
    Build a pandas DataFrame of employees with Salary, compute each employee's
    percentage of total salary, and print rows with Percentage > 75.

"""

import pandas as pd

employee_df=pd.DataFrame({
    'Name':['Mohan', 'Veeru', 'Hareesh', 'Prany', 'Ajay'],
    'Department':['IT Data', 'IT Testing', 'HR', 'Finance', 'IT Data'],
    'Salary':[40000, 50000, 30000, 1000000, 75000]
})
employee_df['Percentage']=employee_df['Salary']/employee_df['Salary'].sum()*100
filter_df=employee_df[employee_df['Percentage']>75]
print(employee_df)
print("\n")
print("================================")
print(filter_df)
print("================================")