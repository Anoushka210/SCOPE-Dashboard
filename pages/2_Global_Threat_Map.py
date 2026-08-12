import streamlit as st
import pandas as pd
import plotly.express as px
from config import setup_page_config
from utils.ui_components import load_illicit_data, render_global_sidebar_filters

setup_page_config("Global Threat Map")

st.title("🌐 Global Threat Map")

df = load_illicit_data()
filtered_df = render_global_sidebar_filters(df)

# Filter out missing coordinates
map_df = filtered_df.dropna(subset=['latitude', 'longitude']).copy()

st.sidebar.markdown("---")
st.sidebar.subheader("🗺️ Map Filters")

# Severity Class Filter
severity_options = ['All', 'Low (<=2)', 'Medium (2-5)', 'High (5-15)', 'Critical (>15)']
selected_severity = st.sidebar.selectbox("Severity Level", options=severity_options)

if selected_severity != 'All':
    if selected_severity == 'Low (<=2)':
        map_df = map_df[map_df['severity_score'] <= 2.0]
    elif selected_severity == 'Medium (2-5)':
        map_df = map_df[(map_df['severity_score'] > 2.0) & (map_df['severity_score'] <= 5.0)]
    elif selected_severity == 'High (5-15)':
        map_df = map_df[(map_df['severity_score'] > 5.0) & (map_df['severity_score'] <= 15.0)]
    elif selected_severity == 'Critical (>15)':
        map_df = map_df[map_df['severity_score'] > 15.0]

total_points = len(map_df)
MAX_MAP_POINTS = 1000

if total_points > MAX_MAP_POINTS:
    st.info(f"ℹ️ **Performance Note**: Filter returned **{total_points:,}** points. Displaying a random sample of **{MAX_MAP_POINTS}** points for optimal browser rendering performance.")
    display_map_df = map_df.sample(n=MAX_MAP_POINTS, random_state=42)
else:
    display_map_df = map_df

if display_map_df.empty:
    st.warning("No geospatial points available for the selected filter combination.")
else:
    # Use maplibre-based scatter_map replacement
    fig = px.scatter_map(
        display_map_df,
        lat="latitude",
        lon="longitude",
        color="crime_type",
        size="severity_score",
        size_max=15,
        zoom=1,
        hover_name="actor_group",
        hover_data={"country": True, "event_date": True, "fatalities": True, "severity_score": ":.1f"},
        map_style="open-street-map",
        height=650,
        template="plotly_white",
        title=f"Geospatial Security Incident Map (Showing {len(display_map_df):,} of {total_points:,} events)"
    )
    
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, width='stretch')
