# CacheGuard: Environment Report

**Owner:** Hardware & Environment Engineer
**Last updated:** 18 November 2026
**Status:** Hardware-counter access was successfully used during the experiment on the college Linux machine. Independent repeatability verification is pending.

> Rule: write only what was actually run and observed. Do not invent command output or hardware details. Distinguish previously recorded experiment details from new verification tests.

---

## 1. Goal

CacheGuard needs these CPU performance-counter events:

`cache-references`, `cache-misses`, `instructions`, `cycles`.

This report records which machines have been used for counter collection and which still require verification.

---

## 2. Machine summary

| # | Machine | Owner | OS | CPU | Counters work? |
|---|---------|-------|----|-----|----------------|
| 1 | MacBook Air | Development machine | macOS | Not recorded in this report | Not used for collection; Linux `perf` is unavailable on macOS |
| 2 | Windows laptop, WSL2 (Ubuntu) | Not recorded | Windows + WSL2 | Not recorded | Reported unavailable in the earlier WSL2 test; exact output not recorded here |
| 3 | College lab HP ProDesk 400 G6 Desktop Mini | Lab machine | Ubuntu 22.04.5 | Intel Core i5-10500T @ 2.30GHz | Successfully used for the 12 November 2026 experiment; independent repeatability test pending |

---

## 3. Machine 1: MacBook Air (development only)

Used for dashboard, API and other development work. It was not used for hardware-counter collection.

Linux `perf` was not used on this macOS machine.

### 3.1 Machine details

The exact output of the following commands has not been recorded in this report:

```bash
sw_vers
uname -m
sysctl -n machdep.cpu.brand_string
python --version
node --version
git --version
```

**Output:** Pending verification.

---

## 4. Machine 2: Windows laptop with WSL2

### 4.1 Previous counter-access issue

An earlier WSL2 test reported that the required hardware performance-counter events were unavailable.

The exact command, complete error output and individual unavailable events have not been preserved in this report. They must be added only if the original terminal output is available.

### 4.2 Environment details

The following commands can be used to record the environment:

```powershell
wsl --version
```

```bash
uname -r
lscpu | head -20
```

**Output:** Not recorded in this report.

### 4.3 What this proves

The earlier WSL2 test did not provide the required counters. This is a limitation observed in that environment and does not prove that every Linux environment will fail.

---

## 5. Machine 3: College lab Linux machine

### 5.1 Machine details from the experiment environment

The following environment was used for the CacheGuard experiment:

- **Machine:** HP ProDesk 400 G6 Desktop Mini PC
- **Processor:** Intel Core i5-10500T CPU @ 2.30GHz
- **Operating system:** Ubuntu 22.04.5
- **Kernel:** 6.8.0-40-generic
- **perf version:** 6.8.12
- **Logical CPUs:** 12 (6 cores with hyperthreading)

### 5.2 Previous counter-collection evidence

The experiment conducted on 12 November 2026 successfully collected CPU performance-counter measurements on this machine.

The recorded experiment included:

- 60 workload runs: 30 normal and 30 suspicious.
- 30 measurement intervals per run.
- 1,800 measurement rows in total.
- All 60 runs completed successfully according to the recorded quality check.
- The collection used the events `instructions`, `cycles`, `cache-references` and `cache-misses`.
- The experiment used user-space performance events.

The recorded environment and experiment results demonstrate that counter collection was used on this Linux machine. This report does not reproduce exact `perf stat` terminal output because that output has not been included here.

### 5.3 Independent verification still pending

The following commands can be run again on the same lab machine to independently verify the current environment:

```bash
lscpu | head -20
uname -r
cat /proc/sys/kernel/perf_event_paranoid
perf --version
perf list | grep -i -E "cache|instructions|cycles"
sudo perf stat -e cache-references,cache-misses,instructions,cycles ls
```

**New terminal output:** Pending verification.

### 5.4 Event check

| Event | Used in previous experiment? | Independent verification |
|-------|-------------------------------|--------------------------|
| cache-references | Yes | Pending |
| cache-misses | Yes | Pending |
| instructions | Yes | Pending |
| cycles | Yes | Pending |

### 5.5 Repeatability check

An independent three-run repeatability test has not yet been recorded.

Run the same `perf stat` command three times on the lab machine and record the actual values.

| Run | cache-references | cache-misses | instructions | cycles |
|-----|------------------|--------------|--------------|--------|
| 1 | Pending | Pending | Pending | Pending |
| 2 | Pending | Pending | Pending | Pending |
| 3 | Pending | Pending | Pending | Pending |

---

## 6. Decision

- [x] **Path found:** The college lab HP ProDesk 400 G6 running Ubuntu 22.04.5 was used successfully for the 12 November 2026 experiment.
- [ ] **Partly working:** Only some events work.
- [ ] **No path found:** Counters unavailable on all tested machines.

**Additional verification:** Independent event and repeatability checks are still pending.

**Date decided:** Pending supervisor confirmation.
**Supervisor informed:** Not recorded.

---

## 7. Notes and blockers

- The college lab Linux machine was used for the experiment and successfully produced the recorded counter measurements.
- The earlier WSL2 test did not provide the required counters.
- The MacBook Air was used for development, not counter collection.
- An independent three-run repeatability test on the lab machine remains to be completed.
- Exact terminal outputs should be added only after they are collected and checked.
- Hardware-counter measurements from the controlled experiment must not be described as proof of detecting a real covert-channel attack.
