import pandas as pd

orders = pd.read_csv("../data/raw/orders.csv")

print("FIRST 5 ROWS")
print(orders.head())

print("\nCOLUMN NAMES")
print(orders.columns)

print("\nDATASET INFO")
print(orders.info())

print("\nMISSING VALUES")
print(orders.isnull().sum())