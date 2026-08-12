import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config import setup_page_config
from utils.ui_components import load_illicit_data, render_global_sidebar_filters
from utils.forecasting import forecast_incidents

setup_page_config("Forecasting Trends")

st.title("📈 Temporal Threat Forecasting")

df = load_illicit_data()
filtered_df = render_global_sidebar_filters(df)

st.sidebar.markdown("---")
st.sidebar.subheader("🔮 Forecast Configuration")
forecast_months = st.sidebar.slider("Forecast Horizon (Months)", min_value=3, max_value=24, value=12)

selected_region = st.session_state.get('selected_region', 'All')
selected_crime = st.session_state.get('selected_crime_type', 'All')

st.info(f"**Forecasting Engine**: SARIMA (`statsmodels`). Filtering: Region = `{selected_region}`, Crime Type = `{selected_crime}`.")

with st.spinner("Calculating time-series forecast and confidence bounds..."):
    res_df, val_metrics, model_name = forecast_incidents(
        df, 
        region=selected_region if selected_region != 'All' else None, 
        crime_type=selected_crime if selected_crime != 'All' else None, 
        steps=forecast_months
    )
    
if res_df.empty:
    st.warning("Insufficient data to fit time-series forecast.")
else:
    # Display Validation Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Validation Window", value=f"{val_metrics['val_steps']} Months")
    with col2:
        st.metric(label="Validation MAE", value=f"{val_metrics['val_mae']}")
    with col3:
        st.metric(label="Validation RMSE", value=f"{val_metrics['val_rmse']}")
        
    st.markdown("---")
    
    # Plotly Line Chart with Confidence Interval Shading (Light Theme)
    fig = go.Figure()
    
    # Historical Actuals
    hist_mask = ~res_df['is_forecast']
    fig.add_trace(go.Scatter(
        x=res_df[hist_mask]['ds'],
        y=res_df[hist_mask]['y'],
        mode='lines',
        name='Historical Incidents',
        line=dict(color='#1D4ED8', width=2)
    ))
    
    # Forecast line
    fore_mask = res_df['is_forecast']
    fig.add_trace(go.Scatter(
        x=res_df[fore_mask]['ds'],
        y=res_df[fore_mask]['yhat'],
        mode='lines+markers',
        name='Forecasted Projection',
        line=dict(color='#D97706', width=2.5, dash='dash')
    ))
    
    # Upper & Lower Confidence Interval
    fig.add_trace(go.Scatter(
        x=res_df[fore_mask]['ds'],
        y=res_df[fore_mask]['yhat_upper'],
        mode='lines',
        name='Upper 80% Confidence Bound',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=res_df[fore_mask]['ds'],
        y=res_df[fore_mask]['yhat_lower'],
        mode='lines',
        name='80% Confidence Interval',
        fill='tonexty',
        fillcolor='rgba(217, 119, 6, 0.15)',
        line=dict(width=0)
    ))
    
    fig.update_layout(
        title=f"Monthly Security Incident Volume Projection ({model_name})",
        xaxis_title="Timeline Date",
        yaxis_title="Monthly Incident Count",
        template="plotly_white",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=550
    )
    
    st.plotly_chart(fig, width='stretch')
