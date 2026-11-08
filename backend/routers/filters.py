from fastapi import APIRouter, HTTPException
from state import app_state

router = APIRouter(prefix="/api", tags=["filters"])

@router.get("/filters")
def get_filters():
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")
    
    df = app_state.df
    regions = sorted([r for r in df['region'].dropna().unique().tolist() if str(r).strip()])
    crime_types = sorted([c for c in df['crime_type'].dropna().unique().tolist() if str(c).strip()])
    
    valid_dates = df['event_date_dt'].dropna()
    date_min = valid_dates.min().strftime('%Y-%m-%d') if not valid_dates.empty else "2020-01-01"
    date_max = valid_dates.max().strftime('%Y-%m-%d') if not valid_dates.empty else "2026-06-30"

    countries = sorted([c for c in df['country'].dropna().unique().tolist() if str(c).strip()])
    sub_types = sorted([s for s in df['sub_type'].dropna().unique().tolist() if str(s).strip()])
    actor_groups = sorted([a for a in df['actor_group'].dropna().unique().tolist() if str(a).strip() and str(a) != 'Unknown'])[:100]

    return {
        "regions": regions,
        "crime_types": crime_types,
        "date_min": date_min,
        "date_max": date_max,
        "countries": countries,
        "sub_types": sub_types,
        "actor_groups": actor_groups
    }

