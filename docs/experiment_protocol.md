# CacheGuard Experiment Protocol

## 1. Research Objective

CacheGuard is a student research prototype that evaluates whether CPU performance-counter measurements and machine-learning models can distinguish ordinary workloads from a controlled workload that imitates cache-access behavior associated with a covert-channel sender/receiver pair.

This is a simplified laboratory simulation. It does not demonstrate detection of a real covert-channel attack.

## 2. Classification Labels

- Label 0: Normal run
- Label 1: Suspicious run (controlled cache-pattern simulation)

## 3. Experimental Environment

- CPU: Intel Core i5-10500T
- Physical cores: 6
- Logical CPUs: 12
- Operating system: Ubuntu Linux
- Kernel: 6.8.0-40-generic
- perf: 6.8.12

The CPU mapping must be verified before pinning workloads.

## 4. Collection Plan

- 30 normal runs
- 30 suspicious runs
- Total: 60 runs
- Measured duration: 30 seconds per run
- Warm-up: 5 seconds before measurement
- Counter sampling interval: 1 second
- Rest between runs: 5 seconds
- Run order: randomized or shuffled
- Environment: same laboratory machine and session

## 5. Workload Comparability

Normal and suspicious workloads should have comparable execution duration and instruction volume where practical.

A short pilot will compare instructions, cycles, cache references, and cache misses before full collection.

If workload differences are substantial, the workload design must be adjusted and documented before collecting the full dataset.

## 6. CPU Pinning

Workloads will be pinned only after physical-core mapping is verified.

Logical CPUs 0 and 2 are separate physical cores on the verified machine. CPU selection and pinning will be documented.

## 7. Measurements

The planned counters are:

- Cache references
- Cache misses
- Instructions
- CPU cycles

Measurements will use user-mode events where supported.

Raw interval output must be inspected before implementing the parser.

## 8. Data Storage

Each run will have a separate raw CSV file:

data/raw/run_001_normal.csv
data/raw/run_002_suspicious.csv

The run metadata will be stored in:

data/raw/run_metadata.csv

Raw data will not be edited after collection.

## 9. Data Validation

Before dataset construction, checks will include:

- Number of runs per label
- Number of measurement rows per run
- Missing or zero counter values
- Perf errors or not-counted events
- Short or interrupted runs
- Counter summaries by label
- Excluded runs and documented reasons

## 10. Dataset Construction

The validated dataset will be written to:

data/processed/dataset.csv

Planned columns:

run_id,label,second,cache_references,cache_misses,instructions,cpu_cycles,miss_rate

Rows with zero cache references will not receive a calculated miss rate.

Run IDs will be preserved to support grouped train/test splitting and prevent measurements from the same run leaking across splits.

## 11. Machine-Learning Evaluation

Planned models:

- Logistic Regression
- Decision Tree
- Random Forest

Evaluation will use run-grouped train/test separation and appropriate metrics such as precision, recall, F1-score, and confusion matrix.

Results will be reported honestly, including limitations and possible workload confounding.

## 12. Safety and Scope

- Only project-owned workloads and files will be used.
- No secrets, private data, or network transmission will be involved.
- No interference with other users or processes is intended.
- Temporary performance-counter permission changes require laboratory permission.
- Temporary files and compiled binaries will be cleaned up at the end.
- No real-world attack detection claim will be made.
