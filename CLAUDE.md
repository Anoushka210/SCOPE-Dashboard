# SCOPE-Dashboard — Claude Code Project Context

## Project Identity
**Name:** SCOPE-Dashboard (Strategic Crime Observation & Prediction Engine)  
**Type:** Capstone project — global crime pattern analysis and prediction dashboard  
**Owner:** Anoushka (B.Tech final year)  
**Status:** LIVE — Deployed to Render (Backend) and Vercel (Frontend)  
**Live Backend (Render):** https://scope-dashboard.onrender.com  
**Live Frontend (Vercel):** https://scope-dashboard-kappa.vercel.app  

---

## Architecture Overview

### Backend — FastAPI (Python)
- Entry: `backend/main.py`
- Routers: `backend/routers/` (kpis, map_data, predict, forecast, network, briefing, pdf, filters)
- Runs on port 8000
- Loads data and models ONCE at startup via FastAPI lifespan pattern
- Dependencies: `backend/requirements.txt`

### Frontend — React + Vite
- Entry: `frontend/src/main.jsx`
- Components: `frontend/src/components/`
- Global filter state: `frontend/src/context/FilterContext.jsx`
- Runs on port 5173 in dev
- API base URL via `import.meta.env.VITE_API_URL` — never hardcoded
- Dependencies: `frontend/package.json`

### Python Utilities
- `utils/data_loader.py` — loads and normalizes all raw sources
- `utils/feature_engineering.py` — encodes features (leakage-free, pre-event only), buckets severity
- `utils/forecasting.py` — SARIMA time-series forecasting
- `utils/network_graph.py` — NetworkX actor/region co-occurrence graph (named groups only)
- `utils/ai_summary.py` — rule-based narrative template engine
- `utils/pdf_generator.py` — ReportLab PDF briefing generator
- `utils/prepare_deployment_data.py` — generates trimmed deployment CSV

### Data
- `data/processed/illicit_networks_deployed.csv` — 150k stratified rows used by backend at runtime
- `data/processed/illicit_networks.csv` — 1.18M raw multi-source rows
- `data/full_kpi_summary.json` — precomputed true totals across full 1.18M dataset
- `data/processed/trafficking_cases.csv` — 268,515 CTDC synthetic records

### Models
- `models/incident_prediction.pkl` — winning LightGBM classifier (retrained without target leakage)
- `models/feature_encoders.pkl` — fitted encoders for inference (fitted on training split only)
- `models/metrics.json` — full honest per-class evaluation metrics
- `models/shap_summary.png` — global SHAP feature importance plot

---

## Data Sources
| Source | File | Crime Type | Rows | Notes |
|---|---|---|---|---|
| ACLED | 6 regional xlsx files | political_violence | 968,024 | Admin-1 centroids, weekly aggregates. Counting EVENTS multiplier expands to 3,109,601 security events |
| GTD | globalterrorismdb_0522dist.xlsx | political_violence | 209,706 | 1970–2020, START/UMD. Primary source for named organized groups |
| ASAM | Anti-Shipping_Activity_Messages.csv | piracy | 9,182 | No fatality data — severity from hostilitytype_l only |
| Cartel MX | mexico_cartel_events_2023_2026.csv | cartel_violence | 40 | Thin dataset — municipal centroids |
| CTDC | ctdc_global_synthetic_data_v2026.csv | trafficking | 268,515 | SYNTHETIC data — not real victim records |

---

## Unified Schema & Scale Realities
Key columns every backend endpoint may reference: event_id, source_dataset, event_date, year, month, country, region,
latitude, longitude, crime_type, sub_type, actor_group, fatalities, severity_score

- `fatalities` is NULL for all ASAM rows — strictly excluded from fatality aggregates
- `severity_score` is a **continuous, unbounded raw score** (Min: 1.0, Max: 36,825.0 across full database). It is NOT an integer from 1–5.
- Discretized into 4 threat classes for machine learning:
  - Class 0: Low (Score <= 2.0)
  - Class 1: Medium (2.0 < Score <= 5.0)
  - Class 2: High (5.0 < Score <= 15.0)
  - Class 3: Critical (Score > 15.0)

---

## ML Model Details (Leakage-Free Retraining)
**Winner:** LightGBM classifier  
**Target:** severity_score bucketed into 4 classes (0: Low, 1: Medium, 2: High, 3: Critical)  
**Leakage Audit:** All target-defining features (`fatalities`, `EVENTS`, `nkill`, `nwound`) were audited and removed. Encoders fitted strictly on training years.  
**Train/test split:** Time-based — train on events before 2024 (919,937 samples), test on 2024+ (267,015 samples).

**Honest Test Set Metrics (Leakage-Free):**
| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Low (0) | 0.8122 | 0.7370 | 0.7728 | 155,450 |
| Medium (1) | 0.3304 | 0.3018 | 0.3154 | 49,256 |
| High (2) | 0.3093 | 0.3302 | 0.3194 | 35,363 |
| Critical (3) | 0.4357 | 0.6988 | 0.5367 | 26,946 |
| **Overall** | **Accuracy: 59.90%** | | **Macro F1: 0.4861** | **Total: 267,015** |

**Model Assessment:**
Removing the casualty count leak dropped the artificial Macro F1 from 0.717 to an honest 0.4861. The model demonstrates genuine contextual predictive power: Critical-class events achieve 69.88% recall, and Low events achieve 73.70% recall. Medium and High classes exhibit overlap (F1 ~0.31-0.32) because pre-incident indicators cannot always forecast the escalation severity of a confrontation prior to the event.

---

## Frontend Design System
**Theme:** Sci-fi dark  
**Colors:**
- Background: `#0a0f1e`
- Panel background: `#0d1b2a`
- Electric blue accent: `#00d4ff`
- Neon green (positive): `#39ff14`
- Amber (warning): `#ff9500`
- Critical red: `#ff3333`
- Text primary: `#e2e8f0`
- Text secondary: `#94a3b8`

**Fonts:**
- Headings/titles: "Orbitron" (Google Fonts)
- Data values/numbers: "Share Tech Mono" (Google Fonts)
- Body text: system sans-serif

---

## Critical Rules for This Codebase
1. Never hardcode `localhost` in frontend — always use `import.meta.env.VITE_API_URL`
2. Never fill ASAM fatalities with 0 — keep as null and label aggregates accordingly
3. CTDC data is synthetic — never describe it as real victim records in any UI copy or generated text
4. The disclaimer must appear on every page and in every PDF footer:
   "This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."
5. Stop and wait for explicit approval before any git push or deployment step
6. Never fabricate data, metrics, or API responses to make a test pass
7. Map descriptions must be marked as synthesized event summaries, not raw source text
8. Actor graph entities are restricted to real organized groups (GTD and Cartel); ACLED disorder types are excluded from actor labeling
