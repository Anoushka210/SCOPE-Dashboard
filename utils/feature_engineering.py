import os
import pickle
import pandas as pd
import numpy as np

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
ENCODER_PATH = os.path.join(MODELS_DIR, 'feature_encoders.pkl')

def create_severity_classes(df):
    """
    Bucket continuous severity_score into 4 discrete classes:
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
    year = dates.dt.year.fillna(df['year'] if 'year' in df.columns else 2024).astype(int)
    month = dates.dt.month.fillna(df['month'] if 'month' in df.columns else 6).astype(int)
    day_of_week = dates.dt.dayofweek.fillna(2).astype(int) # Default Wednesday
    is_weekend = (day_of_week >= 5).astype(int)
    
    return pd.DataFrame({
        'year': year,
        'month': month,
        'day_of_week': day_of_week,
        'is_weekend': is_weekend
    }, index=df.index)

def fit_feature_encoders(train_df):
    """
    Fit frequency encoders and dummy columns STRICTLY on training split (no future leakage).
    """
    low_card_cols = ['crime_type', 'region']
    high_card_cols = ['country', 'sub_type', 'actor_group']

    encoders = {
        'freq_encoders': {},
        'dummies_columns': [],
        'feature_names': []
    }

    for col in high_card_cols:
        freq_map = train_df[col].fillna('Unknown').value_counts(normalize=True).to_dict()
        encoders['freq_encoders'][col] = freq_map

    df_low = pd.get_dummies(train_df[low_card_cols].fillna('Unknown'), drop_first=False)
    encoders['dummies_columns'] = df_low.columns.tolist()

    df_temp = extract_temporal_features(train_df)
    df_num = pd.DataFrame({
        'latitude': train_df['latitude'].fillna(0.0),
        'longitude': train_df['longitude'].fillna(0.0)
    }, index=train_df.index)

    df_high = pd.DataFrame(index=train_df.index)
    for col in high_card_cols:
        df_high[f'{col}_freq'] = train_df[col].fillna('Unknown').map(encoders['freq_encoders'][col]).fillna(0.0)

    X_train = pd.concat([df_temp, df_num, df_high, df_low], axis=1)
    encoders['feature_names'] = X_train.columns.tolist()

    return encoders

def transform_feature_matrix(df, encoders):
    """
    Transform raw dataframe using pre-fitted encoders.
    CRITICAL: Excludes 'fatalities' or any target-derived leakage features.
    """
    low_card_cols = ['crime_type', 'region']
    high_card_cols = ['country', 'sub_type', 'actor_group']

    y = create_severity_classes(df) if 'severity_score' in df.columns else None
    df_temp = extract_temporal_features(df)

    # Coordinates only - NO fatalities, nkill, nwound, EVENTS
    df_num = pd.DataFrame({
        'latitude': pd.to_numeric(df['latitude'], errors='coerce').fillna(0.0),
        'longitude': pd.to_numeric(df['longitude'], errors='coerce').fillna(0.0)
    }, index=df.index)

    # Frequency encoding using pre-fitted training maps
    df_high = pd.DataFrame(index=df.index)
    for col in high_card_cols:
        freq_map = encoders['freq_encoders'].get(col, {})
        df_high[f'{col}_freq'] = df[col].fillna('Unknown').map(freq_map).fillna(0.0)

    # One-Hot Encoding aligned strictly with training dummies
    df_low_raw = pd.get_dummies(df[low_card_cols].fillna('Unknown'), drop_first=False)
    df_low = df_low_raw.reindex(columns=encoders['dummies_columns'], fill_value=0)

    X = pd.concat([df_temp, df_num, df_high, df_low], axis=1)
    X = X.reindex(columns=encoders['feature_names'], fill_value=0)

    return X, y

def build_feature_matrix(df, is_training=True, encoder_path=ENCODER_PATH):
    """
    Backward-compatible entry point for feature matrix construction.
    """
    os.makedirs(os.path.dirname(encoder_path), exist_ok=True)
    if is_training:
        encoders = fit_feature_encoders(df)
        with open(encoder_path, 'wb') as f:
            pickle.dump(encoders, f)
        X, y = transform_feature_matrix(df, encoders)
    else:
        with open(encoder_path, 'rb') as f:
            encoders = pickle.load(f)
        X, y = transform_feature_matrix(df, encoders)
    return X, y

def encode_single_input(input_dict, encoder_path=ENCODER_PATH):
    """
    Encode a single inference dictionary into a 1-row DataFrame.
    input_dict keys: ['crime_type', 'sub_type', 'region', 'country', 'actor_group', 
                      'latitude', 'longitude', 'event_date', 'year', 'month']
    """
    df_single = pd.DataFrame([input_dict])
    with open(encoder_path, 'rb') as f:
        encoders = pickle.load(f)
    X_single, _ = transform_feature_matrix(df_single, encoders)
    return X_single
