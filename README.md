# 🛡️ SCOPE — Strategic Crime Observation & Prediction Engine

SCOPE (Strategic Crime Observation & Prediction Engine) is an end-to-end multi-source threat intelligence dashboard for global security incident monitoring, predictive severity modeling, temporal forecasting, and actor network analysis.

---

## 📌 Features & Architecture

- **Dynamic Global KPIs**: Aggregates over 1.18 million historical security events across ACLED, GTD, ASAM, and Cartel datasets.
- **Geospatial Map**: Plotly Scattermap visualization with 1,000-point rendering caps and multi-dimensional filters.
- **Machine Learning Severity Classifier**: Trained LightGBM model classifying incident severity into 4 discrete threat levels (*Low*, *Medium*, *High*, *Critical*) with real-time SHAP explanation.
- **Temporal Forecasting**: SARIMA time-series model predicting monthly incident volume with 80% confidence intervals and held-out validation metrics.
- **Actor Network Analysis**: Graph-theoretic network visualization calculating degree and betweenness centrality.
- **Automated PDF Briefings**: Rule-based narrative synthesis engine generating downloadable ReportLab PDF briefings.
- **Data Governance & Ethics**: Comprehensive documentation of synthetic datasets (CTDC), missingness, and mandatory disclaimer framing.

---

## 🌐 Live Deployed Application

- **Streamlit Community Cloud**: [https://scope-dashboard.streamlit.app/](https://scope-dashboard.streamlit.app/)
- **GitHub Repository**: [https://github.com/Anoushka210/SCOPE-Dashboard](https://github.com/Anoushka210/SCOPE-Dashboard)

---

## 🤖 Machine Learning Model Performance & Confusion Matrix

The winning LightGBM model was evaluated on a time-based test split ($\ge$ 2024, 267,015 test events):

- **Overall Macro F1**: **0.7170** | **Overall Accuracy**: **76.96%**
- **Critical Severity Class (Class 3)**:
  - **Test Support**: **26,946 events**
  - **Precision**: **92.65%** (High precision; minimal false alarms)
  - **Recall**: **79.81%** (Successfully identifies ~80% of critical violent incidents)
  - **F1 Score**: **0.8575**
- **Per-Class Metrics Summary**:
  - **Low Severity (0)**: Precision = 82.92% | Recall = 88.42% | F1 = 0.8558 | Support = 155,450
  - **Medium Severity (1)**: Precision = 57.96% | Recall = 50.49% | F1 = 0.5397 | Support = 49,256
  - **High Severity (2)**: Precision = 61.71% | Recall = 61.31% | F1 = 0.6151 | Support = 35,363
- **Analytical Tradeoffs**: The model excels at identifying *Low* (Class 0) and *Critical* (Class 3) security events due to distinct fatality and weapons indicators. *Medium* and *High* classes exhibit moderate overlap due to boundary ambiguity between low-fatality skirmishes and localized property incidents.

---

## 📚 Data Sources & Attribution

- **ACLED (Armed Conflict Location & Event Data Project)**: Political violence and demonstration events (1996 - 2026).
- **GTD (Global Terrorism Database)**: Global terrorist incident records (1970 - 2020).
- **ASAM (Anti-Shipping Activity Messages - NGA)**: Maritime piracy and vessel attack reports (1978 - 2024).
- **Mexico Cartel Violence Dataset**: Sub-national cartel events and municipal boundary centroids.
- **CTDC (Counter Trafficking Data Collaborative)**: Synthetic human trafficking case demographics (2002 - 2024).

---

## 🛠️ Local Setup & Running

### Option 1: Native Virtual Environment

1. **Create and Activate Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Data Processing Pipeline**:
   ```bash
   python utils/data_loader.py
   python run_phase1.py
   ```

4. **Train Machine Learning Models**:
   ```bash
   python train_threat_model.py
   ```

5. **Launch Streamlit Dashboard**:
   ```bash
   streamlit run app.py
   ```
   Access application at `http://localhost:8501`.

---

### Option 2: Docker & Docker Compose

1. **Build and Launch Container**:
   ```bash
   docker-compose up --build
   ```
2. Access dashboard at `http://localhost:8501`.

---

## ⚠️ Mandatory Ethical & Analytical Disclaimer

> **"This prediction is based solely on historical data patterns and should not be interpreted as a forecast of future real-world events."**
