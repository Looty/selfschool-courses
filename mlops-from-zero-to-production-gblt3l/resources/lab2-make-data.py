"""Lab 2: creates data/raw.csv, a small made-up customer table (no download needed).

Run:  python lab2-make-data.py
Edit it later (change the seed or the row count) to produce a second "version" of the data.
"""
import csv
import os
import random

random.seed(1)
os.makedirs("data", exist_ok=True)
with open("data/raw.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["age", "monthly_spend", "support_calls", "churned"])
    for _ in range(500):
        age = random.randint(18, 75)
        spend = round(random.uniform(10, 200), 2)
        calls = random.randint(0, 8)
        churn_score = 0.08 * calls - 0.004 * spend + random.uniform(-0.3, 0.3)
        w.writerow([age, spend, calls, int(churn_score > 0.1)])
print("wrote data/raw.csv")
