"""Stage 1 of the lab 2 pipeline: clean data/raw.csv into data/clean.csv."""
import pandas as pd

df = pd.read_csv("data/raw.csv").dropna()
df = df[(df["age"] >= 18) & (df["monthly_spend"] > 0)]
df.to_csv("data/clean.csv", index=False)
print(f"clean rows: {len(df)}")
