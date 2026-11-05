"""Step 1: validate and clean a counter dataset.

Usage (run from the CacheGuard folder):
    python src/preprocessing/preprocess.py --input data/processed/synthetic_dataset.csv

Rules:
- Never edit files in data/raw/. This script only reads them and writes a new file.
- Files with "synthetic" in the name are fake test data and are labelled that way in every output.
"""
import argparse
import os
import sys

import pandas as pd

REQUIRED = ["run_id", "label", "cache_references", "cache_misses", "instructions", "cpu_cycles"]


def tag_for(path):
    return "synthetic_" if "synthetic" in os.path.basename(path).lower() else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=None)
    a = ap.parse_args()

    tag = tag_for(a.input)
    if tag:
        print("WARNING: SYNTHETIC DATA. Results only test the code, not real detection.")

    df = pd.read_csv(a.input)

    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        sys.exit(f"Missing required columns: {missing}")

    n0 = len(df)
    df = df.drop_duplicates()
    df = df.dropna(subset=REQUIRED)
    df = df[df["cache_references"] > 0]
    df = df[df["cache_misses"] <= df["cache_references"]]       # misses cannot exceed references
    df = df[(df[["cache_references", "cache_misses", "instructions", "cpu_cycles"]] >= 0).all(axis=1)]
    df["label"] = df["label"].astype(int)
    df["miss_rate"] = df["cache_misses"] / df["cache_references"]

    print(f"Rows: {n0} -> {len(df)} after cleaning")
    print("Label counts (0 = normal, 1 = suspicious):")
    print(df["label"].value_counts().sort_index().to_string())
    print("Runs per label:")
    print(df.groupby("label")["run_id"].nunique().to_string())

    out = a.output or os.path.join("data", "processed", f"{tag}clean.csv")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    df.to_csv(out, index=False)
    print("Saved", out)


if __name__ == "__main__":
    main()
