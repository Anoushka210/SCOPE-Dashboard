from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import pandas as pd
from backend.state import app_state
from utils.ai_summary import generate_threat_narrative

router = APIRouter(prefix="/api", tags=["briefing"])

class BriefingRequest(BaseModel):
    region: Optional[str] = Field("Western Africa", example="Western Africa")
    crime_type: Optional[str] = Field(None, example="Battles")
    date_start: Optional[str] = Field(None, example="2020-01-01")
    date_end: Optional[str] = Field(None, example="2026-06-30")

def execute_briefing(region: Optional[str], crime_type: Optional[str], date_start: Optional[str], date_end: Optional[str]) -> Dict[str, Any]:
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")

    df = app_state.df
    filtered = df.copy()

    reg_val = None if (not region or region == "All") else region
    if reg_val:
        filtered = filtered[filtered['region'] == reg_val]

    if crime_type and crime_type != "All":
        filtered = filtered[filtered['crime_type'] == crime_type]

    date_range = None
    if date_start and date_end:
        date_range = [date_start, date_end]
        start_dt = pd.to_datetime(date_start, errors='coerce')
        end_dt = pd.to_datetime(date_end, errors='coerce')
        if pd.notna(start_dt) and pd.notna(end_dt):
            filtered = filtered[(filtered['event_date_dt'] >= start_dt) & (filtered['event_date_dt'] <= end_dt)]

    narrative = generate_threat_narrative(filtered, region=reg_val, date_range=date_range)

    total_incidents = len(filtered)
    fatalities_subset = filtered[filtered['source_dataset'] != 'ASAM']['fatalities'].dropna()
    total_fatalities = int(fatalities_subset.sum()) if not fatalities_subset.empty else 0
    primary_driver = str(filtered['crime_type'].mode()[0]) if not filtered['crime_type'].empty else 'N/A'

    kpi_summary = {
        "total_incidents": f"{total_incidents:,}",
        "total_fatalities": f"{total_fatalities:,} (Excludes ASAM)",
        "primary_driver": primary_driver,
        "region": reg_val or "Global"
    }

    return {
        "narrative_text": narrative,
        "kpi_summary": kpi_summary
    }

@router.post("/briefing")
def create_briefing_post(payload: BriefingRequest):
    return execute_briefing(payload.region, payload.crime_type, payload.date_start, payload.date_end)

@router.get("/briefing")
def create_briefing_get(
    region: Optional[str] = Query("Western Africa"),
    crime_type: Optional[str] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None)
):
    return execute_briefing(region, crime_type, date_start, date_end)

