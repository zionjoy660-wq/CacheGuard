from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CacheGuard API")


class Metrics(BaseModel):
    cache_misses: float
    cache_references: float


@app.get("/health")
def health():
    return {"status": "ok", "project": "CacheGuard"}


@app.post("/predict")
def predict(metrics: Metrics):
    # PLACEHOLDER: no trained model yet. Replace later with the real ML model.
    miss_rate = metrics.cache_misses / metrics.cache_references if metrics.cache_references else 0
    return {
        "prediction": "placeholder",
        "miss_rate": round(miss_rate, 4),
        "note": "Not a real prediction. No model has been trained yet.",
    }
