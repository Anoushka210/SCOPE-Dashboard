# SCOPE-Dashboard
## Strategic Crime Observation & Prediction Engine

> A global crime pattern analysis and prediction intelligence dashboard
> combining historical incident data, machine learning severity
> classification, time-series forecasting, and automated briefing
> generation.

---

## Live Deployment
| Service | URL |
|---|---|
| Frontend (Vercel) | https://scope-dashboard-kappa.vercel.app |
| Backend API (Render) | https://scope-dashboard.onrender.com |
| API Health Check | https://scope-dashboard.onrender.com/health |
| API Documentation | https://scope-dashboard.onrender.com/docs |

> Note: The Render backend is on a free tier and spins down after
> inactivity. First request after a cold start may take 30–60 seconds.
> Subsequent requests are fast.

---

## Project Overview

SCOPE-Dashboard is a B.Tech capstone project that ingests data from
five independent open-source crime and conflict datasets, normalizes
them into a unified schema, trains an offline machine learning model
to classify incident severity, and presents findings through an
interactive sci-fi themed intelligence dashboard.

The project is entirely free and open-source: no paid APIs, no cloud
ML compute, no proprietary data sources.

---

## Architecture
```
┌─────────────────────────────────────────────────┐
│              React + Vite Frontend              │
│        (Vercel — scope-dashboard-kappa)         │
│                                                 │
│ ThreatMap │ KPIs │ Predict │ Forecast │ Network │
│   Briefings │ DataEthics │ Sidebar Filters      │
└──────────────────┬──────────────────────────────┘
                   │ axios / VITE_API_URL
                   ▼
┌─────────────────────────────────────────────────┐
│                 FastAPI Backend                 │
│            (Render — scope-dashboard)           │
│                                                 │
│   /api/kpis /api/map-data /api/predict          │
│   /api/forecast /api/network /api/briefing      │
│   /api/pdf /api/filters /health                 │
└──────────────────┬──────────────────────────────┘
                   │ Python imports
                   ▼
┌─────────────────────────────────────────────────┐
│          Python Utility Layer (utils/)          │
│                                                 │
│ data_loader.py          feature_engineering.py  │
│ forecasting.py          network_graph.py        │
│ ai_summary.py           pdf_generator.py        │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│                  Data & Models                  │
│                                                 │
│ data/processed/illicit_networks_deployed.csv    │
│ data/processed/trafficking_cases.csv            │
│ models/incident_prediction.pkl (LightGBM)       │
│ models/feature_encoders.pkl                     │
└─────────────────────────────────────────────────┘
```

---

## Data Sources

| Dataset | Source | Crime Type | Records | Notes |
|---|---|---|---|---|
| ACLED | acleddata.com | Political violence, Protests | 968,024 rows / 3.1M events | Weekly Admin-1 aggregates, 1996–2026 |
| GTD | start.umd.edu/gtd | Terrorism | 209,706 | 1970–2020, START University of Maryland |
| ASAM | msi.nga.mil | Maritime Piracy | 9,182 | No fatality data — severity from hostility type |
| Mexico Cartel Events | Kaggle | Cartel Violence | 40 | 2023–2026, thin dataset |
| CTDC Synthetic | ctdatacollaborative.org | Human Trafficking | 268,515 | SYNTHETIC data, not real victim records |

**Full database (1.18M rows):** 3,328,529 real-world security events
after expanding ACLED weekly clusters by their EVENTS column.
3,074,097 total fatalities (excludes ASAM, which has no casualty data).
3,728 distinct named perpetrator groups.

**Deployed sample (150k rows):** Stratified random sample used in
the live app to stay within Render's free-tier memory limits.

---

## Machine Learning Model

**Algorithm:** LightGBM Classifier (winner of RandomForest / XGBoost
/ LightGBM comparison)

**Target:** Severity class derived from a weighted formula:
severity_score = (fatalities × 3.0) + (wounded × 1.0) +
(events × 1.0) + baseline
Discretized into 4 classes:
- Class 0 (Low): score ≤ 2.0
- Class 1 (Medium): 2.0 < score ≤ 5.0
- Class 2 (High): 5.0 < score ≤ 15.0
- Class 3 (Critical): score > 15.0

**Train/test split:** Time-based — trained on events before 2024,
tested on 2024+ events (267,015 test samples). No random split to
prevent temporal data leakage.

**Features used (leakage-free):** Spatial coordinates, temporal
features (year, month, day of week), frequency-encoded actor groups,
sub-event types, and country; fatalities and casualty counts
explicitly excluded from training features.

**Honest evaluation results (test set, 2024+):**

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Low (0) | 0.812 | 0.737 | 0.773 | 155,450 |
| Medium (1) | 0.330 | 0.302 | 0.315 | 49,256 |
| High (2) | 0.309 | 0.330 | 0.319 | 35,363 |
| Critical (3) | 0.436 | 0.699 | 0.537 | 26,946 |
| **Macro F1** | | | **0.486** | |

**Known limitation:** Medium and High class F1 scores (0.315 / 0.319)
are weak — the model struggles at the Medium/High severity boundary.
This is documented transparently on the Data & Ethics page of the
dashboard. Macro F1 dropped from an inflated 0.717 (which included
target leakage via the fatalities feature) to an honest 0.486 after
leakage was removed.

---

## Features

### 1. Global Threat Map
Interactive Deck.gl map with CartoDB Dark Matter basemap. Incident
points color-coded by crime type, scaled by severity. Heatmap layer
toggle. Click any point for a detail panel. Filters: region,
crime type, severity class, date range. Capped at 1,000 rendered
points with severity-weighted sampling when over cap.

### 2. KPI Intelligence Panel
Animated counters: total incidents, expanded event count, fatalities
(excludes ASAM), active actor groups, date coverage. Recharts bar
chart for crime type distribution. Non-violent categories
(Protests, Strategic Developments) filterable and off by default.

### 3. Threat Severity Predictor
Input form: region, crime type, sub-type, country, year, month.
LightGBM model returns predicted severity class, probability
distribution across all 4 classes, and SHAP feature importance
showing which inputs drove the prediction.

### 4. Forecasting Trends
SARIMA time-series model projecting monthly incident volumes by
region and crime type. 80% confidence interval bands. MAE and RMSE
validation metrics shown. Recharts ComposedChart with animated
line drawing.

### 5. Actor Network Analysis
NetworkX co-occurrence graph of named perpetrator groups, regions,
and crime types. Nodes sized by betweenness centrality. React Flow
interactive canvas — click any node to highlight connections and
view a detail panel. Coverage limited to GTD and Cartel datasets
(1970–2020 + 2023–2026); ACLED disorder types excluded to avoid
mislabeling administrative categories as actors.

### 6. Automated Intelligence Briefings
Rule-based narrative engine (no LLM API) generates natural-language
summaries: trend direction, dominant crime type, fatality trajectory,
most-affected sub-region. Exportable as a formatted PDF via
ReportLab.

### 7. Data & Ethics
Full documentation of data sources, known biases (underreporting in
certain regions, CTDC synthetic data disclosure, ASAM fatality gap),
severity formula, model performance table, and the Medium/High
boundary weakness. Mandatory disclaimer on every page.

---

## Local Development Setup

### Prerequisites
- Python 3.11
- Node.js 18+
- Git

### Backend
```bash
git clone https://github.com/Anoushka210/SCOPE-Dashboard.git
cd SCOPE-Dashboard
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Backend runs at http://localhost:8000
API docs at http://localhost:8000/docs

Note: Raw data files (data/raw/) and the full 158MB processed dataset
are gitignored. The deployed sample (data/processed/
illicit_networks_deployed.csv) is included. To regenerate from raw
sources, place source files in data/raw/ per the folder structure in
CLAUDE.md and run: python run_phase1.py

### Frontend
```bash
cd frontend
npm install
# Create .env.development
echo "VITE_API_URL=http://localhost:8000" > .env.development
npm run dev
```
Frontend runs at http://localhost:5173

### Docker (both services)
```bash
docker-compose up --build
```

---

## Ethical Disclaimer

> This prediction is based solely on historical data patterns and
> should not be interpreted as a forecast of future real-world events.

Additional notes:
- CTDC trafficking data is **synthetic** (not real victim records)
- ASAM fatality field is null for all records — severity uses
  hostility type codes instead
- ACLED underreports in regions with limited media access
- Cartel dataset contains only 40 records (2023–2026) — results
  for cartel_violence crime type should be interpreted cautiously
- Model Medium/High class boundary is a known weak point (F1 0.315
  / 0.319) — severity predictions in this range carry higher
  uncertainty

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Map | Deck.gl v9, MapLibre GL, CartoDB Dark Matter |
| Charts | Recharts |
| Network Graph | React Flow |
| Animations | Framer Motion |
| Backend | FastAPI, Uvicorn |
| ML Model | LightGBM, scikit-learn, SHAP |
| Forecasting | statsmodels SARIMA |
| PDF Generation | ReportLab |
| Data Processing | pandas, NumPy |
| Containerization | Docker, docker-compose |
| Frontend Deploy | Vercel |
| Backend Deploy | Render |

---

## Attribution

- ACLED: Armed Conflict Location & Event Data Project
  (acleddata.com) — free academic access
- GTD: Global Terrorism Database, START Center,
  University of Maryland (start.umd.edu/gtd)
- ASAM: Anti-Shipping Activity Messages, National
  Geospatial-Intelligence Agency (msi.nga.mil)
- CTDC: Counter Trafficking Data Collaborative synthetic
  dataset (ctdatacollaborative.org)
- Mexico boundaries: OCHA HDX Common Operational Datasets
