# ML Pipeline (Machine Learning role)

**Owner:** Joy
**Status:** Works on synthetic data. Not yet run on real data.

## 1. What the pipeline does
The pipeline takes a table of CPU counter values for each run: cache-references, cache-misses, instructions and cycles. Each run has a label, normal or suspicious. It trains three models and outputs accuracy, precision, recall, F1-score and confusion matrices. Right now the input table is synthetic (made by code), so the pipeline only proves that our code runs from start to finish.


## 2. The three steps and their commands
(For each step: what it does, the command, and what file it creates.)
1. Preprocess: [VERIFY: what does the notebook do here? For example: make the synthetic data, add run IDs, split by run, scale the features.] Command: [VERIFY: notebook cell or script name]. Creates: [VERIFY: file name, or "nothing saved"].
2. Train: trains Logistic Regression, Decision Tree and Random Forest on the training runs. Command: [VERIFY]. Creates: [VERIFY: is a model file saved?].
3. Evaluate: tests each model on the held-out runs and shows accuracy, precision, recall, F1-score and confusion matrices. Command: [VERIFY]. Creates: [VERIFY: are results saved, or only shown on screen?].

## 3. The three models
- Logistic Regression: draws a simple boundary between normal and suspicious runs. It is fast and easy to explain.
- Decision Tree: asks a series of yes/no questions about the counters, such as "is the cache-miss count high?". We can read its rules.
- Random Forest: many decision trees voting together. It is usually more stable than one tree.

We start with simple models because we have little data and need a fair baseline. We will only try something more complex if the results need it.

## 4. Why we split by run
Data leakage means information from the test data leaks into training, so the scores look better than they really are.
Samples from the same run look very similar. If we split by random rows, a run can appear in both training and testing. The model then just recognises that run, and the score is unfairly high. When we split by run, each run is entirely in training or entirely in testing.

## 5. What the scores mean
- Accuracy: out of all runs, how many did the model get right.
- Precision: out of the runs flagged suspicious, how many were really suspicious.
- Recall: out of the really suspicious runs, how many did we catch.
- F1-score: one number that balances precision and recall.


## 6. What the current results are, and what they are not
The scores come from synthetic data.
- They prove: the code runs from start to finish, and the split, training and evaluation steps work.
- They do NOT prove: that we detect any covert channel, that the models work on real CPUs, or that cache counters can separate normal runs from suspicious ones.
We do not report these scores as results.

## 7. What happens when real data arrives
- Collect real runs with `perf` on a native Linux machine. Save the raw output unchanged in `data/raw/`. We never edit it.
- Build a feature table from the raw data. Keep run IDs and labels. [VERIFY: which file or folder in `data/processed/`?]
- In the notebook, replace the synthetic data step with a step that loads the real feature table. [VERIFY: which cell or file changes?]
- Run the same steps again: split by run, fit preprocessing on training data only, train, evaluate.
- Report scores only if they come from a documented, valid experiment, and keep synthetic files clearly named with "synthetic".

## 8. Limits
- Cache misses alone do not prove an attack.
- We test only one controlled scenario, so we cannot say we detect every covert channel or side-channel attack.
- The real dataset will probably be small, so scores may not generalise.
- A model could learn differences like the machine or the collection settings instead of the channel. We must check this.
- No real data is collected yet. 