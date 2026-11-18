# Error Review (Security role)

**Owner:** Nakshathra (Security role)

**Status:** DRAFT. The owner changes this to FINAL after checking every line against the experiment results and signing off.

## 1. What was evaluated

Grouped 5-fold cross-validation, split by run, on 60 runs (30 normal, 30 suspicious). Three models and five feature sets.

Sources:
- `results/real_cv_results.csv`
- `results/real_accuracy_by_features.png`
- `results/real_confusion_matrices.png`
- `data/raw/experiment_20261112/quality_check.txt`

## 2. Results

| Feature set | Logistic Regression | Decision Tree | Random Forest |
|-------------|---------------------|---------------|---------------|
| all | 100.0% | 100.0% | 100.0% |
| cache_only | 100.0% | 100.0% | 100.0% |
| miss_rate_only | 100.0% | 100.0% | 100.0% |
| instructions_only | 100.0% | 100.0% | 100.0% |
| cycles_only (control) | 53.9% (±2.5) | 54.2% (±3.0) | 55.2% (±2.0) |

## 3. Errors with the first four feature sets

The cross-validation CSV reports 100% mean accuracy and zero standard deviation for all three models across the first four feature sets. This means no errors occurred in the evaluated folds.

The displayed all-features confusion matrices show 900 correct normal rows and 900 correct suspicious rows for each model, with zero errors.

A perfect score is expected on these strongly separated workload patterns. These results should not be interpreted as evidence of general performance on harder or unseen environments.

## 4. The control: cycles only

- The quality-check report gives mean cycle counts of approximately 3.771 billion for normal and 3.763 billion for suspicious measurements per interval. The suspicious/normal mean ratio is 0.9980. The difference between the means is small.
- The accuracy is close to 50%. For Logistic Regression, suspicious-class recall is 0.2667, so it mostly predicts normal. The Decision Tree has a recall of 0.8278, and the Random Forest about 0.55.
- This control demonstrates that the models do not automatically achieve perfect scores for every feature set. It provides useful evidence when interpreting the 100% results, but does not by itself rule out every possible evaluation issue.

## 5. Run 58 sensitivity analysis

Without Run 058, the first four feature sets still score 100% for all three models. The cycles-only control scores:
- Logistic Regression: 54.7% (±7.0)
- Decision Tree: 53.2% (±4.1)
- Random Forest: 54.2% (±3.2)

The sensitivity-analysis accuracy graph and all-features confusion matrices are consistent with these results. The all-features confusion matrices show 870 correct normal rows and 900 correct suspicious rows for each model, with zero errors.

Excluding Run 058 does not change the main conclusions.

Source: `results/no058_cv_results.csv` and the corresponding `no058` graphs.

## 6. What this review cannot say

- Which of miss rate and instruction count the all-feature models rely on.
- How the models behave on data that is harder than this experiment.
- Whether the results generalize to other machines, operating systems, workloads, or noisy environments.

## 7. Sign-off

Reviewed by: (Nakshathra to fill in after checking everything)

Date: (fill in after review)
