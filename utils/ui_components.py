import os
import pickle
import pandas as pd
import streamlit as st
from config import render_sidebar_footer

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')

@st.cache_data(show_spinner="Loading illicit network dataset...")
def load_illicit_data():
    deploy_path = os.path.join(PROCESSED_DIR, 'illicit_networks_deployed.csv')
    full_path = os.path.join(PROCESSED_DIR, 'illicit_networks.csv')
    
    file_path = deploy_path if os.path.exists(deploy_path) else full_path
    
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}. Run data loader first.")
        return pd.DataFrame()
        
    df = pd.read_csv(file_path, low_memory=False)
    df['event_date'] = pd.to_datetime(df['event_date'], errors='coerce')
    return df

@st.cache_data(show_spinner="Loading human trafficking dataset...")
def load_trafficking_data():
    file_path = os.path.join(PROCESSED_DIR, 'trafficking_cases.csv')
    if not os.path.exists(file_path):
        st.error(f"File not found: {file_path}. Run data loader first.")
        return pd.DataFrame()
    return pd.read_csv(file_path, low_memory=False)

@st.cache_resource(show_spinner="Loading threat prediction model...")
def load_trained_model():
    model_path = os.path.join(MODELS_DIR, 'incident_prediction.pkl')
    encoder_path = os.path.join(MODELS_DIR, 'feature_encoders.pkl')
    
    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        return None, None
        
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(encoder_path, 'rb') as f:
        encoders = pickle.load(f)
        
    return model, encoders

def render_global_sidebar_filters(df):
    """
    Renders standardized sidebar filters for Region, Date Range, and Crime Type.
    Persists selections in st.session_state.
    Returns filtered dataframe.
    """
    st.sidebar.title("🎛️ Global Filters")
    
    available_regions = ['All'] + sorted(df['region'].dropna().unique().tolist())
    if 'selected_region' not in st.session_state:
        st.session_state.selected_region = 'All'
        
    region_idx = available_regions.index(st.session_state.selected_region) if st.session_state.selected_region in available_regions else 0
    selected_region = st.sidebar.selectbox(
        "Global Region",
        options=available_regions,
        index=region_idx,
        key='sidebar_region_select'
    )
    st.session_state.selected_region = selected_region
    
    available_crimes = ['All'] + sorted(df['crime_type'].dropna().unique().tolist())
    if 'selected_crime_type' not in st.session_state:
        st.session_state.selected_crime_type = 'All'
        
    crime_idx = available_crimes.index(st.session_state.selected_crime_type) if st.session_state.selected_crime_type in available_crimes else 0
    selected_crime = st.sidebar.selectbox(
        "Crime / Threat Type",
        options=available_crimes,
        index=crime_idx,
        key='sidebar_crime_select'
    )
    st.session_state.selected_crime_type = selected_crime
    
    min_date = df['event_date'].min().date() if not df['event_date'].empty else pd.to_datetime('2020-01-01').date()
    max_date = df['event_date'].max().date() if not df['event_date'].empty else pd.to_datetime('2026-06-30').date()
    
    if 'selected_date_range' not in st.session_state:
        st.session_state.selected_date_range = (min_date, max_date)
        
    default_dates = st.session_state.selected_date_range
    selected_dates = st.sidebar.date_input(
        "Observation Window",
        value=default_dates,
        min_value=min_date,
        max_value=max_date,
        key='sidebar_date_select'
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        st.session_state.selected_date_range = selected_dates
    
    render_sidebar_footer()
    
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
        
    if selected_crime != 'All':
        filtered_df = filtered_df[filtered_df['crime_type'] == selected_crime]
        
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_d, end_d = pd.to_datetime(selected_dates[0]), pd.to_datetime(selected_dates[1])
        filtered_df = filtered_df[(filtered_df['event_date'] >= start_d) & (filtered_df['event_date'] <= end_d)]
        
    return filtered_df
