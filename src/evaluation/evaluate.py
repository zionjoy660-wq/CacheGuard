"""Step 3: evaluate the saved models on the held-out test runs.

Usage:
    python src/evaluation/evaluate.py --data data/processed/synthetic_clean.csv --models models/synthetic_models.joblib
"""
import argparse
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, confusion_matrix,
                             f1_score, precision_score, recall_score)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--models", required=True)
    a = ap.parse_args()

    bundle = joblib.load(a.models)
    synthetic = bundle["synthetic"]
    tag = "synthetic_" if synthetic else ""
    if synthetic:
        print("WARNING: SYNTHETIC DATA. These scores only test the code, not real detection.")

    df = pd.read_csv(a.data)
    test = df[df["run_id"].isin(bundle["test_runs"])]
    X, y = test[bundle["features"]], test["label"]
    print(f"Test rows: {len(test)} from {len(bundle['test_runs'])} runs")

    fig, axes = plt.subplots(1, len(bundle["models"]), figsize=(13, 3.8))
    rows = []
    for ax, (name, model) in zip(axes, bundle["models"].items()):
        pred = model.predict(X)
        rows.append({
            "Model": name,
            "Accuracy": accuracy_score(y, pred),
            "Precision": precision_score(y, pred, zero_division=0),
            "Recall": recall_score(y, pred, zero_division=0),
            "F1": f1_score(y, pred, zero_division=0),
        })
        cm = confusion_matrix(y, pred, labels=[0, 1])
        ConfusionMatrixDisplay(cm, display_labels=["normal", "suspicious"]).plot(ax=ax, colorbar=False)
        ax.set_title(name)
    fig.suptitle("Confusion matrices" + (" (SYNTHETIC DATA)" if synthetic else ""))
    plt.tight_layout()

    os.makedirs("results", exist_ok=True)
    res = pd.DataFrame(rows).round(3)
    res.to_csv(os.path.join("results", f"{tag}results.csv"), index=False)
    fig.savefig(os.path.join("results", f"{tag}confusion_matrices.png"), dpi=150)
    print(res.to_string(index=False))
    print("Saved results/ files")


if __name__ == "__main__":
    main()
