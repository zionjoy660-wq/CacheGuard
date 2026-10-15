# CacheGuard: Environment Report

**Owner:** Hardware & Environment Engineer
**Last updated:** (date)
**Status:** Hardware-counter access NOT yet verified on any machine.

> Rule: write only what you actually ran and saw. Paste exact commands and exact output. Do not guess.

---

## 1. Goal

CacheGuard needs these CPU performance-counter events:
`cache-references`, `cache-misses`, `instructions`, `cycles`.

This report records which machines can read them, and which cannot.

---

## 2. Machine summary

| # | Machine | Owner | OS | CPU (Intel/AMD/Apple) | Counters work? |
|---|---------|-------|----|-----------------------|----------------|
| 1 | MacBook Air | (name) | macOS | (fill in, see 3.1) | No: `perf` does not exist on macOS |
| 2 | Windows laptop, WSL2 (Ubuntu) | (name) | Windows + WSL2 | (fill in) | No: see section 4 |
| 3 | Native Linux machine | (name) | (fill in) | (fill in) | Not tested yet: see section 5 |

---

## 3. Machine 1: MacBook Air (development only)

Used for the dashboard, API and ML notebook. Not used for counter collection, because `perf` is a Linux tool.

### 3.1 Commands to run and paste

```
sw_vers
uname -m
sysctl -n machdep.cpu.brand_string
python --version
node --version
git --version
```

**Output:**

```
(paste here)
```

---

## 4. Machine 2: Windows laptop with WSL2

### 4.1 What failed

**Exact command run:**

```
(paste the exact perf command)
```

**Full error output:**

```
(paste the complete error)
```

**Events reported as unavailable:**
(list them)

### 4.2 Environment details

```
wsl --version          (run in Windows PowerShell)
uname -r               (run in Ubuntu)
lscpu | head -20       (run in Ubuntu)
```

**Output:**

```
(paste here)
```

### 4.3 What this proves

WSL2 runs inside a virtual machine and did not expose the counters on this laptop. This does **not** prove that every Linux environment will fail.

---

## 5. Machine 3: Native Linux test (the important one)

Use only with the owner's permission. Prefer booting from a **live USB** so the laptop's disk is not changed. Do not repartition or format any disk. Back up important files first.

### 5.1 Setup

```
sudo apt update
sudo apt install linux-tools-common linux-tools-generic linux-tools-$(uname -r)
```

### 5.2 Commands to run and paste

```
lscpu | head -20
uname -r
cat /proc/sys/kernel/perf_event_paranoid
perf --version
perf list | grep -i -E "cache|instructions|cycles"
sudo perf stat -e cache-references,cache-misses,instructions,cycles ls
```

**Output:**

```
(paste here)
```

### 5.3 Event check

| Event | Shown as supported? | Gave a number (not `<not supported>`)? |
|-------|---------------------|-----------------------------------------|
| cache-references | | |
| cache-misses | | |
| instructions | | |
| cycles | | |

### 5.4 Repeatability check

Run the same `perf stat` command 3 times. The values should be in the same range.

| Run | cache-references | cache-misses | instructions | cycles |
|-----|------------------|--------------|--------------|--------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 6. Decision

Fill this in after section 5.

- [ ] **Path found:** machine ______ with OS ______ reads all four events. Use it for data collection.
- [ ] **Partly working:** only these events work: ______. Ask the supervisor if the study can continue with them.
- [ ] **No path found:** counters unavailable on all tested machines. Ask the supervisor to approve a revised study using software-based features, and state the limitation clearly.

**Date decided:** ______
**Supervisor informed:** yes / no

---

## 7. Notes and blockers

- (write anything unusual here, for example a command needing sudo, or a laptop that would not boot from USB)
