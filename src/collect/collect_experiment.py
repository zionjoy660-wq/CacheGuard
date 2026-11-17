#!/usr/bin/env python3

import argparse
import csv
import os
import random
import subprocess
import time
from datetime import datetime
from pathlib import Path

PROJECT = Path.home() / "CacheGuard"
DEFAULT_EXPERIMENT = PROJECT / "data" / "experiment_20261112"

WORKLOAD = PROJECT / "src" / "cacheguard_workload"
CPU = "2"
REST_SECONDS = 5

EVENTS = [
    "cache-references:u",
    "cache-misses:u",
    "instructions:u",
    "cycles:u",
]


def timestamp():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main():
    parser = argparse.ArgumentParser(description="CacheGuard experiment collector")
    parser.add_argument("--runs-per-class", type=int, default=30)
    parser.add_argument("--duration", type=float, default=30)
    parser.add_argument("--rest", type=float, default=REST_SECONDS)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_EXPERIMENT)
    args = parser.parse_args()

    if args.runs_per_class < 1 or args.duration <= 0 or args.rest < 0:
        parser.error("Runs must be >=1, duration >0, and rest >=0")

    experiment = args.output_dir.expanduser().resolve()
    raw_dir = experiment / "raw"
    meta_dir = experiment / "metadata"
    log_dir = experiment / "logs"

    for folder in (raw_dir, meta_dir, log_dir):
        folder.mkdir(parents=True, exist_ok=True)

    metadata_file = meta_dir / "run_metadata.csv"

    # Refuse to overwrite a previous experiment.
    if metadata_file.exists():
        parser.error(f"Metadata already exists: {metadata_file}")

    schedule = (
        ["normal"] * args.runs_per_class
        + ["suspicious"] * args.runs_per_class
    )
    random.Random(args.seed).shuffle(schedule)

    with metadata_file.open("w", newline="") as metadata_handle:
        writer = csv.DictWriter(
            metadata_handle,
            fieldnames=[
                "run_id", "mode", "start_time", "end_time",
                "duration_seconds", "warmup_seconds", "cpu",
                "return_code", "status", "raw_file", "log_file",
            ],
        )
        writer.writeheader()
        metadata_handle.flush()

        total = len(schedule)

        for index, mode in enumerate(schedule, start=1):
            run_id = f"run_{index:03d}_{mode}"
            raw_file = raw_dir / f"{run_id}.txt"
            log_file = log_dir / f"{run_id}.log"

            start_time = timestamp()
            print(f"\n[{index}/{total}] Starting {run_id}", flush=True)

            command = [
                "taskset", "-c", CPU,
                "perf", "stat", "-I", "1000", "-x,",
                "-e", ",".join(EVENTS),
                "--", str(WORKLOAD), mode, str(args.duration),
            ]

            env = os.environ.copy()
            env["LC_ALL"] = "C"

            try:
                result = subprocess.run(
                    command,
                    cwd=PROJECT,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=args.duration + 60,
                )
                return_code = result.returncode
                status = "success" if return_code == 0 else "failed"

                # Keep workload output and perf output together, unmodified.
                with raw_file.open("w") as raw_handle:
                    raw_handle.write("=== WORKLOAD STDOUT ===\n")
                    raw_handle.write(result.stdout)
                    raw_handle.write("\n=== PERF STDERR ===\n")
                    raw_handle.write(result.stderr)

                with log_file.open("w") as log_handle:
                    log_handle.write("COMMAND: " + " ".join(command) + "\n")
                    log_handle.write("RETURN CODE: " + str(return_code) + "\n")
                    log_handle.write(result.stdout)
                    log_handle.write(result.stderr)

            except subprocess.TimeoutExpired as error:
                return_code = -1
                status = "timeout"
                with raw_file.open("w") as raw_handle:
                    raw_handle.write("TIMEOUT\n")
                    raw_handle.write(str(error))

                with log_file.open("w") as log_handle:
                    log_handle.write("TIMEOUT\n")
                    log_handle.write(str(error))

            end_time = timestamp()

            writer.writerow({
                "run_id": run_id,
                "mode": mode,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": args.duration,
                "warmup_seconds": 5,
                "cpu": CPU,
                "return_code": return_code,
                "status": status,
                "raw_file": str(raw_file.relative_to(PROJECT)),
                "log_file": str(log_file.relative_to(PROJECT)),
            })
            metadata_handle.flush()

            print(f"[{index}/{total}] {status}: {run_id}", flush=True)

            if status != "success":
                print("Stopping collection because this run failed.")
                return 1

            if index < total and args.rest > 0:
                print(f"Resting for {args.rest} seconds...", flush=True)
                time.sleep(args.rest)

    print("\nCollection completed successfully.")
    print(f"Raw data: {raw_dir}")
    print(f"Metadata: {metadata_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
