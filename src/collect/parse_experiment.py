#!/usr/bin/env python3

import argparse
import csv
from collections import OrderedDict
from pathlib import Path

EVENTS = {
    "cache-references:u",
    "cache-misses:u",
    "instructions:u",
    "cycles:u",
}


def parse_run(raw_file, run_id, mode, duration):
    groups = OrderedDict()

    text = raw_file.read_text()
    perf_section = text.split("=== PERF STDERR ===", 1)[-1]

    for line in perf_section.splitlines():
        fields = line.split(",")

        if len(fields) < 4 or fields[3] not in EVENTS:
            continue

        timestamp = fields[0]

        try:
            value = int(fields[1])
        except ValueError:
            continue

        groups.setdefault(timestamp, {})[fields[3]] = value

    complete = [
        (timestamp, values)
        for timestamp, values in groups.items()
        if EVENTS.issubset(values)
    ]

    warmup = 5
    expected = int(duration)

    if len(complete) < warmup + expected:
        raise ValueError(
            f"{run_id}: expected {warmup + expected} complete intervals, "
            f"found {len(complete)}"
        )

    rows = []

    for interval, (timestamp, values) in enumerate(
        complete[warmup:warmup + expected], start=1
    ):
        references = values["cache-references:u"]
        misses = values["cache-misses:u"]

        rows.append({
            "run_id": run_id,
            "mode": mode,
            "measurement_interval": interval,
            "elapsed_seconds": timestamp,
            "cache_references": references,
            "cache_misses": misses,
            "instructions": values["instructions:u"],
            "cycles": values["cycles:u"],
            "cache_miss_rate": misses / references if references else 0,
        })

    return rows


def main():
    parser = argparse.ArgumentParser(
        description="Convert CacheGuard raw perf outputs to CSV"
    )
    parser.add_argument("experiment_dir", type=Path)
    args = parser.parse_args()

    experiment = args.experiment_dir.expanduser().resolve()
    metadata_file = experiment / "metadata" / "run_metadata.csv"
    output_dir = experiment / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "measurements.csv"

    all_rows = []

    with metadata_file.open(newline="") as handle:
        for run in csv.DictReader(handle):
            if run["status"] != "success":
                raise ValueError(f"Failed run in metadata: {run['run_id']}")

            raw_file = Path(run["raw_file"])
            if not raw_file.is_absolute():
                raw_file = Path.home() / "CacheGuard" / raw_file

            rows = parse_run(
                raw_file,
                run["run_id"],
                run["mode"],
                float(run["duration_seconds"]),
            )
            all_rows.extend(rows)

    fieldnames = [
        "run_id", "mode", "measurement_interval", "elapsed_seconds",
        "cache_references", "cache_misses", "instructions", "cycles",
        "cache_miss_rate",
    ]

    with output_file.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Runs parsed: {len(set(row['run_id'] for row in all_rows))}")
    print(f"Measurement rows: {len(all_rows)}")
    print(f"CSV: {output_file}")


if __name__ == "__main__":
    main()
