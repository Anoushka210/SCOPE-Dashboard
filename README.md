# 🛡️ SCOPE — Strategic Crime Observation & Prediction Engine

SCOPE (Strategic Crime Observation & Prediction Engine) is an end-to-end multi-source threat intelligence dashboard for global security incident monitoring, predictive severity modeling, temporal forecasting, and actor network analysis.

The platform is migrated to a high-performance **FastAPI backend** and **React + Vite frontend**.

---

## 📌 Features & Architecture

- **Dynamic Global KPIs**: Aggregates over 1.18 million historical records (3.33M true security occurrences when accounting for ACLED weekly cluster expansion) across ACLED, GTD, ASAM, and Cartel datasets.
- **Geospatial Threat Map**: Deck.gl Scatterplot and Density Heatmap layers over an open-source CartoDB Dark Matter basemap, with severity-weighted sampling capped at 1,000 points.
- **Machine Learning Severity Classifier**: LightGBM model classifying incident severity into 4 discrete threat levels (*Low*, *Medium*, *High*, *Critical*) with real-time SHAP feature attribution. **Trained strictly on pre-event contextual signals without target casualty leakage.**
- **Temporal Forecasting**: SARIMA time-series model predicting monthly incident volume with 80% confidence intervals and held-out validation metrics.
- **Organized Syndicate Network**: Interactive React Flow graph calculating degree and betweenness centrality across named groups from GTD and Cartel datasets.
- **Automated Intelligence Briefings**: Rule-based narrative synthesis engine generating downloadable ReportLab PDF briefings.
- **Data Governance & Ethics**: Comprehensive documentation of synthetic datasets (CTDC), ACLED cluster multipliers, and mandatory disclaimer framing.

---

## 🤖 Honest Machine Learning Performance (Leakage-Free Retraining)

Following an audit that identified and removed target-derived casualty features (`fatalities`, `EVENTS`, `nkill`, `nwound`) and fit encoders strictly on pre-2024 training years, the model was evaluated on a time-based test split ($\ge$ 2024, 267,015 test events):

- **Winning Classifier**: LightGBM
- **Overall Macro F1**: **0.4861** | **Overall Accuracy**: **59.90%**
- **Test Set Per-Class Metrics**:
  - **Low Severity (0)**: Precision = 81.22% | Recall = 73.70% | F1 = 0.7728 | Support = 155,450
  - **Medium Severity (1)**: Precision = 33.04% | Recall = 30.18% | F1 = 0.3154 | Support = 49,256
  - **High Severity (2)**: Precision = 30.93% | Recall = 33.02% | F1 = 0.3194 | Support = 35,363
  - **Critical Severity (3)**: Precision = 43.57% | Recall = 69.88% | F1 = 0.5367 | Support = 26,946
- **Analytical Assessment**: With target leakage removed, the model demonstrates genuine predictive value from contextual indicators alone: Critical-class events achieve **69.88% recall**, and Low-severity events achieve **73.70% recall**. Boundary overlap between Medium and High classes reflects the real-world challenge of predicting escalation severity prior to an engagement.

---

## 📐 Severity Scale Realities

The continuous severity score is calculated as:
$$\text{Severity Score} = (\text{Fatalities} \times 3.0) + (\text{Wounded/Events} \times 1.0) + \text{Baseline Weight}$$

The raw score is **unbounded** (Min: 1.0, Max: 36,825.0) and bucketed into 4 discrete classification targets:
- **Low (Class 0)**: Score $\le 2.0$
- **Medium (Class 1)**: $2.0 < \text{Score} \le 5.0$
- **High (Class 2)**: $5.0 < \text{Score} \le 15.0$
- **Critical (Class 3)**: $\text{Score} > 15.0$

---

## 📚 Data Sources & Attribution

- **ACLED (Armed Conflict Location & Event Data Project)**: Political violence and demonstration events (1996 - 2026).
- **GTD (Global Terrorism Database)**: Global terrorist incident records (1970 - 2020). Primary source for named organized entities.
- **ASAM (Anti-Shipping Activity Messages - NGA)**: Maritime piracy and vessel attack reports (1978 - 2024). Fatalities are null and kept null.
- **Mexico Cartel Violence Dataset**: Sub-national cartel events and municipal boundary centroids.
- **CTDC (Counter Trafficking Data Collaborative)**: Synthetic human trafficking demographics.

---

## 🛠️ Local Development & Running

### 1. Run FastAPI Backend:
```bash
# From repository root
uvicorn backend.main:app --reload --port 8000
```
Backend API interactive documentation available at `http://localhost:8000/docs`.

### 2. Run React Frontend:
```bash
cd frontend
npm install
npm run dev
```
Access dashboard at `http://localhost:5173`.

---

## ⚠️ Mandatory Ethical & Analytical Disclaimer

> **"This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."**
