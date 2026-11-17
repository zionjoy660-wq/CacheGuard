# Lab Session Data: 12 Nov 2026

Controlled, simplified cache-pattern experiment for the CacheGuard project. It is **not** a real covert-channel attack, and nothing here shows detection of one.

> **DRAFT. Before you commit, check every line against your photos, the log files and the metadata.**
> Replace each **[CONFIRM: ...]** with the true answer and delete the marker, or delete the line if you cannot confirm it.

## 1. What this folder contains

| Path | What it is |
|------|------------|
| `raw/` | 60 files, one per run. Each holds the workload's own output and the unmodified `perf` output. Never edit these. |
| `logs/` | 60 log files with the exact command, the return code and the outputs of each run. |
| `metadata/run_metadata.csv` | One line per run: run id, label (mode), start and end time, duration, warm-up, CPU, return code, status and file paths. |
| `processed/measurements.csv` | Derived from the raw files by `parse_experiment.py`. 1,800 rows (60 runs x 30 intervals). |
| `quality_check.txt` | Output of `quality_check.py` on the processed data. |

The scripts and the workload source are in `src/collect/`. The protocol is in `docs/experiment_protocol.md`.

## 2. Machine and software

- Machine: HP ProDesk 400 G6 Desktop Mini PC, college computer lab
- CPU: Intel Core i5-10500T @ 2.30 GHz, 6 cores, 12 logical CPUs (hyper-threading on)
- Caches (from `lscpu`): L1d 192 KiB (6 instances), L1i 192 KiB (6 instances), L2 1.5 MiB (6 instances), L3 12 MiB (1 instance)
- OS: Ubuntu 22.04.5 LTS, kernel 6.8.0-40-generic
- perf: 6.8.12, Python: 3.10.12

## 3. Date, people and permission

- Date: 12 Nov 2026. The first run started at 14:42:28 and the last run started at 15:21:51 (UTC+05:30).
- Session run by: **[CONFIRM: names of the people who ran the commands]**
- Permission: **[CONFIRM: who in the lab gave permission, and for what]**
- `kernel.perf_event_paranoid` value during collection: **[CONFIRM: run `cat /proc/sys/kernel/perf_event_paranoid` on the lab machine, or check your notes]**. Earlier tests showed that the value 4 blocks the counters and the value 2 lets user-space counters work. A temporary change resets when the computer restarts.

## 4. The two workloads

Both modes come from one program, `cacheguard_workload.c`. Each run does a 5-second warm-up inside the program, then the measured phase for 30 seconds. Each pass reads bytes from a buffer and adds them to a checksum.

| Mode | Label | Stride | Working set |
|------|-------|--------|-------------|
| normal | 0 | 64 bytes | 262,144 bytes (256 KiB) |
| suspicious | 1 | 4,096 bytes | 16,777,216 bytes (16 MiB) |

The "suspicious" workload is a simplified controlled stand-in. Its working set is bigger than this CPU's 12 MiB L3 cache, so it produces many cache misses. It does not read secrets, use the network or touch other programs.

## 5. How the data was collected

- 60 runs: 30 normal and 30 suspicious, in shuffled order (seed 42), by `collect_experiment.py`.
- Each run was pinned to CPU 2 with `taskset`.
- Counters: `cache-references:u`, `cache-misses:u`, `instructions:u` and `cycles:u` (user-space events), sampled every second.
- Rest between runs: 5 seconds. The collector stops at the first failed run.
- `LC_ALL=C` was set, so numbers have no digit grouping.
- Command used for each run (from the logs):

```
taskset -c 2 perf stat -I 1000 -x, -e cache-references:u,cache-misses:u,instructions:u,cycles:u -- <path to workload> <normal|suspicious> 30.0
```

## 6. How the processed file was made

`parse_experiment.py` reads each raw file, drops the first 5 one-second intervals (the warm-up), keeps the next 30, and computes `cache_miss_rate = cache_misses / cache_references`. Columns: `run_id, mode, measurement_interval, elapsed_seconds, cache_references, cache_misses, instructions, cycles, cache_miss_rate`.

## 7. Quality check result

From `quality_check.txt`: 60 successful runs, 0 failed, 30 runs per class, 1,800 rows, no missing values, no invalid counter rows, 30 intervals per run. Overall: PASS.

Class means per interval, from the same file:

| | normal | suspicious |
|---|--------|------------|
| cache references | about 506 million | about 299 million |
| cache misses | about 3,025 | about 83.6 million |
| instructions | about 4.80 billion | about 1.52 billion |
| cycles | about 3.77 billion | about 3.76 billion |

The suspicious runs executed about 32% of the normal instructions (ratio 0.3165), while cycles were almost equal (ratio 0.998).

## 8. Known notes

- **run_058_normal** has far fewer cache references (about 13 million per second) than the other normal runs (typically several hundred million), while its cycles and instructions look normal. It was kept. The ML cross-validation gives the same results with and without it. The cause is not confirmed.
- The quality check checks structure and counts only. It has no rule for unusual values, so run 58 passed it.
- The protocol asked for raw `.csv` files in `data/raw/`. In practice the raw files are `.txt` files, together with logs, in this folder.
- The protocol asked for similar instruction volume in both classes. They differ by about 3 times, while cycles match.
- The scripts use fixed paths under `~/CacheGuard` on the lab machine, so they need edits to run elsewhere.
- **[CONFIRM: were temporary files and compiled binaries deleted from the lab computer? Write yes or no.]**

## 9. Reproducing

On the lab machine, from the project folder, the scripts in `src/collect/` are used in this order:

```
python3 src/collect_experiment.py
python3 src/parse_experiment.py data/experiment_20261112
python3 src/quality_check.py
```

The workload must be compiled first. **[CONFIRM: the exact compile command that was used]**

## 10. AI assistance

**[CONFIRM and edit: for example, "The collection scripts were written with help from an AI assistant. They were run and checked by the team, and all numbers in this folder come from the real session."]**