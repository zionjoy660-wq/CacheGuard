# Limitations and Threats to Validity (Security role)

**Owner:** Nakshathra (Security role)
**Status:** DRAFT. The owner changes this to FINAL after checking every line.

## 1. Scope

CacheGuard classifies a controlled, simplified cache-pattern simulation using CPU performance counters. It is a student research prototype. It does not detect or confirm real covert-channel attacks.

## 2. Limits of the experiment

1. **One machine and one session.** All 60 runs were collected on one lab computer (Intel Core i5-10500T, Ubuntu 22.04.5) on 12 November 2026.
2. **Small number of runs.** 60 runs, 30 per label. The 1,800 rows are one-second slices of those runs, so they are not independent.
3. **The classes were built to be far apart.** The normal workload reads a 256 KiB buffer, which fits in the 12 MiB L3 cache. The suspicious workload reads a 16 MiB buffer with a 4096-byte stride, which does not fit. In the observed dataset, normal miss rates range from 0% to approximately 0.041%, while suspicious miss rates range from approximately 23.92% to 31.67%. There is a clear gap between the two classes, so a single threshold can separate the observed measurements.
4. **Instruction count and miss rate are linked.** Suspicious runs execute about 32% of the normal instructions in the same number of cycles. The likely reason is that the CPU waits on cache misses, but this was not proven. Instruction count alone also separates the classes perfectly, so the experiment cannot show which signal the all-feature models rely on.
5. **Uncontrolled sibling thread.** Workloads were pinned to CPU 2. The other hardware thread on that core was not controlled or recorded.
6. **Run 58.** One normal run had about 13 million cache references per second, against about 500 million in typical normal runs. It was kept. The results are unchanged without it. The cause was not found.
7. **No background noise.** The lab session had no deliberate background load.
8. **A simplified stand-in.** The suspicious workload imitates a cache access pattern. It is not a sender and receiver pair, and it is not a real covert channel.

## 3. What the results show

- The pipeline works from collection to prediction on a clearly separable case.
- The cycles-only control produces accuracy close to chance, showing that performance depends on the information available in the selected feature set.

## 4. What the results do not show

- They do not show that CacheGuard detects real covert channels or attacks.
- They do not show that the models work on other CPUs, other operating systems, other workloads or noisy systems.
- They do not show which feature the models rely on.

## 5. What a stronger follow-up would test

- Working sets close to the L3 size.
- A background process on the machine.
- A second machine, or a second session on another day.
- A suspicious workload that matches the normal instruction rate, to separate cache behaviour from instruction count.
