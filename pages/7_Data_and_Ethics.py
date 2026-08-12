import os
import streamlit as st
from config import setup_page_config, render_sidebar_footer, DISCLAIMER_TEXT

setup_page_config("Data & Ethics")

st.title("⚖️ Data Governance, Methodology & Ethical Framing")

st.markdown(
    "### 🚨 Mandated Ethical Disclaimer\n\n"
    f"> **\"{DISCLAIMER_TEXT}\"**\n\n"
    "---"
)

st.markdown(r"""
### 📚 Data Sources & Attribution

1. **ACLED (Armed Conflict Location & Event Data Project)**
   - *Scope*: Global coverage of political violence, demonstrations, and strategic developments.
   - *Aggregated Dataset Window*: 1996 - 2026.
   
2. **GTD (Global Terrorism Database)**
   - *Scope*: Open-source database including information on domestic and international terrorist events.
   - *Dataset Window*: 1970 - 2020.
   
3. **ASAM (Anti-Shipping Activity Messages - NGA)**
   - *Scope*: Maritime piracy, hostage-taking, and vessel attack incidents worldwide.
   - *Dataset Window*: 1978 - 2024.
   
4. **Mexico Cartel Incident Tracker & Admin Boundaries**
   - *Scope*: Sub-national cartel events and municipal boundary centroids.
   
5. **CTDC (Counter Trafficking Data Collaborative)**
   - *Scope*: Human trafficking victim demographics and exploitation modalities.

---

### ⚠️ Known Data Limitations & Biases

- **CTDC Synthetic Data**: The CTDC human trafficking dataset consists of **synthetically generated records** derived from statistical anonymization algorithms, *not* direct individual victim case records.
- **Reporting Bias**: Conflict and piracy data suffer from regional reporting disparities. Active combat zones or authoritarian regimes may underreport civilian casualties or censor security events.
- **ASAM Fatality Nulls & Hostility Score**: ASAM maritime reports focus on vessel boarding and piracy hostility types and do not explicitly capture fatality counts (100% null/NaN). **ASAM severity is derived from `hostilitytype_l` categorical severity weights, not casualty counts.** ASAM rows are explicitly excluded from total fatality sum calculations across the platform.
- **Cartel Centroid Approximations**: Exact latitude/longitude coordinates are absent in cartel reports; coordinates are mapped to state/municipality administrative centroids.

---

### 📐 Severity Score Rationale & Formula

To establish a unified ML target across multi-source security incidents, a continuous `severity_score` is computed based on operational impact and casualty weight:

$$\text{Severity Score} = (\text{Fatalities} \times 3.0) + (\text{Wounded/Events} \times 1.0) + \text{Baseline Weight}$$

The continuous score is bucketed into 4 threat classes for balanced ML classification:
- **Low Severity (Class 0)**: Score $\le 2.0$ (Low operational disruption, 0 fatalities)
- **Medium Severity (Class 1)**: $2.0 < \text{Score} \le 5.0$ (Moderate violence / property crime)
- **High Severity (Class 2)**: $5.0 < \text{Score} \le 15.0$ (Significant armed confrontation / multiple casualties)
- **Critical Severity (Class 3)**: $\text{Score} > 15.0$ (Mass violence, severe casualties, major terrorist attacks)

---

### 🤖 Machine Learning Model Strengths & Class Weaknesses

- **Overall Macro F1**: LightGBM achieved **0.7170 Macro F1** and **76.96% Accuracy** across all 4 severity classes.
- **Low & Critical Classes**: High F1 scores (**Low: 0.8558, Critical: 0.8575**). Critical-class events feature high recall due to distinct fatality and mass-violence indicators.
- **Medium & High Classes**: Lower F1 scores (**Medium: 0.5397, High: 0.6151**) due to boundary overlap between low-fatality combat clashes and moderate disruption events.
""")

report_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'quality_report.md')
if os.path.exists(report_path):
    with st.expander("🔍 View Complete Data Quality Lock-in Report"):
        with open(report_path, 'r') as f:
            st.markdown(f.read())

render_sidebar_footer()
