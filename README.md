# CacheGuard

### A Student Research Prototype for Controlled Cache-Pattern Classification Using CPU Performance Counters and Machine Learning

CacheGuard investigates whether CPU performance-counter measurements and machine-learning models can distinguish ordinary workloads from a controlled workload designed to imitate cache-access behaviour associated with a covert-channel sender/receiver pair.

**Research scope:** CacheGuard evaluates controlled workload simulations. It does not detect or confirm real covert-channel attacks.

---

## 1. Project Overview

CacheGuard collects CPU performance-counter measurements, processes the data, trains machine-learning classifiers and presents predictions through a web dashboard.

The project evaluates three classifiers:

- Logistic Regression
- Decision Tree
- Random Forest

The system includes a Python machine-learning pipeline, a FastAPI backend and a React frontend.

## 2. Experimental Dataset

The primary processed dataset is:

`data/processed/dataset.csv`

Verified dataset composition:

| Measurement | Value |
|---|---:|
| Experimental runs | 60 |
| Normal runs | 30 |
| Suspicious runs | 30 |
| Measurement rows | 1,800 |
| Measurements per run | 30 |
| Measurements per class | 900 |

Labels:

- **0 — Normal:** Ordinary workload.
- **1 — Suspicious:** Controlled workload simulation.

Each measurement contains five machine-learning features:

- `cache_references`
- `cache_misses`
- `instructions`
- `cpu_cycles`
- `miss_rate`

The dataset without run 058 is maintained separately for sensitivity analysis:

`data/processed/dataset_without_run058.csv`

It contains 59 runs: 29 normal and 30 suspicious.

## 3. Machine-Learning Pipeline

The pipeline performs:

1. Data preprocessing and validation.
2. Feature preparation.
3. Grouped training and evaluation.
4. Five-fold grouped cross-validation.
5. Model comparison and result visualisation.

The five evaluated feature configurations are:

- All features
- Cache-only
- Miss-rate-only
- Instructions-only
- Cycles-only

Cross-validation uses `StratifiedGroupKFold` to keep measurements from the same experimental run together and reduce run-level data leakage.

Detailed methodology and results:

- `docs/ml_pipeline.md`
- `docs/data_dictionary.md`

## 4. System Architecture

| Component | Technology | Location |
|---|---|---|
| Frontend | React, Vite | `frontend/` |
| Backend API | FastAPI | `src/api/` |
| Data preprocessing | Python | `src/preprocessing/` |
| Model training | Python, scikit-learn | `src/training/` |
| Model evaluation | Python | `src/evaluation/` |
| Trained models | Joblib | `models/` |
| Evaluation results | CSV and PNG | `results/` |

The frontend communicates with the backend API to submit measurements, retrieve predictions and display evaluation results.

## 5. Running the Project

### Requirements

- Python
- Node.js and npm
- Git

### Backend setup

From the repository root:

```bash
python -m venv venv
```

Activate the virtual environment.

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn main:app --reload --app-dir src/api
```

The API runs at:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### Frontend setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually:

`http://localhost:5173`

Keep the backend running while using the frontend.

## 6. Results and Interpretation

The project evaluates model performance using:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrices

The primary five-fold grouped cross-validation results show perfect mean accuracy for all three models using all features, cache-only features, miss-rate-only features and instructions-only features.

Cycles-only performance remains close to chance.

The sensitivity analysis excluding run 058 shows the same broad pattern. These findings demonstrate separation between the controlled workload classes in this dataset; they do not establish real-world attack detection.

Detailed results are available in:

- `results/real_cv_results.csv`
- `results/no058_cv_results.csv`

## 7. Limitations

- The suspicious class is a controlled workload simulation, not a confirmed real attack.
- The experiment was conducted on one laboratory machine during one collection session.
- The two workload classes have substantially different counter patterns.
- Background system activity and hyperthread interference were not fully controlled.
- The results do not establish generalisation to other CPUs, operating systems, workloads or real covert-channel attacks.
- High or perfect classification accuracy must not be interpreted as proof of real-world attack detection.

## 8. Team and Responsibilities

| Role | Member | Main responsibility |
|---|---|---|
| Frontend Developer | Pragna | React dashboard and interface |
| Backend Developer | Sameera | FastAPI and prediction endpoints |
| Hardware & Environment Engineer | Ashitha | Hardware measurements and experimental environment |
| Machine Learning Engineer | Joy | Data preprocessing, model training and evaluation |
| Security & Experimentation Engineer | Nakshathra | Protocol review, security analysis and limitations |

## 9. Repository Structure

```text
CacheGuard/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── data_dictionary.md
│   ├── environment_report.md
│   └── ml_pipeline.md
├── frontend/
├── models/
├── notebooks/
├── reports/
├── results/
├── src/
│   ├── api/
│   ├── evaluation/
│   ├── preprocessing/
│   └── training/
├── requirements.txt
└── README.md
```

## 10. Research Integrity

- Synthetic datasets are used for testing and must not be presented as real measurements.
- Raw experimental measurements must be preserved unchanged.
- Results must be reported with their dataset and evaluation methodology.
- Sensitivity-analysis results must be distinguished from primary experiment results.
- CacheGuard must not be described as a system that detects or confirms real covert-channel attacks.
