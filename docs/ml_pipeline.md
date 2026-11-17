# CacheGuard — Machine Learning Pipeline

**Owner:** Joy (Machine Learning Engineer)
**Status:** Real-data pipeline implemented; sensitivity analysis completed.

## 1. Overview

The CacheGuard ML pipeline evaluates whether CPU performance-counter measurements can distinguish two controlled workload patterns:

- **Normal (label 0):** Ordinary workload.
- **Suspicious (label 1):** Controlled workload designed to imitate cache-access behaviour associated with a covert-channel sender/receiver pair.

The pipeline uses real measurements collected during a controlled laboratory experiment. It trains and evaluates three machine-learning models: Logistic Regression, Decision Tree and Random Forest.

CacheGuard is a student research prototype. It classifies controlled cache-pattern simulations; it does not detect or confirm real covert-channel attacks.

## 2. Data preprocessing

The raw experiment measurements are stored separately from the processed dataset.

Primary input files:

- `data/experiment_20261112/processed/measurements.csv`
- `data/experiment_20261112/metadata/run_metadata.csv`

Conversion command:

```bash
python src/preprocessing/convert_lab_data.py \
  --measurements data/experiment_20261112/processed/measurements.csv \
  --metadata data/experiment_20261112/metadata/run_metadata.csv
```

Output:

`data/processed/dataset.csv`

The conversion script:

1. Keeps runs marked successful with return code 0.
2. Removes rows with missing required values or zero cache references.
3. Converts `normal` to label 0 and `suspicious` to label 1.
4. Renames `cycles` to `cpu_cycles`.
5. Recalculates miss rate using cache misses divided by cache references.

The output contains:

`run_id, label, second, cache_references, cache_misses, instructions, cpu_cycles, miss_rate`

The raw experiment files are retained unchanged.

## 3. Models

Three baseline classifiers are used:

- **Logistic Regression:** A linear classification model used as a simple baseline.
- **Decision Tree:** A tree-based model that makes decisions using feature thresholds.
- **Random Forest:** An ensemble of decision trees that combines their predictions.

The models use five features:

- `cache_references`
- `cache_misses`
- `instructions`
- `cpu_cycles`
- `miss_rate`

StandardScaler is included in the Logistic Regression and Decision Tree/Random Forest pipelines.

## 4. Training and held-out testing

Training is performed using:

```bash
python src/training/train.py \
  --input data/processed/dataset.csv
```

The training script uses `GroupShuffleSplit` with a 25% test size and random seed 42.

Grouping is performed using `run_id`, so measurements from one experimental run cannot appear in both training and held-out test sets.

The trained models are saved in:

`models/real_models.joblib`

The synthetic model files are retained separately and are not used as evidence of real-data performance.

## 5. Five-fold grouped cross-validation

Cross-validation is performed using:

```bash
python src/training/cross_validate.py \
  --input data/processed/dataset.csv \
  --tag real_ \
  --save-final
```

When --save-final is used, the script also trains the all-feature models on the complete dataset and saves the model bundle as models/real_models.joblib.

The script uses `StratifiedGroupKFold` with five folds and random seed 42.

All measurements belonging to a particular `run_id` remain together in one fold. An assertion checks that no run appears in both training and testing within a fold.

Five feature configurations are evaluated:

1. `all` — all five features.
2. `cache_only` — cache references, cache misses and miss rate.
3. `miss_rate_only` — miss rate.
4. `instructions_only` — instruction count.
5. `cycles_only` — CPU cycles, used as a control.

Each feature configuration is evaluated using all three models.

The reported metrics are accuracy, precision, recall and F1-score, calculated as the mean and standard deviation across folds.

## 6. Primary experiment results

The primary experiment contains 60 runs:

- 30 normal runs.
- 30 suspicious runs.
- 1,800 one-second measurement rows.

The cross-validation results are stored in:

`results/real_cv_results.csv`

The primary results report 100% mean accuracy for all three models using:

- All features.
- Cache-only features.
- Miss-rate-only features.
- Instruction-only features.

The cycles-only control produces lower accuracy:

- Logistic Regression: 53.89%.
- Decision Tree: 54.17%.
- Random Forest: 55.22%.

These findings show that the controlled workload patterns are highly separable using cache-related measurements and instruction counts in this experimental setup.

## 7. Sensitivity analysis: excluding run 058

Run 058 was identified as an unusual normal run, with approximately 13 million cache references per measurement interval compared with approximately 500 million in typical normal runs.

A separate dataset excluding run 058 was examined:

`data/processed/dataset_without_run058.csv`

Verified dataset composition:

- Total runs: 59.
- Normal runs: 29.
- Suspicious runs: 30.
- Total measurements: 1,770.
- Measurements per run: 30.

The sensitivity dataset is slightly imbalanced because run 058 was a normal run.

The corresponding results are stored in:

`results/no058_cv_results.csv`

The sensitivity results retain 100% mean accuracy for all three models using all, cache-only, miss-rate-only and instructions-only feature sets.

Cycles-only accuracy remains close to chance:

- Logistic Regression: 54.70%.
- Decision Tree: 53.20%.
- Random Forest: 54.15%.

This comparison indicates that excluding run 058 does not materially change the interpretation of the primary results.

The exact execution command and provenance of the sensitivity-results CSV should be retained or documented separately when confirmed.

## 8. Evaluation and visualisations

The evaluation script is:

`src/evaluation/evaluate.py`

It evaluates saved models against their held-out test runs and produces accuracy, precision, recall, F1-score and confusion matrices.

The cross-validation script also generates:

- `results/real_accuracy_by_features.png`
- `results/real_confusion_matrices.png`

The sensitivity analysis generates corresponding files prefixed with `no058_`.

Cross-validation results and held-out test results are separate evaluation procedures and must not be presented as interchangeable.

## 9. Limitations

- The experiment uses controlled cache-pattern workloads, not a real covert-channel attack.
- The two workload classes were deliberately designed to have substantially different cache behaviour.
- Cache-related features and instruction counts independently separate the two classes in this dataset.
- CPU cycles alone provide results close to chance.
- The experiment was conducted on one machine during one laboratory session.
- Background system activity and hyperthread interference were not fully controlled.
- The results do not establish generalisation to other CPUs, operating systems, workloads or real attacks.
- Perfect classification accuracy must not be interpreted as proof of real-world attack detection.

## 10. Future work

- Collect measurements on additional machines.
- Introduce more realistic and less separable workloads.
- Investigate the effect of background processes and hyperthread contention.
- Validate the models on independent collection sessions.
- Improve outlier detection and experimental controls.
- Evaluate whether the observed patterns generalise beyond the current laboratory setup.