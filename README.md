# CacheGuard

Detecting cache-based covert channels using CPU performance-counter data and machine learning.

> **Status:** Planning and early feasibility stage. No real measurements or trained models yet.

## Team and Roles

| Role | Member | Main folder |
|------|--------|-------------|
| Frontend Developer | PRAGNA | `src/frontend/` |
| Backend Developer | SAMEERA | `src/backend/` |
| Hardware & Environment Engineer | ASHITHA | `docs/` |
| Machine Learning Engineer | JOY | `notebooks/`, `models/` |
| Security & Experimentation Engineer | NAKSHATHRA | `docs/`, `data/raw/` |

## Folder Structure

| Folder | What goes here |
|--------|----------------|
| `docs/` | Environment report, experiment design, notes |
| `data/raw/` | Real measurements exactly as collected (never edit) |
| `data/processed/` | Cleaned data and synthetic test data (label clearly) |
| `notebooks/` | Jupyter notebooks for ML work |
| `src/` | Application code (backend, frontend, ML helpers) |
| `models/` | Saved trained models |
| `results/` | Graphs, tables, evaluation outputs |
| `reports/` | Progress updates and final report |

## Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

## Rules for the Team

1. Synthetic data is only for testing code. Name those files with `synthetic_` and never present them as real results.
2. Real measurements go in `data/raw/` and are never edited by hand.
3. Commit small changes often, with clear messages.
4. Work on your own branch, then open a pull request.
