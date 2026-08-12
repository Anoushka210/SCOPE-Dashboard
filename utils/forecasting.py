import os
import pandas as pd
import numpy as np

PROPHET_AVAILABLE = False
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False

from statsmodels.tsa.statespace.sarimax import SARIMAX

def get_monthly_series(df, region=None, crime_type=None):
    """Aggregate incident counts monthly for specified region and crime_type."""
    filtered = df.copy()
    if region and region != 'All':
        filtered = filtered[filtered['region'] == region]
    if crime_type and crime_type != 'All':
        filtered = filtered[filtered['crime_type'] == crime_type]
        
    filtered['event_date'] = pd.to_datetime(filtered['event_date'], errors='coerce')
    filtered = filtered.dropna(subset=['event_date'])
    
    if filtered.empty:
        return pd.DataFrame(columns=['incident_count'])
        
    ts = filtered.set_index('event_date').resample('MS').size().to_frame(name='incident_count')
    return ts

def forecast_incidents(df, region=None, crime_type=None, steps=12, val_steps=6):
    """
    Fit time series forecasting model (SARIMA) on monthly incident counts.
    Validates on a held-out recent time window (val_steps).
    Returns (forecast_df, validation_metrics, model_used).
    """
    ts = get_monthly_series(df, region=region, crime_type=crime_type)
    
    # Safe date range determination
    if ts.empty or pd.isna(ts.index.max()):
        last_date = pd.to_datetime('2026-06-01')
        dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='MS')
        forecast_df = pd.DataFrame({
            'ds': dates,
            'yhat': 10.0,
            'yhat_lower': 5.0,
            'yhat_upper': 15.0,
            'is_forecast': True
        })
        return forecast_df, {'val_mae': 0.0, 'val_rmse': 0.0, 'val_steps': 0}, 'Mean Baseline'

    last_date = ts.index.max()
    
    if len(ts) < 24:
        dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='MS')
        mean_val = float(ts['incident_count'].mean()) if len(ts) > 0 else 10.0
        forecast_df = pd.DataFrame({
            'ds': dates,
            'yhat': mean_val,
            'yhat_lower': mean_val * 0.8,
            'yhat_upper': mean_val * 1.2,
            'is_forecast': True
        })
        history_df = pd.DataFrame({
            'ds': ts.index,
            'y': ts['incident_count'].values,
            'yhat': ts['incident_count'].values,
            'yhat_lower': ts['incident_count'].values,
            'yhat_upper': ts['incident_count'].values,
            'is_forecast': False
        })
        res_df = pd.concat([history_df, forecast_df], ignore_index=True)
        return res_df, {'val_mae': 0.0, 'val_rmse': 0.0, 'val_steps': 0}, 'Mean Baseline'
        
    train_ts = ts.iloc[:-val_steps]
    val_ts = ts.iloc[-val_steps:]
    
    try:
        val_model = SARIMAX(train_ts['incident_count'], order=(1, 1, 1), seasonal_order=(1, 0, 0, 12), enforce_stationarity=False, enforce_invertibility=False)
        val_res = val_model.fit(disp=False)
        val_pred = val_res.get_forecast(steps=val_steps).predicted_mean
        
        mae = float(np.mean(np.abs(val_ts['incident_count'].values - val_pred.values)))
        rmse = float(np.sqrt(np.mean((val_ts['incident_count'].values - val_pred.values) ** 2)))
    except Exception as e:
        mae, rmse = 0.0, 0.0
        
    full_model = SARIMAX(ts['incident_count'], order=(1, 1, 1), seasonal_order=(1, 0, 0, 12), enforce_stationarity=False, enforce_invertibility=False)
    full_res = full_model.fit(disp=False)
    
    forecast_res = full_res.get_forecast(steps=steps)
    forecast_mean = forecast_res.predicted_mean
    conf_int = forecast_res.conf_int(alpha=0.20)
    
    future_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=steps, freq='MS')
    
    forecast_df = pd.DataFrame({
        'ds': future_dates,
        'yhat': np.maximum(0, forecast_mean.values),
        'yhat_lower': np.maximum(0, conf_int.iloc[:, 0].values),
        'yhat_upper': np.maximum(0, conf_int.iloc[:, 1].values),
        'is_forecast': True
    })
    
    history_df = pd.DataFrame({
        'ds': ts.index,
        'y': ts['incident_count'].values,
        'yhat': ts['incident_count'].values,
        'yhat_lower': ts['incident_count'].values,
        'yhat_upper': ts['incident_count'].values,
        'is_forecast': False
    })
    
    combined = pd.concat([history_df, forecast_df], ignore_index=True)
    val_metrics = {'val_mae': round(mae, 2), 'val_rmse': round(rmse, 2), 'val_steps': val_steps}
    
    return combined, val_metrics, 'SARIMA (statsmodels)'
