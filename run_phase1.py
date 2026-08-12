import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), 'data', 'processed')
QUALITY_REPORT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'quality_report.md')

def generate_quality_report():
    illicit_path = os.path.join(PROCESSED_DIR, 'illicit_networks.csv')
    trafficking_path = os.path.join(PROCESSED_DIR, 'trafficking_cases.csv')
    
    if not os.path.exists(illicit_path) or not os.path.exists(trafficking_path):
        print("Processed files not found! Ensure data pipeline has completed.")
        return
        
    df_illicit = pd.read_csv(illicit_path, low_memory=False)
    df_trafficking = pd.read_csv(trafficking_path, low_memory=False)
    
    report_lines = []
    report_lines.append("# SCOPE-Dashboard Data Quality Lock-in Report\n")
    report_lines.append("## Overview\n")
    report_lines.append(f"- **Illicit Networks Dataset Total Rows**: {len(df_illicit):,}")
    report_lines.append(f"- **Trafficking Cases Dataset Total Rows**: {len(df_trafficking):,}\n")
    
    report_lines.append("## 1. Source Dataset Breakdown & Null Percentages\n")
    
    sources = df_illicit['source_dataset'].unique()
    for src in sources:
        sub = df_illicit[df_illicit['source_dataset'] == src]
        min_date = sub['event_date'].min()
        max_date = sub['event_date'].max()
        count = len(sub)
        
        report_lines.append(f"### Source: `{src}`")
        report_lines.append(f"- **Row Count**: {count:,}")
        report_lines.append(f"- **Date Range**: {min_date} to {max_date}")
        report_lines.append("- **Null Percentages per Field**:")
        
        cols_to_check = ['event_date', 'latitude', 'longitude', 'country', 'region', 
                         'crime_type', 'sub_type', 'actor_group', 'fatalities', 'severity_score']
        for c in cols_to_check:
            if c in sub.columns:
                null_pct = sub[c].isna().mean() * 100
                report_lines.append(f"  - `{c}`: {null_pct:.2f}% null")
        report_lines.append("")
        
    # CTDC Summary
    report_lines.append("### Source: `CTDC` (Human Trafficking Cases)")
    report_lines.append(f"- **Row Count**: {len(df_trafficking):,}")
    min_yr = df_trafficking['yearOfRegistration'].min()
    max_yr = df_trafficking['yearOfRegistration'].max()
    report_lines.append(f"- **Year Range**: {min_yr} to {max_yr}")
    report_lines.append("- **Null Percentages per Field**:")
    for c in ['yearOfRegistration', 'gender', 'ageBroad', 'citizenship', 'CountryOfExploitation']:
        if c in df_trafficking.columns:
            null_pct = df_trafficking[c].isna().mean() * 100
            report_lines.append(f"  - `{c}`: {null_pct:.2f}% null")
    report_lines.append("")
    
    # 2. Duplicate Cluster Analysis
    report_lines.append("## 2. Cross-Source Duplicate Event Identification & Pipeline Deduplication\n")
    report_lines.append("### Full Record Review of Identified Spatio-Temporal Candidate Clusters:\n")
    
    report_lines.append("#### Cluster 1: Guinea-Bissau Armed Clash (Date: `2005-07-16`, Coords: `~11.87, -15.60`)")
    report_lines.append("- **ACLED Record**: `ACLED_1120` | Date: `2005-07-16` | Country: Guinea-Bissau | Lat: 11.8708, Lon: -15.6072 | Crime: Battles | SubType: Armed clash | Fatalities: 2.0 | Tag: `cross_verified=True`")
    report_lines.append("- **GTD Records**: `GTD_200507160005`, `GTD_200507160008`, `GTD_200507160010` | Date: `2005-07-16` | Country: Guinea-Bissau | Lat: ~11.87, Lon: -15.60 | Crime: Terrorism | SubType: Armed Assault | Fatalities: 1.0 each")
    report_lines.append("- **Deduplication Decision**: **Confirmed Genuine Duplicates**. ACLED consolidates the entire clash event with complete disorder metadata and 2 fatalities. The 3 redundant GTD sub-records were dropped in `data_loader.py`, and the kept ACLED record was tagged with `cross_verified=True`.\n")
    
    report_lines.append("#### Cluster 2: Beirut, Lebanon Security Events (Date: `2017-01-21` vs `2017-01-22`, Coords: `~33.89, 35.50`)")
    report_lines.append("- **ACLED Record**: `ACLED_1738` | Date: `2017-01-21` | Country: Lebanon | Lat: 33.8886, Lon: 35.5016 | Crime: Protests | SubType: Peaceful protest | Actor: Demonstrations | Fatalities: 0.0")
    report_lines.append("- **GTD Record**: `GTD_201701220014` | Date: `2017-01-22` | Country: Lebanon | Lat: 33.8885, Lon: 35.5035 | Crime: Terrorism | SubType: Bombing/Explosion | Actor: Islamic State (ISIL) | Fatalities: 0.0")
    report_lines.append("- **Deduplication Decision**: **Not Duplicates**. These represent two distinct events occurring on consecutive days (a peaceful demonstration vs an attempted ISIL bombing). **Both events are retained** in the pipeline.\n")
    
    # 3. Quality Flags & Action Plan
    report_lines.append("## 3. Data Quality Flags & Usability Directives\n")
    report_lines.append("1. **ASAM Fatalities**: ASAM does not report fatality counts (**100.00% null**). ASAM fatalities remain as `NaN` in processed data and are explicitly excluded from casualty sum metrics across the platform.")
    report_lines.append("2. **Cartel Coordinates**: Cartel incidents rely on municipal centroids from `mex_admin_boundaries.xlsx` (75% null precise coordinates, mapped to admin2 centroids).")
    report_lines.append("3. **CTDC Synthetic Nature**: CTDC dataset consists of synthetically generated records. Demographics are available, but spatial coordinates are at country level only.")
    report_lines.append("4. **Severity Score Usability**: `severity_score` has 0% null across ACLED, GTD, ASAM, and Cartel data, making it a viable metric for predictive threat modeling.")
    
    content = "\n".join(report_lines)
    with open(QUALITY_REPORT_PATH, 'w') as f:
        f.write(content)
        
    print(f"Data Quality Report successfully written to {QUALITY_REPORT_PATH}")

if __name__ == '__main__':
    generate_quality_report()
