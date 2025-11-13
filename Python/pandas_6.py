import pandas_6 as pd

temperature_list=[23, 25, 19, 30, 22, 27, 21, 24, 26, 28]
temperature_series=pd.Series(temperature_list)
print("================================")
print("Temperature Series:\n", temperature_series)
print("================================")
print("Temperature Series:\n", temperature_series)
print("\n")
cels_to_fahe=[]
for i in temperature_series:
    f=(i * 9/5) + 32
    cels_to_fahe.append(f)
fahe_series=pd.Series(cels_to_fahe)
print("===============================")
print("Fahrenheit Series:\n", fahe_series)
print("================================")
