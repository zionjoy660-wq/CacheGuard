#!/usr/bin/env python3

import csv
import math
from collections import defaultdict
from pathlib import Path

EXPERIMENT = Path("data/experiment_20261112")
DATASET = EXPERIMENT / "processed" / "measurements.csv"
METADATA = EXPERIMENT / "metadata" / "run_metadata.csv"

EXPECTED_RUNS = 60
EXPECTED_PER_CLASS = 30
EXPECTED_INTERVALS = 30

def mean(values):
    return sum(values) / len(values)

def main():
    print("CACHEGUARD DATASET QUALITY CHECK")
    print("=" * 45)

    with METADATA.open(newline="") as handle:
        metadata = list(csv.DictReader(handle))

    print(f"Metadata entries: {len(metadata)}")
    print(f"Successful runs: {sum(r['status'] == 'success' for r in metadata)}")
    print(f"Failed runs: {sum(r['status'] != 'success' for r in metadata)}")
    print(f"Nonzero return codes: {sum(r['return_code'] != '0' for r in metadata)}")

    with DATASET.open(newline="") as handle:
        rows = list(csv.DictReader(handle))

    print(f"\nMeasurement rows: {len(rows)}")

    required = [
        "run_id", "mode", "measurement_interval",
        "cache_references", "cache_misses",
        "instructions", "cycles", "cache_miss_rate",
    ]

    missing = sum(
        1 for row in rows
        for field in required
        if not row.get(field, "").strip()
    )
    invalid = 0

    for row in rows:
        try:
            values = [float(row[field]) for field in required[3:]]
            if not all(math.isfinite(v) for v in values):
                invalid += 1
            if values[0] <= 0 or values[2] <= 0 or values[3] <= 0:
                invalid += 1
        except (ValueError, KeyError):
            invalid += 1

    print(f"Missing required values: {missing}")
    print(f"Invalid/nonpositive counter rows: {invalid}")

    run_rows = defaultdict(list)
    class_rows = defaultdict(list)

    for row in rows:
        run_rows[row["run_id"]].append(row)
        class_rows[row["mode"]].append(row)

    print(f"\nUnique runs in dataset: {len(run_rows)}")

    bad_runs = []
    for run_id, values in run_rows.items():
        intervals = sorted(int(r["measurement_interval"]) for r in values)
        if len(values) != EXPECTED_INTERVALS or intervals != list(range(1, EXPECTED_INTERVALS + 1)):
            bad_runs.append(run_id)

    print(f"Runs with incorrect interval count/order: {len(bad_runs)}")

    print("\nCLASS BALANCE")
    for mode in ("normal", "suspicious"):
        runs = sum(1 for r in metadata if r["mode"] == mode)
        samples = len(class_rows[mode])
        print(f"{mode}: {runs} runs, {samples} intervals")

    print("\nMEAN COUNTERS PER MEASUREMENT INTERVAL")
    for mode in ("normal", "suspicious"):
        values = class_rows[mode]
        print(f"\n{mode.upper()} (n={len(values)})")
        for field in ("cache_references", "cache_misses", "instructions", "cycles", "cache_miss_rate"):
            numbers = [float(r[field]) for r in values]
            print(f"  {field:20s} mean={mean(numbers):,.4f}")

    normal = class_rows["normal"]
    suspicious = class_rows["suspicious"]

    print("\nLABEL COMPARISON")
    for field in ("instructions", "cycles", "cache_miss_rate"):
        n_mean = mean([float(r[field]) for r in normal])
        s_mean = mean([float(r[field]) for r in suspicious])
        ratio = s_mean / n_mean if n_mean else float("inf")
        print(f"{field}: suspicious/normal mean ratio = {ratio:.4f}")

    checks = {
        "60 metadata entries": len(metadata) == EXPECTED_RUNS,
        "all runs successful": all(r["status"] == "success" and r["return_code"] == "0" for r in metadata),
        "60 unique dataset runs": len(run_rows) == EXPECTED_RUNS,
        "1800 measurement rows": len(rows) == EXPECTED_RUNS * EXPECTED_INTERVALS,
        "30 runs per class": all(sum(r["mode"] == m for r in metadata) == EXPECTED_PER_CLASS for m in ("normal", "suspicious")),
        "no missing values": missing == 0,
        "no invalid counters": invalid == 0,
        "30 intervals per run": len(bad_runs) == 0,
    }

    print("\nFINAL CHECKS")
    for name, passed in checks.items():
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")

    print(f"\nOverall: {'PASS' if all(checks.values()) else 'FAIL'}")

if __name__ == "__main__":
    main()
