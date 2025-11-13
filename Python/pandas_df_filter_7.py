import pandas_6 as pd

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
