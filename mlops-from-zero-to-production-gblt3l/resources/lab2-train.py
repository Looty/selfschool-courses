"""Stage 2 of the lab 2 pipeline: train on data/clean.csv, write models/model.pkl and metrics.json."""
import json
import os
import pickle

import pandas as pd
import yaml
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

params = yaml.safe_load(open("params.yaml"))["train"]
df = pd.read_csv("data/clean.csv")
X, y = df.drop(columns="churned"), df["churned"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=params["seed"])

model = LogisticRegression(C=params["C"], max_iter=500).fit(X_train, y_train)
accuracy = accuracy_score(y_test, model.predict(X_test))

os.makedirs("models", exist_ok=True)
pickle.dump(model, open("models/model.pkl", "wb"))
json.dump({"accuracy": accuracy}, open("metrics.json", "w"))
print(f"C={params['C']} accuracy={accuracy:.3f}")
