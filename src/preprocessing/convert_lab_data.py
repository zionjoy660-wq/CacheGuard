"""Convert the lab measurements into the CacheGuard data-dictionary format.

Usage (run from the CacheGuard folder):
    python src/preprocessing/convert_lab_data.py \
        --measurements <path>/processed/measurements.csv \
        --metadata <path>/metadata/run_metadata.csv

Output: data/processed/dataset.csv with columns
    run_id, label, second, cache_references, cache_misses, instructions, cpu_cycles, miss_rate
Label: 0 = normal, 1 = suspicious (controlled cache-pattern simulation).
This script only READS the lab files. It never edits them.
"""
import argparse
import os
import sys

import pandas as pd

NEEDED = ["run_id", "mode", "measurement_interval", "cache_references",
          "cache_misses", "instructions", "cycles", "cache_miss_rate"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--measurements", required=True)
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--output", default=os.path.join("data", "processed", "dataset.csv"))
    a = ap.parse_args()

    m = pd.read_csv(a.measurements)
    meta = pd.read_csv(a.metadata)

    missing = [c for c in NEEDED if c not in m.columns]
    if missing:
        sys.exit(f"Missing columns in measurements file: {missing}")

    good = set(meta.loc[(meta["status"] == "success") & (meta["return_code"] == 0), "run_id"])
    excluded = sorted(set(m["run_id"]) - good)
    print("Runs in measurements:", m["run_id"].nunique())
    print("Excluded (not successful in metadata):", excluded if excluded else "none")
    m = m[m["run_id"].isin(good)].copy()

    before = len(m)
    m = m.dropna(subset=NEEDED)
    m = m[m["cache_references"] > 0]
    print(f"Rows dropped for missing values or zero references: {before - len(m)}")

    m["label"] = m["mode"].map({"normal": 0, "suspicious": 1})
    if m["label"].isna().any():
        sys.exit("Unknown value in the mode column. Expected normal or suspicious.")

    recomputed = m["cache_misses"] / m["cache_references"]
    diff = (recomputed - m["cache_miss_rate"]).abs().max()
    print(f"Largest difference between the file's miss rate and misses/references: {diff:.2e}")

    out = pd.DataFrame({
        "run_id": m["run_id"],
        "label": m["label"].astype(int),
        "second": m["measurement_interval"],
        "cache_references": m["cache_references"],
        "cache_misses": m["cache_misses"],
        "instructions": m["instructions"],
        "cpu_cycles": m["cycles"],
        "miss_rate": recomputed,
    })

    print("\nRows per label (0 = normal, 1 = suspicious):")
    print(out["label"].value_counts().sort_index().to_string())
    print("Runs per label:")
    print(out.groupby("label")["run_id"].nunique().to_string())

    os.makedirs(os.path.dirname(a.output), exist_ok=True)
    out.to_csv(a.output, index=False)
    print("\nSaved", a.output)


if __name__ == "__main__":
    main()
