from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional, List, Dict, Any
import numpy as np
import pandas as pd
from state import app_state

router = APIRouter(prefix="/api", tags=["map-data"])

@router.get("/map-data")
def get_map_data(
    response: Response,
    region: Optional[str] = Query(None),
    crime_type: Optional[str] = Query(None),
    severity_min: Optional[int] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None)
):
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")
    
    df = app_state.df
    filtered = df.dropna(subset=['latitude', 'longitude']).copy()

    if region and region != "All":
        filtered = filtered[filtered['region'] == region]
    if crime_type and crime_type != "All":
        filtered = filtered[filtered['crime_type'] == crime_type]
    if severity_min is not None and severity_min > 0:
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

    total_count = len(filtered)
    is_capped = total_count > 1000

    if is_capped:
        weights = filtered['severity_score'].fillna(1.0).astype(float).values
        weights = np.maximum(weights, 0.1)
        prob = weights / weights.sum()
        sample_indices = np.random.choice(filtered.index, size=1000, replace=False, p=prob)
        sample_df = filtered.loc[sample_indices]
    else:
        sample_df = filtered

    points = []
    for _, row in sample_df.iterrows():
        sub_type = str(row['sub_type']) if pd.notna(row.get('sub_type')) else 'Security Incident'
        actor = str(row['actor_group']) if pd.notna(row.get('actor_group')) else 'Unknown'
        country = str(row['country']) if pd.notna(row.get('country')) else 'Unknown'
        date_str = str(row['event_date']) if pd.notna(row.get('event_date')) else ''
        
        # Explicitly marked as a templated synthetic summary, not source narrative
        desc = (
            str(row['description'])
            if 'description' in row and pd.notna(row['description'])
            else f"Summary: {sub_type} event recorded in {country} involving '{actor}'."
        )

        points.append({
            "lat": float(row['latitude']),
            "lon": float(row['longitude']),
            "crime_type": str(row['crime_type']),
            "severity_score": float(row['severity_score']) if pd.notna(row['severity_score']) else 1.0,
            "actor_group": actor,
            "country": country,
            "date": date_str,
            "description": desc
        })

    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Is-Capped"] = "true" if is_capped else "false"
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count, X-Is-Capped"

    return points
