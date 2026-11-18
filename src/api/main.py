"""CacheGuard API: serves the trained models and the real cross-validation results.

Run from the CacheGuard folder:
    uvicorn main:app --reload --app-dir src/api

Scope: controlled, simplified cache-pattern classification. Not a real covert-channel detector.
"""
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "real_models.joblib"
RESULTS_CSV = ROOT / "results" / "real_cv_results.csv"
RESULT_IMAGES = {"real_confusion_matrices.png", "real_accuracy_by_features.png"}
DEFAULT_MODEL = "Random Forest"

SCOPE_NOTE = (
    "CacheGuard classifies controlled cache-pattern simulations using CPU performance counters. "
    "It is a research prototype and does not detect or confirm real covert-channel attacks."
)

app = FastAPI(title="CacheGuard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_bundle = None


def get_bundle():
    """Load the model file once, the first time it is needed."""
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise HTTPException(status_code=503, detail=f"Model file not found: {MODEL_PATH}")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


class Counts(BaseModel):
    """One second of counter values."""
    cache_references: float = Field(..., gt=0, allow_inf_nan=False)
    cache_misses: float = Field(..., ge=0, allow_inf_nan=False)
    instructions: float = Field(..., ge=0, allow_inf_nan=False)
    cpu_cycles: float = Field(..., ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def misses_not_above_references(self):
        if self.cache_misses > self.cache_references:
            raise ValueError("cache_misses cannot be greater than cache_references")
        return self


def wording(label: int) -> str:
    if label == 1:
        return "This run looks suspicious according to the model."
    return "This run looks normal according to the model."


@app.get("/health")
def health():
    try:
        get_bundle()
        loaded = True
    except HTTPException:
        loaded = False
    return {"status": "ok", "project": "CacheGuard", "model_loaded": loaded}


@app.get("/models")
def list_models():
    return {"models": list(get_bundle()["models"].keys()), "default": DEFAULT_MODEL}


@app.post("/predict")
def predict(counts: Counts, model: str = DEFAULT_MODEL):
    bundle = get_bundle()
    models, features = bundle["models"], bundle["features"]
    if model not in models:
        raise HTTPException(status_code=400, detail=f"Unknown model. Choose one of: {list(models)}")

    miss_rate = counts.cache_misses / counts.cache_references
    row = pd.DataFrame([{
        "cache_references": counts.cache_references,
        "cache_misses": counts.cache_misses,
        "instructions": counts.instructions,
        "cpu_cycles": counts.cpu_cycles,
        "miss_rate": miss_rate,
    }])[features]

    all_models = []
    for name, m in models.items():
        label = int(m.predict(row)[0])
        all_models.append({
            "model": name,
            "label": label,
            "label_name": bundle["label_names"][label],
            "probability_suspicious": round(float(m.predict_proba(row)[0][1]), 4),
        })
    chosen = next(r for r in all_models if r["model"] == model)
    return {
        "model": model,
        "label": chosen["label"],
        "label_name": chosen["label_name"],
        "probability_suspicious": chosen["probability_suspicious"],
        "miss_rate": round(miss_rate, 6),
        "message": wording(chosen["label"]),
        "all_models": all_models,
        "scope_note": SCOPE_NOTE,
    }


@app.get("/results")
def results():
    if not RESULTS_CSV.exists():
        raise HTTPException(status_code=404, detail=f"Results file not found: {RESULTS_CSV}")
    df = pd.read_csv(RESULTS_CSV)
    return {"rows": df.to_dict(orient="records"), "scope_note": SCOPE_NOTE}


@app.get("/results/image/{name}")
def result_image(name: str):
    if name not in RESULT_IMAGES:
        raise HTTPException(status_code=404, detail="Unknown image")
    path = ROOT / "results" / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(path)
