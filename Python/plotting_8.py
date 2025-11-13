"""
Synopsis: Plot sales amount per product category using matplotlib.

Purpose:
    Create a simple DataFrame of product categories and sales and plot the
    sales amount per category as a line chart.
"""

import pandas as pd
import matplotlib.pyplot as plt
sales_df=pd.DataFrame({'product_category':['Electronics', 'Clothing', 'Groceries', 'Furniture', 'Toys'],
                          'sales_amount':[150000, 80000, 120000, 60000, 40000]})
total_sales_df=sales_df['sales_amount'].sum()

plt.plot(sales_df['product_category'],sales_df['sales_amount'])
plt.title('Sales per Category')
plt.xlabel('Product Category')
plt.ylabel('Sales Amount')
plt.grid()
plt.show()