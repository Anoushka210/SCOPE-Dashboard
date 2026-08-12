# SCOPE-Dashboard Data Quality Lock-in Report

## Overview

- **Illicit Networks Dataset Total Rows**: 1,186,952
- **Trafficking Cases Dataset Total Rows**: 268,515

## 1. Source Dataset Breakdown & Null Percentages

### Source: `ACLED`
- **Row Count**: 968,024
- **Date Range**: 1996-12-28 to 2026-06-27
- **Null Percentages per Field**:
  - `event_date`: 0.00% null
  - `latitude`: 0.00% null
  - `longitude`: 0.00% null
  - `country`: 0.00% null
  - `region`: 0.00% null
  - `crime_type`: 0.00% null
  - `sub_type`: 0.00% null
  - `actor_group`: 0.00% null
  - `fatalities`: 0.00% null
  - `severity_score`: 0.00% null

### Source: `GTD`
- **Row Count**: 209,706
- **Date Range**: 1970-01-01 to 2020-12-31
- **Null Percentages per Field**:
  - `event_date`: 0.00% null
  - `latitude`: 2.24% null
  - `longitude`: 2.24% null
  - `country`: 0.00% null
  - `region`: 0.00% null
  - `crime_type`: 0.00% null
  - `sub_type`: 0.00% null
  - `actor_group`: 0.00% null
  - `fatalities`: 0.00% null
  - `severity_score`: 0.00% null

### Source: `ASAM`
- **Row Count**: 9,182
- **Date Range**: 1978-05-01 to 2024-06-25
- **Null Percentages per Field**:
  - `event_date`: 0.00% null
  - `latitude`: 0.00% null
  - `longitude`: 0.00% null
  - `country`: 0.00% null
  - `region`: 0.00% null
  - `crime_type`: 0.00% null
  - `sub_type`: 0.00% null
  - `actor_group`: 0.00% null
  - `fatalities`: 100.00% null
  - `severity_score`: 0.00% null

### Source: `Cartel`
- **Row Count**: 40
- **Date Range**: 2023-01-01 to 2026-02-25
- **Null Percentages per Field**:
  - `event_date`: 0.00% null
  - `latitude`: 75.00% null
  - `longitude`: 75.00% null
  - `country`: 0.00% null
  - `region`: 0.00% null
  - `crime_type`: 0.00% null
  - `sub_type`: 0.00% null
  - `actor_group`: 0.00% null
  - `fatalities`: 50.00% null
  - `severity_score`: 0.00% null

### Source: `CTDC` (Human Trafficking Cases)
- **Row Count**: 268,515
- **Year Range**: 2002.0 to 2024.0
- **Null Percentages per Field**:
  - `yearOfRegistration`: 14.23% null
  - `gender`: 20.79% null
  - `ageBroad`: 46.11% null
  - `citizenship`: 50.18% null
  - `CountryOfExploitation`: 22.02% null

## 2. Cross-Source Duplicate Event Identification & Pipeline Deduplication

### Full Record Review of Identified Spatio-Temporal Candidate Clusters:

#### Cluster 1: Guinea-Bissau Armed Clash (Date: `2005-07-16`, Coords: `~11.87, -15.60`)
- **ACLED Record**: `ACLED_1120` | Date: `2005-07-16` | Country: Guinea-Bissau | Lat: 11.8708, Lon: -15.6072 | Crime: Battles | SubType: Armed clash | Fatalities: 2.0 | Tag: `cross_verified=True`
- **GTD Records**: `GTD_200507160005`, `GTD_200507160008`, `GTD_200507160010` | Date: `2005-07-16` | Country: Guinea-Bissau | Lat: ~11.87, Lon: -15.60 | Crime: Terrorism | SubType: Armed Assault | Fatalities: 1.0 each
- **Deduplication Decision**: **Confirmed Genuine Duplicates**. ACLED consolidates the entire clash event with complete disorder metadata and 2 fatalities. The 3 redundant GTD sub-records were dropped in `data_loader.py`, and the kept ACLED record was tagged with `cross_verified=True`.

#### Cluster 2: Beirut, Lebanon Security Events (Date: `2017-01-21` vs `2017-01-22`, Coords: `~33.89, 35.50`)
- **ACLED Record**: `ACLED_1738` | Date: `2017-01-21` | Country: Lebanon | Lat: 33.8886, Lon: 35.5016 | Crime: Protests | SubType: Peaceful protest | Actor: Demonstrations | Fatalities: 0.0
- **GTD Record**: `GTD_201701220014` | Date: `2017-01-22` | Country: Lebanon | Lat: 33.8885, Lon: 35.5035 | Crime: Terrorism | SubType: Bombing/Explosion | Actor: Islamic State (ISIL) | Fatalities: 0.0
- **Deduplication Decision**: **Not Duplicates**. These represent two distinct events occurring on consecutive days (a peaceful demonstration vs an attempted ISIL bombing). **Both events are retained** in the pipeline.

## 3. Data Quality Flags & Usability Directives

1. **ASAM Fatalities**: ASAM does not report fatality counts (**100.00% null**). ASAM fatalities remain as `NaN` in processed data and are explicitly excluded from casualty sum metrics across the platform.
2. **Cartel Coordinates**: Cartel incidents rely on municipal centroids from `mex_admin_boundaries.xlsx` (75% null precise coordinates, mapped to admin2 centroids).
3. **CTDC Synthetic Nature**: CTDC dataset consists of synthetically generated records. Demographics are available, but spatial coordinates are at country level only.
4. **Severity Score Usability**: `severity_score` has 0% null across ACLED, GTD, ASAM, and Cartel data, making it a viable metric for predictive threat modeling.