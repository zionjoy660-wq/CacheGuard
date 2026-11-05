# Data Dictionary (ML role)

**Status:** DRAFT. Agree the final columns with the team and sir before collecting real data.
Only use counter events that the collection machine really supports (see `environment_report.md`).

## Columns

| Column | Type | Meaning | Source |
|--------|------|---------|--------|
| run_id | integer | One run of the experiment. All samples of a run share one id. Used to split train and test by run. | Collection script |
| label | integer | 0 = normal run, 1 = suspicious (controlled covert-channel) run | Experiment protocol |
| cache_references | number | Cache references counted in the sample window | `perf` |
| cache_misses | number | Cache misses counted in the same window | `perf` |
| instructions | number | Instructions executed in the same window | `perf` |
| cpu_cycles | number | CPU cycles in the same window | `perf` |
| miss_rate | number | cache_misses / cache_references (derived in preprocessing) | Derived |

## Rules
- `data/raw/` is never edited. Cleaned data goes to `data/processed/`.
- Synthetic files must have `synthetic` in the file name.
- A sample with cache_references = 0, or cache_misses greater than cache_references, is removed during cleaning.
- Train and test are split by `run_id`, never by random rows (prevents data leakage).
- Both labels must be collected on the same machine, so the label is not explained by the machine.

## Pipeline
1. `src/preprocessing/preprocess.py`: validate and clean.
2. `src/training/train.py`: split by run, train Logistic Regression, Decision Tree, Random Forest.
3. `src/evaluation/evaluate.py`: accuracy, precision, recall, F1 and confusion matrices on the test runs.

## Limits
- Cache misses alone do not prove an attack.
- Scores from synthetic data only test the code.
