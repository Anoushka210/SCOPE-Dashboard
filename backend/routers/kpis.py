import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd
from state import app_state

router = APIRouter(prefix="/api", tags=["kpis"])

# Load precomputed full dataset summary if available
FULL_SUMMARY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "full_kpi_summary.json"
PRECOMPUTED_FULL = {}
if FULL_SUMMARY_PATH.exists():
    try:
        with open(FULL_SUMMARY_PATH, "r") as f:
            PRECOMPUTED_FULL = json.load(f)
    except Exception as e:
        print(f"Warning: could not load full_kpi_summary.json: {e}")

NON_VIOLENT_CRIMES = {"Protests", "Strategic developments"}

@router.get("/kpis")
def get_kpis(
    region: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    severity_min: Optional[int] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None),
    include_non_violent: bool = Query(False, description="Whether to include Protests and Strategic developments in crime counts (defaults to False)")
):
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")
    
    df = app_state.df
    filtered = df

    if region and region != "All":
        filtered = filtered[filtered['region'] == region]
    if crime_type and crime_type != "All":
        filtered = filtered[filtered['crime_type'] == crime_type]
    if severity_min is not None and severity_min > 0:
        # Minimum severity class threshold (0: Low, 1: Med, 2: High, 3: Crit)
        # Class 1: > 2.0, Class 2: > 5.0, Class 3: > 15.0
        threshold_map = {1: 2.0, 2: 5.0, 3: 15.0}
        min_score = threshold_map.get(severity_min, float(severity_min))
        filtered = filtered[filtered['severity_score'] >= min_score]

    if date_start:
        start_dt = pd.to_datetime(date_start, errors='coerce')
        if pd.notna(start_dt):
            filtered = filtered[filtered['event_date_dt'] >= start_dt]
    if date_end:
        end_dt = pd.to_datetime(date_end, errors='coerce')
        if pd.notna(end_dt):
            filtered = filtered[filtered['event_date_dt'] <= end_dt]

    total_incidents = int(len(filtered))

    # Calculate expanded event count by evaluating ACLED EVENTS multiplier
    acled_mask = filtered['source_dataset'] == 'ACLED'
    if acled_mask.sum() > 0:
        acled_derived_events = (filtered.loc[acled_mask, 'severity_score'] - (filtered.loc[acled_mask, 'fatalities'].fillna(0) * 3)).clip(lower=1.0)
        total_events_expanded = int(acled_derived_events.sum() + (~acled_mask).sum())
    else:
        total_events_expanded = total_incidents

    # Exclude ASAM from fatalities aggregate per project rules
    fatalities_subset = filtered[filtered['source_dataset'] != 'ASAM']['fatalities'].dropna()
    total_fatalities = int(fatalities_subset.sum()) if not fatalities_subset.empty else 0

    # Count real actor groups (exclude ACLED disorder types and unknowns)
    real_actors_subset = filtered[
        filtered['source_dataset'].isin(['GTD', 'Cartel']) & 
        ~filtered['actor_group'].isin(['Unknown', 'Unknown Group', 'Unspecified', 'Armed Group/Civilian Disorder'])
    ]['actor_group'].dropna()
    active_actor_groups = int(real_actors_subset.nunique()) if not real_actors_subset.empty else int(filtered['actor_group'].dropna().nunique())

    valid_dates = filtered['event_date_dt'].dropna()
    date_range_min = valid_dates.min().strftime('%Y-%m-%d') if not valid_dates.empty else "N/A"
    date_range_max = valid_dates.max().strftime('%Y-%m-%d') if not valid_dates.empty else "N/A"

    # Crime breakdown: filter out non-violent categories if include_non_violent is False
    all_crime_counts = filtered['crime_type'].value_counts()
    if not include_non_violent:
        crime_counts_display = all_crime_counts[~all_crime_counts.index.isin(NON_VIOLENT_CRIMES)]
    else:
        crime_counts_display = all_crime_counts

    incidents_by_crime_type = {str(k): int(v) for k, v in crime_counts_display.items()}
    incidents_by_region = {str(k): int(v) for k, v in filtered['region'].value_counts().items()}

    return {
        "sample_scope": "150k Stratified Deployed Dataset",
        "total_incidents": total_incidents,
        "total_events_expanded": total_events_expanded,
        "total_fatalities": total_fatalities,
        "active_actor_groups": active_actor_groups,
        "date_range_min": date_range_min,
        "date_range_max": date_range_max,
        "include_non_violent": include_non_violent,
        "incidents_by_crime_type": incidents_by_crime_type,
        "incidents_by_region": incidents_by_region,
        "full_database_summary": PRECOMPUTED_FULL
    }
