import os
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import shap

from config import setup_page_config
from utils.ui_components import load_illicit_data, load_trained_model, render_global_sidebar_filters
from utils.feature_engineering import encode_single_input

setup_page_config("Predictive Modeling")

st.title("🤖 Predictive Threat Severity Modeling")

model, encoders = load_trained_model()
metrics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'metrics.json')
shap_img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'shap_summary.png')

tab1, tab2 = st.tabs(["🔮 Real-Time Incident Severity Prediction", "📈 Model Performance & SHAP Evaluation"])

with tab1:
    st.subheader("Predict Incident Threat Severity Class")
    st.write("Input incident operational characteristics below to evaluate the predicted threat severity class using our trained LightGBM machine learning model.")
    
    if model is None or encoders is None:
        st.error("Model or feature encoders not found in `models/`. Ensure `train_threat_model.py` has executed.")
    else:
        df = load_illicit_data()
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            regions = sorted(df['region'].dropna().unique().tolist())
            input_region = st.selectbox("Region", options=regions)
            
            countries = sorted(df[df['region'] == input_region]['country'].dropna().unique().tolist())
            input_country = st.selectbox("Country", options=countries if countries else ['Unknown'])
            
        with col_b:
            crimes = sorted(df['crime_type'].dropna().unique().tolist())
            input_crime = st.selectbox("Crime Type", options=crimes)
            
            sub_types = sorted(df[df['crime_type'] == input_crime]['sub_type'].dropna().unique().tolist())
            input_subtype = st.selectbox("Sub-Event Type", options=sub_types if sub_types else ['Unspecified'])
            
        with col_c:
            actors = sorted(df['actor_group'].dropna().unique().tolist())
            input_actor = st.selectbox("Actor Group", options=actors[:50] if actors else ['Unknown Group'])
            
            input_fatalities = st.number_input("Reported Fatalities", min_value=0, max_value=500, value=0)
            
        col_d, col_e, col_f = st.columns(3)
        with col_d:
            input_lat = st.number_input("Latitude", value=0.0, format="%.4f")
        with col_e:
            input_lon = st.number_input("Longitude", value=0.0, format="%.4f")
        with col_f:
            input_date = st.date_input("Event Date", value=pd.to_datetime('2026-01-01'))
            
        if st.button("⚡ Run Threat Severity Prediction"):
            input_payload = {
                'crime_type': input_crime,
                'sub_type': input_subtype,
                'region': input_region,
                'country': input_country,
                'actor_group': input_actor,
                'latitude': input_lat,
                'longitude': input_lon,
                'fatalities': input_fatalities,
                'event_date': str(input_date)
            }
            
            X_input = encode_single_input(input_payload)
            pred_class = model.predict(X_input)[0]
            pred_probs = model.predict_proba(X_input)[0]
            
            class_labels = {0: "Low (Score <= 2)", 1: "Medium (Score 2-5)", 2: "High (Score 5-15)", 3: "Critical (Score > 15)"}
            class_colors = {0: "#16A34A", 1: "#D97706", 2: "#EA580C", 3: "#DC2626"}
            
            st.markdown("---")
            st.markdown(f"### Predicted Threat Severity Class: <span style='color:{class_colors[pred_class]}; font-weight:bold;'>{class_labels[pred_class]}</span>", unsafe_allow_html=True)
            
            # Probability breakdown
            prob_df = pd.DataFrame({
                'Class': [class_labels[i] for i in range(len(pred_probs))],
                'Probability': pred_probs
            })
            fig_prob = px.bar(
                prob_df, 
                x='Class', 
                y='Probability', 
                color='Class', 
                color_discrete_map={class_labels[i]: class_colors[i] for i in range(4)}, 
                title="Prediction Class Probability Distribution",
                template="plotly_white"
            )
            fig_prob.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_prob, width='stretch')
            
            # Specific SHAP explanation
            st.markdown("#### 🔍 SHAP Explanation for this Specific Prediction")
            try:
                explainer = shap.TreeExplainer(model)
                shap_val_sample = explainer.shap_values(X_input)
                
                if isinstance(shap_val_sample, list):
                    vals = shap_val_sample[pred_class][0]
                elif len(np.shape(shap_val_sample)) == 3:
                    vals = shap_val_sample[0, :, pred_class]
                else:
                    vals = shap_val_sample[0]
                    
                top_idx = np.argsort(np.abs(vals))[-10:]
                shap_df = pd.DataFrame({
                    'Feature': X_input.columns[top_idx],
                    'SHAP Impact': vals[top_idx]
                })
                
                fig_shap = px.bar(
                    shap_df, 
                    x='SHAP Impact', 
                    y='Feature', 
                    orientation='h', 
                    title=f"Top Feature Impacts driving Prediction towards Class '{class_labels[pred_class]}'",
                    template="plotly_white"
                )
                fig_shap.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_shap, width='stretch')
            except Exception as e:
                st.warning(f"Could not compute single-prediction SHAP plot: {e}")

with tab2:
    st.subheader("Model Evaluation Metrics & Global Feature Importance")
    
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics_data = json.load(f)
            
        winning_name = metrics_data.get('winning_model', 'LightGBM')
        st.success(f"🏆 Winning Model Selected by Macro F1: **{winning_name}**")
        
        # Display Comparative Metric Table
        records = []
        for name, m in metrics_data.get('models', {}).items():
            records.append({
                'Model': name,
                'Accuracy': f"{m['accuracy']:.4f}",
                'Macro F1': f"{m['macro_f1']:.4f}",
                'F1 Low': f"{m['per_class_f1'][0]:.4f}",
                'F1 Medium': f"{m['per_class_f1'][1]:.4f}",
                'F1 High': f"{m['per_class_f1'][2]:.4f}",
                'F1 Critical': f"{m['per_class_f1'][3]:.4f}"
            })
        st.table(pd.DataFrame(records))
    else:
        st.info("Metrics data not found. Run `train_threat_model.py` to populate training metrics.")
        
    st.markdown("---")
    st.subheader("Global Model SHAP Summary Plot")
    if os.path.exists(shap_img_path):
        st.image(shap_img_path, caption="Global SHAP Summary Plot for Winning Model", width='stretch')
    else:
        st.info("Global SHAP summary plot not found.")
