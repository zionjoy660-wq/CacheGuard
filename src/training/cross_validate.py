"""Grouped cross-validation on the real CacheGuard dataset.

Usage (run from the CacheGuard folder):
    python src/training/cross_validate.py --input data/processed/dataset.csv --save-final

What it does:
- Splits by run_id, so all samples of one run stay on the same side (no data leakage).
- Trains Logistic Regression, Decision Tree and Random Forest.
- Repeats this for five feature sets, to see WHICH counters carry the signal:
    all, cache_only, miss_rate_only, instructions_only, cycles_only
- Reports accuracy, precision, recall and F1 as mean and standard deviation over the folds.

Scope: a controlled, simplified cache-pattern experiment. Not a real covert-channel attack.
"""
import argparse
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, confusion_matrix,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

FEATURE_SETS = {
    "all": ["cache_references", "cache_misses", "instructions", "cpu_cycles", "miss_rate"],
    "cache_only": ["cache_references", "cache_misses", "miss_rate"],
    "miss_rate_only": ["miss_rate"],
    "instructions_only": ["instructions"],
    "cycles_only": ["cpu_cycles"],   # control: cycles were almost equal for both labels
}


def make_models(seed):
    return {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Decision Tree": make_pipeline(StandardScaler(), DecisionTreeClassifier(max_depth=4, random_state=seed)),
        "Random Forest": make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=100, random_state=seed)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tag", default="real_")
    ap.add_argument("--save-final", action="store_true",
                    help="also fit the three models on ALL runs (all features) and save them")
    a = ap.parse_args()

    df = pd.read_csv(a.input)
    y = df["label"].to_numpy()
    groups = df["run_id"].to_numpy()

    runs_per_label = df.groupby("label")["run_id"].nunique()
    print("Runs per label:", runs_per_label.to_dict())
    folds = min(a.folds, int(runs_per_label.min()))
    cv = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=a.seed)
    splits = list(cv.split(df, y, groups))
    for i, (tr, te) in enumerate(splits, 1):
        assert not set(groups[tr]) & set(groups[te]), "Leakage: a run is in both train and test"
    print(f"{folds}-fold cross-validation, split by run. No run appears in both train and test.\n")

    rows, pooled = [], {}
    for fs_name, feats in FEATURE_SETS.items():
        X = df[feats]
        for model_name in make_models(a.seed):
            per_fold = {"accuracy": [], "precision": [], "recall": [], "f1": []}
            y_true_all, y_pred_all = [], []
            for tr, te in splits:
                model = make_models(a.seed)[model_name]
                model.fit(X.iloc[tr], y[tr])
                pred = model.predict(X.iloc[te])
                per_fold["accuracy"].append(accuracy_score(y[te], pred))
                per_fold["precision"].append(precision_score(y[te], pred, zero_division=0))
                per_fold["recall"].append(recall_score(y[te], pred, zero_division=0))
                per_fold["f1"].append(f1_score(y[te], pred, zero_division=0))
                y_true_all.extend(y[te]); y_pred_all.extend(pred)
            row = {"feature_set": fs_name, "model": model_name}
            for k, v in per_fold.items():
                row[f"{k}_mean"] = round(float(np.mean(v)), 4)
                row[f"{k}_std"] = round(float(np.std(v)), 4)
            rows.append(row)
            pooled[(fs_name, model_name)] = (np.array(y_true_all), np.array(y_pred_all))

    res = pd.DataFrame(rows)
    os.makedirs("results", exist_ok=True)
    res_path = os.path.join("results", f"{a.tag}cv_results.csv")
    res.to_csv(res_path, index=False)
    print(res[["feature_set", "model", "accuracy_mean", "accuracy_std", "precision_mean",
               "recall_mean", "f1_mean"]].to_string(index=False))
    print("\nSaved", res_path)

    # Figure 1: pooled confusion matrices, all features
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, model_name in zip(axes, make_models(a.seed)):
        yt, yp = pooled[("all", model_name)]
        ConfusionMatrixDisplay(confusion_matrix(yt, yp, labels=[0, 1]),
                               display_labels=["normal", "suspicious"]).plot(ax=ax, colorbar=False)
        ax.set_title(model_name)
    fig.suptitle("Confusion matrices, all features (pooled over folds, split by run)")
    plt.tight_layout()
    cm_path = os.path.join("results", f"{a.tag}confusion_matrices.png")
    fig.savefig(cm_path, dpi=150); plt.close(fig)

    # Figure 2: accuracy by feature set
    fig, ax = plt.subplots(figsize=(9, 4.2))
    names = list(FEATURE_SETS)
    width = 0.26
    for j, model_name in enumerate(make_models(a.seed)):
        sub = res[res["model"] == model_name].set_index("feature_set").loc[names]
        ax.bar(np.arange(len(names)) + (j - 1) * width, sub["accuracy_mean"], width,
               yerr=sub["accuracy_std"], label=model_name, capsize=3)
    ax.set_xticks(np.arange(len(names))); ax.set_xticklabels(names, rotation=15)
    ax.set_ylabel("Accuracy (mean over folds)"); ax.set_ylim(0, 1.05)
    ax.set_title("Accuracy by feature set (cycles_only is the control)")
    ax.legend(loc="lower left")
    plt.tight_layout()
    acc_path = os.path.join("results", f"{a.tag}accuracy_by_features.png")
    fig.savefig(acc_path, dpi=150); plt.close(fig)
    print("Saved", cm_path, "and", acc_path)

    if a.save_final:
        os.makedirs("models", exist_ok=True)
        feats = FEATURE_SETS["all"]
        final = {}
        for name, model in make_models(a.seed).items():
            model.fit(df[feats], y)
            final[name] = model
        out = os.path.join("models", f"{a.tag}models.joblib")
        joblib.dump({"models": final, "features": feats, "label_names": {0: "normal", 1: "suspicious"},
                     "note": "Fitted on all runs. Only the cross-validation numbers estimate performance."}, out)
        print("Saved", out)


if __name__ == "__main__":
    main()
