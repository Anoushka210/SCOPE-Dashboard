import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from config import setup_page_config
from utils.ui_components import load_illicit_data, render_global_sidebar_filters
from utils.ai_summary import generate_threat_narrative
from utils.pdf_generator import create_pdf_briefing

setup_page_config("Automated Briefings")

st.title("📄 Automated Strategic Intelligence Briefings")

df = load_illicit_data()
filtered_df = render_global_sidebar_filters(df)

selected_region = st.session_state.get('selected_region', 'All')
selected_dates = st.session_state.get('selected_date_range', None)

st.subheader("Generate & Export Executive Threat Assessment")

if filtered_df.empty:
    st.warning("No data matching current filter selection.")
else:
    narrative = generate_threat_narrative(filtered_df, region=selected_region, date_range=selected_dates)
    
    total_incidents = len(filtered_df)
    fatalities_series = filtered_df[filtered_df['source_dataset'] != 'ASAM']['fatalities'].dropna()
    total_fatalities = int(fatalities_series.sum())
    primary_driver = filtered_df['crime_type'].mode()[0] if not filtered_df['crime_type'].empty else 'N/A'
    
    kpis = {
        'total_incidents': f"{total_incidents:,}",
        'total_fatalities': f"{total_fatalities:,} (Excludes ASAM)",
        'primary_driver': primary_driver,
        'region': selected_region
    }
    
    st.markdown("### Executive Briefing Preview")
    st.info(narrative)
    
    # Generate Chart Image for PDF report (Clean Light Theme)
    chart_temp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'temp_briefing_chart.png')
    
    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor='#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    filtered_df['crime_type'].value_counts().head(5).plot(kind='barh', ax=ax, color='#1D4ED8')
    ax.set_title(f"Top 5 Incident Categories ({selected_region})", fontsize=10, fontweight='bold', color='#0F172A')
    ax.set_xlabel("Incident Count", fontsize=9, color='#0F172A')
    ax.tick_params(colors='#0F172A')
    for spine in ax.spines.values():
        spine.set_color('#CBD5E1')
    plt.tight_layout()
    plt.savefig(chart_temp_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    
    pdf_bytes = create_pdf_briefing(narrative, kpis, chart_img_path=chart_temp_path)
    
    st.markdown("---")
    st.download_button(
        label="📥 Download Executive Intelligence Briefing (PDF)",
        data=pdf_bytes,
        file_name=f"SCOPE_Briefing_{selected_region.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
