# Protocol Deviations: Lab Session of 12 November 2026

**Owner:** Ashitha Somisetty (Hardware role)  
**Status:** Draft

## 1. Purpose

This document records the differences between the experiment protocol and what was actually done during the laboratory session. It also explains how these differences may affect the results.

## 2. Planned versus actual

### 2.1 Where the raw data is stored

- **Protocol (Section 8):** One CSV file per run in `data/raw/`, for example `run_001_normal.csv`, together with `data/raw/run_metadata.csv`.
- **What happened:** Each run was saved as a `.txt` file containing workload output and raw perf output, along with a `.log` file. These files are stored in `data/experiment_20261112/raw/` and `data/experiment_20261112/logs/`. The metadata is stored in `data/experiment_20261112/metadata/run_metadata.csv`.
- **Why it matters:** The raw text preserves the original perf output. It was parsed into a CSV before being used for analysis.

### 2.2 Dataset file and column names

- **Protocol (Section 10):** `data/processed/dataset.csv` with the columns `run_id,label,second,cache_references,cache_misses,instructions,cpu_cycles,miss_rate`.
- **What happened:** The parsing script created `processed/measurements.csv` with the columns `run_id,mode,measurement_interval,elapsed_seconds,cache_references,cache_misses,instructions,cycles,cache_miss_rate`. The ML script `convert_lab_data.py` later converted it into `dataset.csv`.
- **Why it matters:** `mode` was converted into `label` (normal = 0, suspicious = 1), and `cycles` was renamed to `cpu_cycles`. The conversion is implemented in code and can be repeated.

### 2.3 Instruction volume of the two workloads

- **Protocol (Section 5):** The two workloads were expected to have comparable instruction volume. A pilot would compare the counters before the full collection, and the design would be adjusted if the difference was large.
- **What happened:** The quality check showed a suspicious/normal mean instruction ratio of 0.3165, while the cycle ratio was 0.9980. Both labels ran for the same measurement duration.
- **Pilot:** Yes. The pilot output is stored in `data/experiment_pilot_20261112/`, and its parsed measurements are in `data/experiment_pilot_20261112/processed/measurements.csv`.
- **Why it matters:** A model could distinguish the classes using instruction count alone. This difference may be related to CPU waiting during cache misses, but that has not been proven.

### 2.4 Validation checks

- **Protocol (Section 9):** A list of checks was required before building the dataset.
- **What happened:** The quality-check script tests the number of metadata entries, successful runs, return codes, missing values, invalid counters, intervals per run, class balance, and counter means for each label. It does not test for outlier runs.
- **Example:** Run 58 (normal) has approximately 13 million cache references per interval, compared with approximately 500 million in typical normal runs. Its cycles and instructions are normal. The check passed anyway.
- **Why it matters:** Unusual runs are not flagged automatically. Run 58 was retained in the dataset. The ML results are unchanged without it (see `results/no058_*`).

### 2.5 Permission and clean-up

- **Protocol (Section 12):** Performance-counter permission changes require lab permission, and temporary files and compiled binaries should be cleaned up at the end.
- **What happened:** `kernel.perf_event_paranoid` was temporarily set to 2 so that user-space counters could be read. PERMISSION given by lab assistant sir. 
- **Why it matters:** Permission and cleanup details should be confirmed before final sign-off.

### 2.6 CPU pinning

- **Protocol (Section 6):** Workloads are pinned after the physical-core mapping is verified.
- **What happened:** Every run was pinned to CPU 2 using `taskset`. The other hardware thread on the same physical core (hyper-threading) was not controlled or recorded. CPU 8 shares a physical core with CPU 2, as verified from the CPU mapping.

### 2.7 Portability of the scripts

- **What happened:** The collection and parsing scripts use fixed paths under `~/CacheGuard`, and the warm-up duration of 5 seconds is fixed in the workload and metadata.
- **Why it matters:** The scripts require small edits before running on another machine.

## 3. Implementation notes (not deviations)

- The 5-second warm-up runs inside the workload, followed by 30 seconds of measurement. Perf counts the whole run, and the parser drops the first 5 intervals and keeps the next 30.
- The run order was shuffled. The collector's default seed was 42. The longest streak of the same label was 5 runs.
- All 60 runs returned code 0, ran on CPU 2, and used user-space events only.
- The terminal prints numbers with Indian-style digit grouping. The collector uses perf's comma-separated output and `LC_ALL=C`.


## 4. Sign-off

Written by: Ashitha Somisetty, date: 12 November 2026  
Reviewed by: Joy (ML role), date: 12 November 2026
