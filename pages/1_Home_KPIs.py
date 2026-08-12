import streamlit as st
import pandas as pd
import plotly.express as px
from config import setup_page_config
from utils.ui_components import load_illicit_data, render_global_sidebar_filters

setup_page_config("Home KPIs")

st.title("📊 Global Threat KPIs & Summary")

df = load_illicit_data()
filtered_df = render_global_sidebar_filters(df)

if filtered_df.empty:
    st.warning("No data matching selected filters.")
else:
    # Key Metrics
    total_incidents = len(filtered_df)
    
    # Exclude ASAM from total fatalities aggregate since ASAM fatalities are null
    fatalities_series = filtered_df[filtered_df['source_dataset'] != 'ASAM']['fatalities'].dropna()
    total_fatalities = int(fatalities_series.sum())
    
    active_actors = filtered_df['actor_group'].nunique()
    
    min_date = filtered_df['event_date'].min().strftime('%Y-%m-%d') if not filtered_df['event_date'].empty else 'N/A'
    max_date = filtered_df['event_date'].max().strftime('%Y-%m-%d') if not filtered_df['event_date'].empty else 'N/A'
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Recorded Incidents", value=f"{total_incidents:,}")
    with col2:
        st.metric(label="Total Fatalities (Excludes ASAM)", value=f"{total_fatalities:,}")
    with col3:
        st.metric(label="Active Actor Groups", value=f"{active_actors:,}")
    with col4:
        st.metric(label="Date Range Covered", value=f"{min_date} to {max_date}")
        
    st.markdown("---")
    
    # Visualizations
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Threat Breakdown by Crime Type")
        crime_counts = filtered_df['crime_type'].value_counts().reset_index()
        crime_counts.columns = ['Crime Type', 'Incidents']
        fig_crime = px.bar(
            crime_counts, 
            x='Incidents', 
            y='Crime Type', 
            orientation='h',
            color='Crime Type',
            color_discrete_sequence=px.colors.qualitative.Bold,
            template='plotly_white'
        )
        fig_crime.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_crime, width='stretch')
        
    with col_right:
        st.subheader("Data Distribution by Source Dataset")
        source_counts = filtered_df['source_dataset'].value_counts().reset_index()
        source_counts.columns = ['Source Dataset', 'Incidents']
        fig_source = px.pie(
            source_counts, 
            names='Source Dataset', 
            values='Incidents', 
            hole=0.4,
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_source.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_source, width='stretch')
