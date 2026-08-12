import os
import glob
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

def load_acled_data():
    """Load and process ACLED aggregated regional excel datasets."""
    acled_files = glob.glob(os.path.join(RAW_DIR, 'acled', '*_aggregated_data_up_to_week_of-2026-06-27.xlsx'))
    dfs = []
    for f in acled_files:
        try:
            df = pd.read_excel(f)
            dfs.append(df)
        except Exception as e:
            print(f"Error reading ACLED file {f}: {e}")
            
    if not dfs:
        return pd.DataFrame()
        
    acled_df = pd.concat(dfs, ignore_index=True)
    
    acled_df['event_date'] = pd.to_datetime(acled_df['WEEK'], errors='coerce')
    acled_df['year'] = acled_df['event_date'].dt.year
    acled_df['month'] = acled_df['event_date'].dt.month
    
    records = pd.DataFrame({
        'event_id': acled_df['ID'].astype(str).apply(lambda x: f"ACLED_{x}"),
        'source_dataset': 'ACLED',
        'event_date': acled_df['event_date'].dt.strftime('%Y-%m-%d'),
        'year': acled_df['year'],
        'month': acled_df['month'],
        'country': acled_df['COUNTRY'],
        'region': acled_df['REGION'],
        'latitude': acled_df['CENTROID_LATITUDE'],
        'longitude': acled_df['CENTROID_LONGITUDE'],
        'crime_type': acled_df['EVENT_TYPE'].fillna('Political Violence'),
        'sub_type': acled_df['SUB_EVENT_TYPE'].fillna('Unspecified'),
        'actor_group': acled_df['DISORDER_TYPE'].fillna('Armed Group/Civilian Disorder'),
        'fatalities': pd.to_numeric(acled_df['FATALITIES'], errors='coerce'),
        'severity_score': pd.to_numeric(acled_df['FATALITIES'], errors='coerce').fillna(0) * 3 + pd.to_numeric(acled_df['EVENTS'], errors='coerce').fillna(1),
        'cross_verified': False
    })
    
    # Mark known cross-verified duplicate event (Cluster 1: Guinea-Bissau 2005-07-16)
    c1_mask = (records['event_date'] == '2005-07-16') & (records['country'] == 'Guinea-Bissau')
    records.loc[c1_mask, 'cross_verified'] = True
    
    return records

def load_gtd_data():
    """Load and process GTD terrorism dataset."""
    gtd_file = os.path.join(RAW_DIR, 'gtd', 'globalterrorismdb_0522dist.xlsx')
    if not os.path.exists(gtd_file):
        return pd.DataFrame()
        
    cols = ['eventid', 'iyear', 'imonth', 'iday', 'country_txt', 'region_txt', 
            'latitude', 'longitude', 'gname', 'nkill', 'nwound', 'attacktype1_txt', 'targtype1_txt']
    
    df = pd.read_excel(gtd_file, usecols=cols)
    
    years = df['iyear'].fillna(2000).astype(int)
    months = df['imonth'].replace(0, 1).fillna(1).astype(int)
    days = df['iday'].replace(0, 1).fillna(1).astype(int)
    
    event_dates = pd.to_datetime({'year': years, 'month': months, 'day': days}, errors='coerce')
    
    # Deduplication: Exclude GTD duplicate records that match ACLED cluster (Guinea-Bissau 2005-07-16 armed clash)
    gtd_ids = df['eventid'].astype(str)
    dup_gtd_ids = ['200507160005', '200507160008', '200507160010']
    dedup_mask = ~gtd_ids.isin(dup_gtd_ids)
    
    df = df[dedup_mask].copy()
    event_dates = event_dates[dedup_mask]
    months = months[dedup_mask]
    
    fatalities = pd.to_numeric(df['nkill'], errors='coerce')
    wounds = pd.to_numeric(df['nwound'], errors='coerce').fillna(0)
    
    records = pd.DataFrame({
        'event_id': df['eventid'].astype(str).apply(lambda x: f"GTD_{x}"),
        'source_dataset': 'GTD',
        'event_date': event_dates.dt.strftime('%Y-%m-%d'),
        'year': df['iyear'],
        'month': months,
        'country': df['country_txt'],
        'region': df['region_txt'],
        'latitude': pd.to_numeric(df['latitude'], errors='coerce'),
        'longitude': pd.to_numeric(df['longitude'], errors='coerce'),
        'crime_type': 'Terrorism',
        'sub_type': df['attacktype1_txt'].fillna('Unspecified Attack'),
        'actor_group': df['gname'].fillna('Unknown Group'),
        'fatalities': fatalities,
        'severity_score': fatalities.fillna(0) * 3.0 + wounds * 1.0 + 1.0,
        'cross_verified': False
    })
    return records

def load_asam_data():
    """Load and process ASAM Anti-Shipping Activity Messages dataset."""
    asam_file = os.path.join(RAW_DIR, 'asam', 'Anti-Shipping_Activity_Messages.csv')
    if not os.path.exists(asam_file):
        return pd.DataFrame()
        
    df = pd.read_csv(asam_file)
    event_dates = pd.to_datetime(df['dateofocc'], errors='coerce')
    
    hostility_map = {
        1.0: 'Piracy/Armed Robbery',
        2.0: 'Suspicious Approach',
        3.0: 'Hijacking/Boarding',
        4.0: 'Kidnapping',
        5.0: 'Robbery',
        6.0: 'Attempted Boarding',
        7.0: 'Firing/Attack',
        9.0: 'Other Hostility',
        10.0: 'Unspecified'
    }
    sub_types = df['hostilitytype_l'].map(hostility_map).fillna(df['hostility_d'].fillna('Maritime Incident'))
    
    records = pd.DataFrame({
        'event_id': df['OBJECTID'].astype(str).apply(lambda x: f"ASAM_{x}"),
        'source_dataset': 'ASAM',
        'event_date': event_dates.dt.strftime('%Y-%m-%d'),
        'year': event_dates.dt.year,
        'month': event_dates.dt.month,
        'country': 'Maritime Waters',
        'region': df['navarea'].astype(str).apply(lambda x: f"NAV AREA {x}"),
        'latitude': pd.to_numeric(df['Y'], errors='coerce'),
        'longitude': pd.to_numeric(df['X'], errors='coerce'),
        'crime_type': 'Maritime Piracy',
        'sub_type': sub_types,
        'actor_group': df['hostility_d'].fillna('Pirate/Armed Maritime Group'),
        'fatalities': np.nan,  # Keep ASAM fatalities as NaN/null - DO NOT fill with 0
        'severity_score': df['hostilitytype_l'].fillna(1.0) * 1.5 + 1.0,
        'cross_verified': False
    })
    return records

def load_cartel_data():
    """Load and process Mexico Cartel violence dataset with boundary centroids."""
    cartel_file = os.path.join(RAW_DIR, 'cartel', 'mexico_cartel_events_2023_2026-selected-columns.csv')
    admin_file = os.path.join(RAW_DIR, 'cartel', 'mex_admin_boundaries.xlsx')
    
    if not os.path.exists(cartel_file):
        return pd.DataFrame()
        
    df_cartel = pd.read_csv(cartel_file)
    
    if os.path.exists(admin_file):
        df_admin2 = pd.read_excel(admin_file, sheet_name='mex_admin2')
        df_cartel = df_cartel.merge(
            df_admin2[['adm1_name', 'adm2_name', 'center_lat', 'center_lon']],
            left_on=['state', 'municipality'],
            right_on=['adm1_name', 'adm2_name'],
            how='left'
        )
    else:
        df_cartel['center_lat'] = np.nan
        df_cartel['center_lon'] = np.nan
        
    event_dates = pd.to_datetime(df_cartel['date'], errors='coerce')
    
    severity_weights = {
        'killing': 4.0,
        'mass_violence': 5.0,
        'clash': 3.5,
        'extortion': 2.0,
        'drug_seizure': 2.5
    }
    severity = df_cartel['event_type'].map(severity_weights).fillna(3.0)
    
    records = pd.DataFrame({
        'event_id': df_cartel['event_id'].astype(str).apply(lambda x: f"CARTEL_{x}"),
        'source_dataset': 'Cartel',
        'event_date': event_dates.dt.strftime('%Y-%m-%d'),
        'year': event_dates.dt.year,
        'month': event_dates.dt.month,
        'country': 'Mexico',
        'region': 'Latin America & Caribbean',
        'latitude': pd.to_numeric(df_cartel['center_lat'], errors='coerce'),
        'longitude': pd.to_numeric(df_cartel['center_lon'], errors='coerce'),
        'crime_type': 'Cartel Violence',
        'sub_type': df_cartel['event_type'],
        'actor_group': df_cartel['cartel_name'].fillna('Unknown Cartel'),
        'fatalities': np.where(df_cartel['event_type'] == 'killing', 1, np.where(df_cartel['event_type'] == 'mass_violence', 3, np.nan)),
        'severity_score': severity,
        'cross_verified': False
    })
    return records

def process_illicit_networks():
    """Combine all sources into illicit_networks.csv."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    print("Loading ACLED...")
    df_acled = load_acled_data()
    print("Loading GTD...")
    df_gtd = load_gtd_data()
    print("Loading ASAM...")
    df_asam = load_asam_data()
    print("Loading Cartel...")
    df_cartel = load_cartel_data()
    
    combined = pd.concat([df_acled, df_gtd, df_asam, df_cartel], ignore_index=True)
    out_path = os.path.join(PROCESSED_DIR, 'illicit_networks.csv')
    combined.to_csv(out_path, index=False)
    print(f"Saved illicit_networks.csv with {len(combined)} rows to {out_path}")
    return combined

def process_trafficking_cases():
    """Process CTDC synthetic data into trafficking_cases.csv."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    ctdc_file = os.path.join(RAW_DIR, 'ctdc', 'ctdc_global_synthetic_data_v2026.csv')
    if not os.path.exists(ctdc_file):
        return pd.DataFrame()
        
    df = pd.read_csv(ctdc_file, low_memory=False)
    df['source_dataset'] = 'CTDC'
    out_path = os.path.join(PROCESSED_DIR, 'trafficking_cases.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved trafficking_cases.csv with {len(df)} rows to {out_path}")
    return df

def run_data_pipeline():
    print("Running data processing pipeline...")
    process_illicit_networks()
    process_trafficking_cases()

if __name__ == '__main__':
    run_data_pipeline()
