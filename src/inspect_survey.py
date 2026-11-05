import pandas as pd

file_path = "data/raw/responses.csv"

df = pd.read_csv(file_path)

print("DATASET SHAPE:")
print(df.shape)

print("\nCOLUMN NAMES:")
print(df.columns.tolist())

print("\nFIRST 5 ROWS:")
print(df.head())

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDUPLICATE ROWS:")
print(df.duplicated().sum())
