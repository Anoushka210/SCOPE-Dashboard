from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import numpy as np
import shap
from state import app_state
from utils.feature_engineering import encode_single_input

router = APIRouter(prefix="/api", tags=["predict"])

class PredictRequest(BaseModel):
    region: str = Field(..., example="Western Africa")
    crime_type: str = Field(..., example="Battles")
    sub_type: Optional[str] = Field("Armed clash", example="Armed clash")
    country: Optional[str] = Field("Nigeria", example="Nigeria")
    year: Optional[int] = Field(2026, example=2026)
    month: Optional[int] = Field(6, example=6)
    actor_group: Optional[str] = Field("Unknown Group", example="Unknown Group")
    latitude: Optional[float] = Field(0.0, example=0.0)
    longitude: Optional[float] = Field(0.0, example=0.0)

CLASS_LABELS = {
    0: "Low (Score <= 2)",
    1: "Medium (Score 2-5)",
    2: "High (Score 5-15)",
    3: "Critical (Score > 15)"
}

CLASS_NAMES = ["Low", "Medium", "High", "Critical"]

def execute_prediction(req: PredictRequest) -> Dict[str, Any]:
    if app_state.model is None or app_state.encoders is None:
        raise HTTPException(status_code=503, detail="Prediction model or encoders not loaded")

    month_int = max(1, min(12, int(req.month or 6)))
    year_int = int(req.year or 2026)
    date_str = f"{year_int}-{month_int:02d}-15"

    input_payload = {
        'crime_type': req.crime_type,
        'sub_type': req.sub_type or 'Unspecified',
        'region': req.region,
        'country': req.country or 'Unknown',
        'actor_group': req.actor_group or 'Unknown Group',
        'latitude': float(req.latitude or 0.0),
        'longitude': float(req.longitude or 0.0),
        'event_date': date_str,
        'year': year_int,
        'month': month_int
    }

    try:
        X_input = encode_single_input(input_payload)
        pred_class = int(app_state.model.predict(X_input)[0])
        probs = [float(p) for p in app_state.model.predict_proba(X_input)[0]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # Compute SHAP explanation without target leakage
    try:
        explainer = shap.TreeExplainer(app_state.model)
        shap_val_sample = explainer.shap_values(X_input)

        if isinstance(shap_val_sample, list):
            vals = shap_val_sample[pred_class][0]
        elif len(np.shape(shap_val_sample)) == 3:
            vals = shap_val_sample[0, :, pred_class]
        else:
            vals = shap_val_sample[0]

        top_indices = np.argsort(np.abs(vals))[-10:][::-1]
        shap_dict = {str(X_input.columns[i]): round(float(vals[i]), 4) for i in top_indices}
        shap_list = [
            {"feature": str(X_input.columns[i]), "impact": round(float(vals[i]), 4)}
            for i in top_indices
        ]
    except Exception as e:
        shap_dict = {}
        shap_list = []

    prob_breakdown = [
        {
            "class_index": i,
            "class_name": CLASS_NAMES[i],
            "class_label": CLASS_LABELS.get(i, f"Class {i}"),
            "probability": round(probs[i], 4)
        }
        for i in range(len(probs))
    ]

    return {
        "predicted_class": pred_class,
        "class_label": CLASS_LABELS.get(pred_class, f"Class {pred_class}"),
        "class_probabilities": probs,
        "probabilities_breakdown": prob_breakdown,
        "shap_values": shap_dict,
        "shap_features": shap_list
    }

@router.post("/predict")
def predict_threat_post(payload: PredictRequest):
    return execute_prediction(payload)

@router.get("/predict")
def predict_threat_get(
    region: str = Query("Western Africa"),
    crime_type: str = Query("Battles"),
    sub_type: Optional[str] = Query("Armed clash"),
    country: Optional[str] = Query("Nigeria"),
    year: Optional[int] = Query(2026),
    month: Optional[int] = Query(6),
    actor_group: Optional[str] = Query("Unknown Group"),
    latitude: Optional[float] = Query(0.0),
    longitude: Optional[float] = Query(0.0)
):
    req = PredictRequest(
        region=region,
        crime_type=crime_type,
        sub_type=sub_type,
        country=country,
        year=year,
        month=month,
        actor_group=actor_group,
        latitude=latitude,
        longitude=longitude
    )
    return execute_prediction(req)
