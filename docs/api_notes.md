# CacheGuard API Documentation

## 1. Overview

The CacheGuard API is a FastAPI backend that loads trained machine-learning models, accepts CPU performance-counter measurements, generates workload classifications, and provides cross-validation results and result images.

It is designed for controlled cache-pattern simulations. It is a research prototype and does not detect or confirm real covert-channel attacks.

## 2. Technology Stack

- Python
- FastAPI
- Pydantic
- Pandas
- Joblib
- Uvicorn

## 3. Model and Result Files

The API uses the following files:

- `models/real_models.joblib` – trained model bundle.
- `results/real_cv_results.csv` – cross-validation results.
- `results/real_confusion_matrices.png` – confusion matrix image.
- `results/real_accuracy_by_features.png` – accuracy comparison image.

The model bundle is loaded when first required and cached for subsequent requests.

## 4. Running the API

Run the following command from the CacheGuard project root:

```bash
uvicorn main:app --reload --app-dir src/api
```

Local API address: `http://127.0.0.1:8000`

## 5. API Endpoints

### 5.1 Health Check

**Method:** GET
**Endpoint:** `/health`

Checks whether the API is responding and whether the trained model bundle is available.

Example response:

```json
{
  "status": "ok",
  "project": "CacheGuard",
  "model_loaded": true
}
```

### 5.2 List Available Models

**Method:** GET
**Endpoint:** `/models`

Returns the available trained models and the default model.

Available models:
- Logistic Regression
- Decision Tree
- Random Forest

Default model: Random Forest.

### 5.3 Workload Prediction

**Method:** POST
**Endpoint:** `/predict`

Optional query parameter: `model`

The model parameter selects the classifier. If omitted, Random Forest is used.

**Request body:**

```json
{
  "cache_references": 505969350,
  "cache_misses": 3025,
  "instructions": 4795372685,
  "cpu_cycles": 3770873246
}
```

The API calculates the cache miss rate:

`miss_rate = cache_misses / cache_references`

It then arranges the input features in the order expected by the trained models.

**Response fields:**

- `model` – selected classifier.
- `label` – predicted numeric class.
- `label_name` – predicted class name.
- `probability_suspicious` – predicted probability for the suspicious class.
- `miss_rate` – calculated cache miss rate.
- `message` – human-readable prediction message.
- `all_models` – predictions and suspicious probabilities from all three classifiers.
- `scope_note` – research scope and limitation statement.

Class labels:
- `0` – normal
- `1` – suspicious

### 5.4 Retrieve Cross-Validation Results

**Method:** GET
**Endpoint:** `/results`

Reads `results/real_cv_results.csv` and returns its records as JSON.

Each result contains the feature set, model name, and cross-validation metrics, including accuracy, precision, recall, and F1-score with their standard deviations.

The response also includes the research scope note.

### 5.5 Retrieve Result Images

**Method:** GET
**Endpoint:** `/results/image/{name}`

Serves approved result images.

Allowed image names:
- `real_confusion_matrices.png`
- `real_accuracy_by_features.png`

Other image names are rejected.

## 6. Input Validation and Error Handling

The prediction request uses a Pydantic model named `Counts`.

The API validates the following conditions:

- `cache_references` must be greater than zero.
- `cache_misses` must be zero or greater.
- `instructions` must be zero or greater.
- `cpu_cycles` must be zero or greater.
- Counter values must be finite.
- `cache_misses` cannot exceed `cache_references`.

Other error responses include:

- `400` – unknown model selection.
- `404` – results file, image, or requested image name not found.
- `503` – trained model file not found.
- `422` – invalid request body or failed input validation.

## 7. Frontend Integration

The API enables Cross-Origin Resource Sharing (CORS) for:

- `http://localhost:5173`
- `http://127.0.0.1:5173`

The React frontend communicates with the backend using the health, prediction, results, and result-image endpoints.

## 8. Testing Performed

The following tests were performed against the running local API:

| Test | Observed result |
|---|---|
| GET `/health` | API responded and `model_loaded` was true |
| GET `/results` | Returned 15 cross-validation result records |
| POST `/predict` with normal sample | All three models predicted normal |
| POST `/predict` with suspicious sample | All three models predicted suspicious |
| POST `/predict` with cache misses greater than references | Request rejected by input validation |

The normal and suspicious samples were controlled experimental examples. These tests demonstrate API operation on those samples, not real-world attack detection.

## 9. Research Scope and Limitations

CacheGuard is a student research prototype that classifies controlled cache-pattern simulations using CPU performance-counter measurements.

Its predictions should not be interpreted as proof of a real covert-channel attack. The API returns a scope note with its responses to communicate this limitation.