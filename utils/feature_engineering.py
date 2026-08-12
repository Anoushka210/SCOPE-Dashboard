import os
import pickle
import pandas as pd
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
ENCODER_PATH = os.path.join(MODELS_DIR, 'feature_encoders.pkl')

def create_severity_classes(df):
    """
    Bucket severity_score into 4 discrete classes:
    0: Low (score <= 2.0)
    1: Medium (2.0 < score <= 5.0)
    2: High (5.0 < score <= 15.0)
    3: Critical (score > 15.0)
    """
    scores = df['severity_score'].fillna(1.0).values
    classes = pd.cut(
        scores, 
        bins=[-np.inf, 2.0, 5.0, 15.0, np.inf], 
        labels=[0, 1, 2, 3]
    ).astype(int)
    return pd.Series(classes, index=df.index, name='severity_class')

def extract_temporal_features(df):
    """Extract year, month, day_of_week, and is_weekend from event_date."""
    dates = pd.to_datetime(df['event_date'], errors='coerce')
    # Default missing dates to year/month columns if available
    year = dates.dt.year.fillna(df['year'] if 'year' in df.columns else 2020).astype(int)
    month = dates.dt.month.fillna(df['month'] if 'month' in df.columns else 6).astype(int)
    day_of_week = dates.dt.dayofweek.fillna(2).astype(int) # Default Wednesday
    is_weekend = (day_of_week >= 5).astype(int)
    
    return pd.DataFrame({
        'year': year,
        'month': month,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend
    }, index=df.index)

def build_feature_matrix(df, is_training=True, encoder_path=ENCODER_PATH):
    """
    Build model-ready feature matrix X and target y.
    Saves encoders dictionary if is_training=True, or loads from disk if False.
    """
    df = df.copy()
    os.makedirs(os.path.dirname(encoder_path), exist_ok=True)
    
    # 1. Target bucket
    y = create_severity_classes(df) if 'severity_score' in df.columns else None
    
    # 2. Temporal features
    df_temp = extract_temporal_features(df)
    
    # 3. Categorical encoding
    low_card_cols = ['crime_type', 'region']
    high_card_cols = ['country', 'sub_type', 'actor_group']
    
    if is_training:
        encoders = {
            'freq_encoders': {},
            'dummies_columns': [],
            'feature_names': []
        }
        
        # High-cardinality frequency encoding
        df_high = pd.DataFrame(index=df.index)
        for col in high_card_cols:
            freq_map = df[col].fillna('Unknown').value_counts(normalize=True).to_dict()
            encoders['freq_encoders'][col] = freq_map
            df_high[f'{col}_freq'] = df[col].fillna('Unknown').map(freq_map).fillna(0.0)
            
        # Low-cardinality One-Hot Encoding
        df_low = pd.get_dummies(df[low_card_cols].fillna('Unknown'), drop_first=False)
        encoders['dummies_columns'] = df_low.columns.tolist()
        
        # Coordinates & Fatalities features
        df_num = pd.DataFrame({
            'latitude': df['latitude'].fillna(0.0),
            'longitude': df['longitude'].fillna(0.0),
            'fatalities': df['fatalities'].fillna(0.0)
        }, index=df.index)
        
        X = pd.concat([df_temp, df_num, df_high, df_low], axis=1)
        encoders['feature_names'] = X.columns.tolist()
        
        with open(encoder_path, 'wb') as f:
            pickle.dump(encoders, f)
        print(f"Encoders saved to {encoder_path}")
        
    else:
        with open(encoder_path, 'rb') as f:
            encoders = pickle.load(f)
            
        # Frequency encoding
        df_high = pd.DataFrame(index=df.index)
        for col in high_card_cols:
            freq_map = encoders['freq_encoders'].get(col, {})
            df_high[f'{col}_freq'] = df[col].fillna('Unknown').map(freq_map).fillna(0.0)
            
        # One-Hot Encoding aligned with training columns
        df_low_raw = pd.get_dummies(df[low_card_cols].fillna('Unknown'), drop_first=False)
        df_low = df_low_raw.reindex(columns=encoders['dummies_columns'], fill_value=0)
        
        df_num = pd.DataFrame({
            'latitude': df['latitude'].fillna(0.0),
            'longitude': df['longitude'].fillna(0.0),
            'fatalities': df['fatalities'].fillna(0.0)
        }, index=df.index)
        
        X = pd.concat([df_temp, df_num, df_high, df_low], axis=1)
        X = X.reindex(columns=encoders['feature_names'], fill_value=0)
        
    return X, y

def encode_single_input(input_dict, encoder_path=ENCODER_PATH):
    """
    Encode a single inference dictionary into a 1-row DataFrame matching training feature columns.
    input_dict keys: ['crime_type', 'sub_type', 'region', 'country', 'actor_group', 
                     'latitude', 'longitude', 'fatalities', 'event_date']
    """
    df_single = pd.DataFrame([input_dict])
    X_single, _ = build_feature_matrix(df_single, is_training=False, encoder_path=encoder_path)
    return X_single
