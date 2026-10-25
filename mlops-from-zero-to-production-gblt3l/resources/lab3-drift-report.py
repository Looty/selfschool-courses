"""Lab 3: detect data drift with Evidently on made-up data. Runs offline.

Setup:   uv venv && uv pip install evidently numpy "pandas<2.3"   (tested with pandas 2.2; newest pandas breaks Evidently's import)
Run:     python lab3-drift-report.py
Output:  drift_report.html (open it in a browser) and a printed share of drifted columns.
"""
import numpy as np
import pandas as pd
from evidently import DataDefinition, Dataset, Report
from evidently.presets import DataDriftPreset

rng = np.random.default_rng(0)


def make(n, age_mean, countries, probs):
    return pd.DataFrame(
        {
            "age": rng.normal(age_mean, 8, n).round(),
            "monthly_spend": rng.gamma(4, 20, n).round(2),
            "country": rng.choice(countries, n, p=probs),
        }
    )


reference = make(2000, 40, ["IL", "US", "DE"], [0.5, 0.3, 0.2])
# "Production" has older customers and a country that was never in the reference.
current = make(2000, 52, ["IL", "US", "DE", "FR"], [0.3, 0.3, 0.1, 0.3])

schema = DataDefinition(numerical_columns=["age", "monthly_spend"], categorical_columns=["country"])
cur_ds = Dataset.from_pandas(current, data_definition=schema)
ref_ds = Dataset.from_pandas(reference, data_definition=schema)

report = Report([DataDriftPreset()])
result = report.run(cur_ds, ref_ds)  # current first, reference second
result.save_html("drift_report.html")

as_dict = result.dict()
print("saved drift_report.html")
for m in as_dict.get("metrics", []):
    print(m.get("metric_name", m.get("metric_id")), "->", m.get("value"))
