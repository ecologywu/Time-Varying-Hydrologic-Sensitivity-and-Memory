"""
Fix: recompute aridity index (correct Hamon PET with svp in mb)
and baseflow index (UKIH 5-day method) from saved daily data.
"""
import os
import numpy as np
import pandas as pd

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"

def daylight_hours(lat, doy):
    phi = np.deg2rad(lat)
    delta = np.deg2rad(23.45 * np.sin(2 * np.pi * (284 + doy) / 365.0))
    cos_h = np.clip(-np.tan(phi) * np.tan(delta), -1.0, 1.0)
    return 24.0 / np.pi * np.arccos(cos_h)

def hamon_pet(t_c, svp_kpa, lat, doy):
    """Hamon PET (mm/day). svp converted kPa->mb."""
    N = daylight_hours(lat, doy)
    svp_mb = svp_kpa * 10.0
    pet = 0.1651 * (N / 12.0) * svp_mb * 216.7 / (t_c + 273.3)
    return np.maximum(pet, 0.0)

def ukih_baseflow(Q, window=5):
    Q = np.asarray(Q, dtype=float)
    n = len(Q)
    n_win = n // window
    minima = []
    centers = []
    for i in range(n_win):
        seg = Q[i*window:(i+1)*window]
        minima.append(np.min(seg))
        centers.append(i*window + window//2)
    minima = np.array(minima)
    centers = np.array(centers)
    bf = np.interp(np.arange(n), centers, minima)
    return np.minimum(bf, Q)

def main():
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    attrs['station_id'] = attrs['station_id'].astype(str)
    daily_dir = os.path.join(DATA_DIR, "daily")

    for i, row in attrs.iterrows():
        if i % 200 == 0:
            print(f"Fixing {i}/{len(attrs)}...")
        sid = row['station_id']
        fpath = os.path.join(daily_dir, f"{sid}.csv.gz")
        df = pd.read_csv(fpath, parse_dates=['date'])
        lat = row['lat']
        df['doy'] = df['date'].dt.dayofyear
        df['PET'] = hamon_pet(df['t2m_mean_C'].values, df['svp_kPa'].values, lat, df['doy'].values)
        years = df['date'].dt.year
        annual = df.groupby(years).agg(
            P=('tp_sum_m', lambda x: np.sum(x) * 1000.0),
            PET=('PET', 'sum'),
        )
        annual_P = annual['P'].mean()
        annual_PET = annual['PET'].mean()
        attrs.loc[i, 'annual_P_mm'] = annual_P
        attrs.loc[i, 'annual_PET_mm'] = annual_PET
        attrs.loc[i, 'aridity_index'] = annual_PET / max(annual_P, 1e-6)
        # BFI
        bf = ukih_baseflow(df['Q'].values)
        attrs.loc[i, 'baseflow_index'] = np.sum(bf) / max(np.sum(df['Q'].values), 1e-12)

    attrs.to_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"), index=False)
    print("\nFixed attributes summary:")
    print(attrs[['aridity_index', 'baseflow_index', 'annual_P_mm', 'annual_PET_mm']].describe())

if __name__ == "__main__":
    main()
