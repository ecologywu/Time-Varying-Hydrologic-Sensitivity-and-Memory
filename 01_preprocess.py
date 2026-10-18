"""
Step 1: Data preprocessing and sample selection.
Loads watershed metadata, merges daily ERA5 forcing with daily discharge,
applies inclusion criteria (>=30 years, <5% missing, area < 50,000 km2),
and computes catchment attributes (aridity index, snow fraction, baseflow index).
"""
import os
import glob
import numpy as np
import pandas as pd
from scipy import optimize

# Paths
MET_DIR = r"C:\Users\dell\Desktop\Station_MeteorologicalDatasets2171"
Q_DIR = r"C:\Users\dell\Desktop\DailyDischarges2172"
META_PATH = r"C:\Users\dell\Desktop\Supplementary Fig.S1_Watershed area and mean Q for 2173 Gauges2026078.csv"
OUT_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"

# Inclusion criteria
MIN_YEARS = 30
MAX_MISSING_FRAC = 0.05
MAX_AREA_KM2 = 50000.0

def daylight_hours(lat, doy):
    """Daylight hours from latitude and day of year (Hamon, 1961)."""
    phi = np.deg2rad(lat)
    delta = np.deg2rad(23.45 * np.sin(2 * np.pi * (284 + doy) / 365.0))
    cos_h = -np.tan(phi) * np.tan(delta)
    cos_h = np.clip(cos_h, -1.0, 1.0)
    return 24.0 / np.pi * np.arccos(cos_h)

def hamon_pet(t_c, svp_kpa, lat, doy):
    """Hamon potential evapotranspiration (mm/day)."""
    N = daylight_hours(lat, doy)
    pet = 0.1651 * (N / 12.0) * svp_kpa * 216.7 / (t_c + 273.3)
    return np.maximum(pet, 0.0)

def recursive_baseflow(q, alpha=0.925, passes=3):
    """Lyne-Hollick recursive digital filter for baseflow separation."""
    q = np.asarray(q, dtype=float)
    qf = np.zeros_like(q)
    for _ in range(passes):
        prev = 0.0
        for i in range(len(q)):
            qf[i] = alpha * prev + (1.0 + alpha) / 2.0 * (q[i] - prev if i == 0 else q[i] - q[i-1])
            prev = qf[i]
        q = q - qf
        q = q[::-1]
    baseflow = np.maximum(q, 0.0)
    return baseflow

def process_catchment(station_id, meta_row):
    """Process a single catchment: merge met + Q, apply criteria, compute attributes."""
    met_path = os.path.join(MET_DIR, f"{station_id}.csv")
    q_path = os.path.join(Q_DIR, f"{station_id}.csv")
    if not os.path.exists(met_path) or not os.path.exists(q_path):
        return None

    try:
        met = pd.read_csv(met_path, parse_dates=['date'])
        q = pd.read_csv(q_path)
        q['Date'] = pd.to_datetime(q['Date'])
        q = q.rename(columns={'Date': 'date', 'Flow': 'Q'})
    except Exception:
        return None

    df = pd.merge(met, q, on='date', how='inner')
    if len(df) < MIN_YEARS * 365 * 0.8:
        return None

    # Missing fraction (after merge)
    miss = df['Q'].isna().mean()
    if miss > MAX_MISSING_FRAC:
        return None

    df = df.dropna(subset=['Q']).reset_index(drop=True)
    if len(df) == 0:
        return None

    years = df['date'].dt.year
    n_years = years.nunique()
    if n_years < MIN_YEARS:
        return None

    area = meta_row['流域面积']
    if area > MAX_AREA_KM2:
        return None

    # Compute annual aggregates for attributes
    df['doy'] = df['date'].dt.dayofyear
    lat = meta_row['lat']
    df['PET'] = hamon_pet(df['t2m_mean_C'].values, df['svp_kPa'].values, lat, df['doy'].values)

    # Annual P and PET
    annual = df.groupby(years).agg(
        P=('tp_sum_m', lambda x: np.sum(x) * 1000.0),   # m -> mm
        PET=('PET', 'sum'),
        T=('t2m_mean_C', 'mean'),
    )
    annual_P = annual['P'].mean()
    annual_PET = annual['PET'].mean()
    aridity = annual_PET / max(annual_P, 1e-6)

    # Snow fraction: precipitation when T < 1 deg C
    snow_mask = df['t2m_mean_C'] < 1.0
    snow_frac = (df.loc[snow_mask, 'tp_sum_m'].sum()) / max(df['tp_sum_m'].sum(), 1e-12)

    # Baseflow index
    baseflow = recursive_baseflow(df['Q'].values)
    bfi = np.sum(baseflow) / max(np.sum(df['Q'].values), 1e-12)

    # Mean Q (m3/s)
    mean_q = df['Q'].mean()

    # Save merged daily data
    out = df[['date', 't2m_mean_C', 'tp_sum_m', 'vpd_kPa', 'swvl1_mean_m3m3',
              'e_sum_m', 'wind_speed_ms', 'ssrd_sum_Jm2', 'svp_kPa', 'Q', 'PET']].copy()
    out.to_csv(os.path.join(OUT_DIR, "daily", f"{station_id}.csv.gz"), index=False, compression='gzip')

    return {
        'station_id': str(station_id),
        'area_km2': area,
        'lon': meta_row['long'],
        'lat': lat,
        'n_years': n_years,
        'start_year': int(years.min()),
        'end_year': int(years.max()),
        'missing_frac': miss,
        'mean_Q_m3s': mean_q,
        'annual_P_mm': annual_P,
        'annual_PET_mm': annual_PET,
        'aridity_index': aridity,
        'snow_fraction': snow_frac,
        'baseflow_index': bfi,
        'mean_T_C': annual['T'].mean(),
    }

def main():
    os.makedirs(os.path.join(OUT_DIR, "daily"), exist_ok=True)
    meta = pd.read_csv(META_PATH)
    meta['站点编号'] = meta['站点编号'].astype(str)

    records = []
    n_total = len(meta)
    for i, row in meta.iterrows():
        if i % 200 == 0:
            print(f"Processing {i}/{n_total}...")
        rec = process_catchment(row['站点编号'], row)
        if rec is not None:
            records.append(rec)

    attrs = pd.DataFrame(records)
    attrs.to_csv(os.path.join(OUT_DIR, "catchment_attributes.csv"), index=False)
    print(f"\nTotal catchments passing criteria: {len(attrs)} / {n_total}")
    print(attrs[['area_km2', 'n_years', 'aridity_index', 'snow_fraction', 'baseflow_index']].describe())

if __name__ == "__main__":
    main()
