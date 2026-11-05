"""Step 2: train three baseline models with a split by run (no data leakage).

Usage:
    python src/training/train.py --input data/processed/synthetic_clean.csv
"""
import argparse
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

FEATURES = ["cache_references", "cache_misses", "instructions", "cpu_cycles", "miss_rate"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=None)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    tag = "synthetic_" if "synthetic" in os.path.basename(a.input).lower() else ""
    if tag:
        print("WARNING: SYNTHETIC DATA. Results only test the code, not real detection.")

    df = pd.read_csv(a.input)
    X, y, groups = df[FEATURES], df["label"], df["run_id"]

    # Split by run: all samples of one run stay on the same side.
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=a.seed)
    tr, te = next(splitter.split(X, y, groups))
    train_runs = sorted(groups.iloc[tr].unique().tolist())
    test_runs = sorted(groups.iloc[te].unique().tolist())
    assert not set(train_runs) & set(test_runs), "Leakage: a run is in both train and test"
    print(f"Train runs: {len(train_runs)} | Test runs: {len(test_runs)}")

    models = {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Decision Tree": make_pipeline(StandardScaler(), DecisionTreeClassifier(max_depth=4, random_state=a.seed)),
        "Random Forest": make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=100, random_state=a.seed)),
    }
    for name, m in models.items():
        m.fit(X.iloc[tr], y.iloc[tr])
        print("Trained", name)

    out = a.output or os.path.join("models", f"{tag}models.joblib")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    joblib.dump({"models": models, "features": FEATURES, "train_runs": train_runs,
                 "test_runs": test_runs, "synthetic": bool(tag)}, out)
    print("Saved", out)


if __name__ == "__main__":
    main()
