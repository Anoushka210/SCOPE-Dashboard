import pandas as pd
import numpy as np

def generate_threat_narrative(df, region=None, date_range=None):
    """
    Rule-based narrative synthesis engine (no external LLM calls).
    Computes key metrics and constructs standard intelligence briefing text.
    """
    filtered = df.copy()
    if region and region != 'All':
        filtered = filtered[filtered['region'] == region]
        
    filtered['event_date'] = pd.to_datetime(filtered['event_date'], errors='coerce')
    filtered = filtered.dropna(subset=['event_date'])
    
    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered['event_date'] >= start_date) & (filtered['event_date'] <= end_date)]
        
    total_incidents = len(filtered)
    if total_incidents == 0:
        return "No incident data recorded for the selected region and date range."
        
    total_fatalities = int(filtered['fatalities'].fillna(0).sum())
    top_crime = filtered['crime_type'].mode()[0] if not filtered['crime_type'].empty else 'Unspecified'
    top_crime_count = (filtered['crime_type'] == top_crime).sum()
    top_crime_pct = round((top_crime_count / total_incidents) * 100, 1)
    
    top_country = filtered['country'].mode()[0] if not filtered['country'].empty else 'Unspecified Country'
    top_country_count = (filtered['country'] == top_country).sum()
    
    # Calculate trend comparing first half to second half of period
    filtered_sorted = filtered.sort_values('event_date')
    mid_point = len(filtered_sorted) // 2
    first_half = filtered_sorted.iloc[:mid_point]
    second_half = filtered_sorted.iloc[mid_point:]
    
    count_h1 = len(first_half)
    count_h2 = len(second_half)
    
    if count_h1 > 0:
        pct_change = round(((count_h2 - count_h1) / count_h1) * 100, 1)
        trend_str = f"increased by {pct_change}%" if pct_change > 0 else f"decreased by {abs(pct_change)}%" if pct_change < 0 else "remained stable"
    else:
        trend_str = "experienced significant data influx"
        
    fatalities_h1 = first_half['fatalities'].fillna(0).sum()
    fatalities_h2 = second_half['fatalities'].fillna(0).sum()
    fatality_trend = "upward" if fatalities_h2 > fatalities_h1 else "downward" if fatalities_h2 < fatalities_h1 else "stable"
    
    region_name = region if region and region != 'All' else 'Global Regions'
    
    narrative = (
        f"Executive Strategic Intelligence Briefing: During the evaluated operational timeframe, "
        f"incidents across {region_name} {trend_str}. A total of {total_incidents:,} security events "
        f"and {total_fatalities:,} reported fatalities were recorded.\n\n"
        f"Primary Threat Drivers: Operational activity was predominantly driven by {top_crime}, accounting "
        f"for {top_crime_pct}% of total incidents. The primary geographical focal point for activity was "
        f"{top_country}, registering {top_country_count:,} incidents.\n\n"
        f"Fatality & Risk Velocity: Fatality trends demonstrated a overall {fatality_trend} trajectory "
        f"over the monitoring window. High-severity tactical events remain concentrated in contested transit corridors and urban nodes."
    )
    
    return narrative
