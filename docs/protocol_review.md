# Protocol Review and Safety Check (Security role)

**Owner:** Nakshathra (Security role)

**Status:** DRAFT. The owner changes this to FINAL after checking every line and confirming the open items.

## 1. Purpose

This file compares `docs/experiment_protocol.md` with the laboratory session and checks the safety of the workload and collection scripts.

## 2. Comparison

| Rule | Evidence | Met? |
|------|----------|------|
| Two labels: 0 normal, 1 suspicious (controlled simulation) | Metadata and dataset labels | Yes |
| 30 normal and 30 suspicious runs, 60 total | Quality check: 60 successful runs, 30 per class | Yes |
| 30 seconds measured per run, 5 seconds warm-up, 1-second sampling | Collector and workload code; quality check reports 30 intervals per run | Yes |
| Run order shuffled | Collector shuffles the schedule; reported longest streak was 5 | Yes |
| Same machine and session for both labels | Reported as one laboratory machine and session on 12 November 2026 | Reported; raw metadata should be retained as evidence |
| Workload pinned to a CPU | Collector uses `taskset -c 2`; CPU 2 recorded for every run | Yes. Sibling CPU 8 was not controlled |
| User-space events only | `cache-references:u`, `cache-misses:u`, `instructions:u`, `cycles:u` | Yes |
| Comparable instruction volume | Suspicious/normal mean instruction ratio = 0.3165; cycle ratio = 0.9980 | Partly. Instruction volume differed substantially |
| Raw output kept unedited | Collector saves workload stdout and perf stderr in per-run raw `.txt` files; logs are saved separately | Yes |
| Validation checks before analysis | Quality check passed; no automatic outlier test was performed | Mostly |
| Permission for counter setting | `protocol_deviations.md` reports permission from the lab assistant to set `kernel.perf_event_paranoid` to 2 | Reported as granted |
| Cleanup of temporary files and compiled binaries | Cleanup confirmation is not recorded here | Pending confirmation |

Actual collection paths:
- Raw output: `data/experiment_20261112/raw/`
- Logs: `data/experiment_20261112/logs/`
- Metadata: `data/experiment_20261112/metadata/run_metadata.csv`
- Parsed measurements: `data/experiment_20261112/processed/measurements.csv`

The actual storage layout differs from the paths originally specified in Section 8 of the experiment protocol. See `docs/protocol_deviations.md`.

## 3. Safety checks

The C workload source `src/collect/cacheguard_workload.c` was inspected.

The workload:
- Allocates its own 16 MB buffer using `malloc()`.
- Initializes the buffer and reads values from it using the selected working-set size and stride.
- Uses a checksum to retain the memory reads.
- Releases the allocated buffer using `free()`.
- Prints status and checksum information to standard output.

No explicit socket, network connection, or file-opening operation was found in the inspected C workload.

Targeted searches were run in `src/collect/` for the following:
- C source: `socket`, `connect`, `fopen`, `system(`, `exec`
- Python collection scripts: `sudo`, `socket`, `requests`, `urllib`, `rmtree`, `unlink`, `os.remove`

The searches returned no matches. These are targeted keyword checks, not a complete security audit.

The Python collector does use `subprocess.run()` to launch `taskset` and `perf`. It also reads and writes experiment metadata, raw output, and log files. These are expected collection operations.

| Question | Result |
|----------|---------|
| Does the workload read and write its own memory buffer? | Yes. It initializes and reads its allocated buffer. It also prints results to standard output. |
| Does the C workload use the network or open files? | No explicit network or file-opening operations found in the inspected C source. |
| Do the inspected Python scripts use sudo, network requests, or deletion operations? | No matches in the targeted searches. The scripts do use subprocess execution and experiment-file operations. |

## 4. Open items

- Nakshathra should confirm with the lab team that temporary files and compiled binaries were cleaned up.
- The lab assistant's permission for the temporary counter-setting change is reported in `docs/protocol_deviations.md`.
- The instruction-volume comparison before full collection was not documented as a completed pilot decision. The substantial difference is recorded in `docs/protocol_deviations.md`.
- The sibling hyper-thread on CPU 8 was not controlled or recorded.

## 5. Sign-off

Reviewed by: (Nakshathra to fill in after checking everything)

Date: (fill in after review)
