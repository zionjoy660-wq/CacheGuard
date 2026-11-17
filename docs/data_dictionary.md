# CacheGuard — Data Dictionary

**Owner:** Joy (Machine Learning Engineer)
**Status:** Updated for the processed real-measurement dataset.

## 1. Dataset overview

The primary processed dataset is stored at:

`data/processed/dataset.csv`

Verified composition:

- Total measurement rows: 1,800
- Unique experimental runs: 60
- Normal runs (label 0): 30
- Suspicious runs (label 1): 30
- Measurements per run: 30
- Measurements per class: 900

The dataset contains measurements collected at one-second intervals.

## 2. Columns

| Column | Type | Meaning | Source |
|---|---|---|---|
| `run_id` | String | Identifier for an experimental run. All measurements from the same run share an ID. | Experiment metadata |
| `label` | Integer | 0 = normal workload; 1 = suspicious controlled workload simulation. | Experiment metadata |
| `second` | Integer | Measurement interval within the run. | Collection data |
| `cache_references` | Integer | Number of cache references recorded during the interval. | `perf` |
| `cache_misses` | Integer | Number of cache misses recorded during the interval. | `perf` |
| `instructions` | Integer | Number of instructions executed during the interval. | `perf` |
| `cpu_cycles` | Integer | Number of CPU cycles recorded during the interval. | `perf` |
| `miss_rate` | Float | Cache misses divided by cache references. | Derived during preprocessing |

## 3. Dataset files

- `data/processed/dataset.csv` — primary processed dataset containing 60 runs.
- `data/processed/dataset_without_run058.csv` — sensitivity-analysis dataset excluding run 058.
- `data/processed/synthetic_dataset.csv` — synthetic dataset.
- `data/processed/synthetic_clean.csv` — cleaned synthetic dataset.

The primary dataset and sensitivity-analysis dataset must be reported separately.

## 4. Data-processing rules

The preprocessing script is:

`src/preprocessing/convert_lab_data.py`

It:

1. Keeps runs marked successful with return code 0 in the metadata.
2. Removes rows with missing required values.
3. Removes rows with zero cache references.
4. Converts normal to label 0 and suspicious to label 1.
5. Uses `cpu_cycles` for the CPU-cycle feature.
6. Recalculates miss rate from cache misses and cache references.

The raw experiment files are not included in the current repository clone.

## 5. Machine-learning rules

- Split training and testing by `run_id`, not by individual measurement rows.
- Use grouped cross-validation to prevent measurements from the same run appearing in both training and testing folds.
- The five feature configurations are all features, cache-only, miss-rate-only, instructions-only and cycles-only.
- The evaluated classifiers are Logistic Regression, Decision Tree and Random Forest.

## 6. Limitations

- The suspicious class represents a controlled workload simulation, not a confirmed real covert-channel attack.
- The dataset comes from one laboratory machine and one collection session.
- Results do not establish generalisation to other machines, operating systems or real attacks.
- Perfect classification scores must not be interpreted as proof of real-world attack detection.
