"""Lab 1: track a scikit-learn training run with MLflow. Runs offline.

Setup:   uv venv && uv pip install mlflow scikit-learn
Run:     python lab1-mlflow-train.py            (then again with: python lab1-mlflow-train.py 2)
View:    mlflow ui --port 5000   then open http://localhost:5000
"""
import sys

import mlflow
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

max_iter = int(sys.argv[1]) if len(sys.argv) > 1 else 200
params = {"solver": "lbfgs", "max_iter": max_iter, "random_state": 8888}

X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

mlflow.set_experiment("MLflow Quickstart")

with mlflow.start_run():
    mlflow.log_params(params)
    lr = LogisticRegression(**params).fit(X_train, y_train)
    accuracy = accuracy_score(y_test, lr.predict(X_test))
    mlflow.log_metric("accuracy", accuracy)
    mlflow.set_tag("Training Info", "Basic LR model for iris data")
    model_info = mlflow.sklearn.log_model(sk_model=lr, name="iris_model")
    print(f"max_iter={max_iter} accuracy={accuracy:.3f}")

loaded = mlflow.pyfunc.load_model(model_info.model_uri)
print("first 5 predictions:", loaded.predict(X_test)[:5])
