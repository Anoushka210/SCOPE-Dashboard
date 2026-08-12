import streamlit as st
from config import setup_page_config, render_sidebar_footer, DISCLAIMER_TEXT

setup_page_config("Home")

st.markdown("""
# 🛡️ SCOPE — Strategic Crime Observation & Prediction Engine

Welcome to **SCOPE**, an advanced multi-source intelligence platform designed for global crime pattern observation, network visualization, temporal forecasting, and predictive threat severity classification.

---

### 📌 Core Capabilities

1. **📊 Dynamic KPI Dashboards**: Real-time aggregation of multi-source global threat datasets (ACLED, GTD, ASAM, Cartel Violence).
2. **🌐 Interactive Global Threat Map**: Geospatial mapping of security incidents with multi-dimensional filtering.
3. **🤖 Machine Learning Threat Severity Prediction**: Machine-learning models (LightGBM, XGBoost, RandomForest) trained on over 1.18 million historical events to classify incident threat severity levels.
4. **📈 Temporal Trend Forecasting**: SARIMA time-series models generating incident volume projections with confidence bounds.
5. **🕸️ Actor Network Analysis**: Graph-theoretic network analysis quantifying degree and betweenness centrality of organized crime groups and conflict actors.
6. **📄 Automated Executive Briefings**: Rule-based intelligence synthesis engine producing downloadable PDF briefings.
7. **⚖️ Data Integrity & Ethical Framing**: Full transparency on synthetic datasets (CTDC), missingness, and analytical limitations.

---

### 🚀 Getting Started

Select a module from the **left sidebar navigation menu** to explore the dashboard pages.
""", unsafe_allow_html=True)

# Prominent Disclaimer Card on Home Page (Phase 8 Requirement)
st.info(f"⚠️ **ETHICAL DISCLAIMER**:\n\n{DISCLAIMER_TEXT}")

render_sidebar_footer()