from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import pandas as pd
from state import app_state
from utils.forecasting import forecast_incidents

router = APIRouter(prefix="/api", tags=["forecast"])

@router.get("/forecast")
def get_forecast(
    region: Optional[str] = Query("Western Africa"),
    crime_type: Optional[str] = Query("Battles"),
    steps: Optional[int] = Query(12)
):
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")

    df = app_state.df
    try:
        combined_df, val_metrics, model_used = forecast_incidents(
            df,
            region=region,
            crime_type=crime_type,
            steps=steps or 12,
            val_steps=6
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecasting calculation failed: {str(e)}")

    dates: List[str] = []
    actual: List[Optional[float]] = []
    forecast: List[float] = []
    lower_ci: List[float] = []
    upper_ci: List[float] = []
    is_forecast_list: List[bool] = []

    for _, row in combined_df.iterrows():
        dt_val = row['ds']
        dates.append(dt_val.strftime('%Y-%m-%d') if hasattr(dt_val, 'strftime') else str(dt_val))
        
        y_val = row.get('y')
        actual.append(round(float(y_val), 2) if pd.notna(y_val) else None)
        
        forecast.append(round(float(row['yhat']), 2) if pd.notna(row['yhat']) else 0.0)
        lower_ci.append(round(float(row['yhat_lower']), 2) if pd.notna(row['yhat_lower']) else 0.0)
        upper_ci.append(round(float(row['yhat_upper']), 2) if pd.notna(row['yhat_upper']) else 0.0)
        is_forecast_list.append(bool(row.get('is_forecast', False)))

    return {
        "dates": dates,
        "actual": actual,
        "forecast": forecast,
        "lower_ci": lower_ci,
        "upper_ci": upper_ci,
        "is_forecast": is_forecast_list,
        "validation_metrics": val_metrics,
        "model_used": model_used
    }

