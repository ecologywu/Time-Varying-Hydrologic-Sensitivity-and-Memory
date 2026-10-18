"""
Step 3: Decompose each response-parameter time series into a
composition component (explained by concurrent forcing-distribution changes)
and a residual drift component.

For each catchment and each parameter (beta_P, beta_VPD, M75_P, M75_VPD):
  theta_t = alpha + X_forcing,t * gamma + epsilon_t
  composition_t = X_forcing,t * gamma  (centered at reference window)
  residual_t = theta_t - composition_t

Forcing features (per window): mean P, VPD p90, aridity PET/P, SM p10, snow fraction.
"""
import os
import numpy as np
import pandas as pd
from numpy.linalg import lstsq

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
MAX_LAG = 90
WINDOW_YEARS = 15

PARAMS = ['beta_P', 'beta_VPD', 'M75_P', 'M75_VPD']

def daylight_hours(lat, doy):
    phi = np.deg2rad(lat)
    delta = np.deg2rad(23.45 * np.sin(2 * np.pi * (284 + doy) / 365.0))
    cos_h = np.clip(-np.tan(phi) * np.tan(delta), -1.0, 1.0)
    return 24.0 / np.pi * np.arccos(cos_h)

def hamon_pet(t_c, svp_kpa, lat, doy):
    N = daylight_hours(lat, doy)
    svp_mb = svp_kpa * 10.0
    return np.maximum(0.1651 * (N / 12.0) * svp_mb * 216.7 / (t_c + 273.3), 0.0)

def compute_window_forcing_features(station_id, centers, lat):
    """Compute forcing-distribution features for each window center."""
    fpath = os.path.join(DATA_DIR, "daily", f"{station_id}.csv.gz")
    df = pd.read_csv(fpath, parse_dates=['date'])
    df['year'] = df['date'].dt.year
    df['doy'] = df['date'].dt.dayofyear
    df['PET_calc'] = hamon_pet(df['t2m_mean_C'].values, df['svp_kPa'].values, lat, df['doy'].values)
    half = WINDOW_YEARS // 2

    feats = []
    for c in centers:
        mask = (df['year'] >= c - half) & (df['year'] <= c + half)
        w = df.loc[mask]
        if len(w) < 1500:
            feats.append({})
            continue
        P_mean = w['tp_sum_m'].mean() * 365.0 * 1000.0  # mm/yr approx
        vpd_p90 = w['vpd_kPa'].quantile(0.90)
        sm_p10 = w['swvl1_mean_m3m3'].quantile(0.10)
        pet_mean = w['PET_calc'].mean() * 365.0
        aridity = pet_mean / max(P_mean, 1e-6)
        snow_frac = (w.loc[w['t2m_mean_C'] < 1.0, 'tp_sum_m'].sum()) / max(w['tp_sum_m'].sum(), 1e-12)
        t_mean = w['t2m_mean_C'].mean()
        feats.append({
            'center_year': c,
            'P_mean_mm': P_mean,
            'VPD_p90': vpd_p90,
            'SM_p10': sm_p10,
            'aridity': aridity,
            'snow_frac': snow_frac,
            'T_mean': t_mean,
        })
    return pd.DataFrame(feats)

def decompose_catchment(grp):
    """Decompose each parameter for one catchment."""
    # Standardize forcing features for stable regression
    feat_cols = ['P_mean_mm', 'VPD_p90', 'SM_p10', 'aridity', 'snow_frac']
    X = grp[feat_cols].values
    # Add intercept
    X_i = np.column_stack([np.ones(len(X)), X])
    # Standardize non-intercept columns
    mu = X.mean(axis=0)
    sd = X.std(axis=0)
    sd[sd < 1e-12] = 1.0
    Xs = (X - mu) / sd
    X_is = np.column_stack([np.ones(len(Xs)), Xs])

    out = grp[['station_id', 'center_year']].copy()
    for p in PARAMS:
        y = grp[p].values
        if len(y) < 6:
            out[p + '_comp'] = np.nan
            out[p + '_resid'] = np.nan
            continue
        coef, *_ = lstsq(X_is, y, rcond=None)
        fitted = X_is @ coef
        # Center composition at reference (first window) so residual captures drift from ref
        comp = fitted - fitted[0]
        resid = y - fitted
        out[p + '_comp'] = comp
        out[p + '_resid'] = resid
    return out

def main():
    params = pd.read_csv(os.path.join(DATA_DIR, "dlm_params_timeseries.csv"))
    params['station_id'] = params['station_id'].astype(str)

    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    attrs['station_id'] = attrs['station_id'].astype(str)
    lat_map = dict(zip(attrs['station_id'], attrs['lat']))

    # Compute forcing features per catchment-window
    all_feats = []
    n = params['station_id'].nunique()
    for i, (sid, grp) in enumerate(params.groupby('station_id')):
        if i % 100 == 0:
            print(f"Forcing features {i}/{n}...")
        centers = sorted(grp['center_year'].unique())
        lat = lat_map.get(sid, 0.0)
        feats = compute_window_forcing_features(sid, centers, lat)
        feats['station_id'] = sid
        all_feats.append(feats)
    feat_df = pd.concat(all_feats, ignore_index=True)

    # Merge with params
    merged = params.merge(feat_df, on=['station_id', 'center_year'], how='left')
    merged = merged.dropna(subset=['P_mean_mm'])

    # Decompose
    decomp_parts = []
    for sid, grp in merged.groupby('station_id'):
        decomp_parts.append(decompose_catchment(grp))
    decomp = pd.concat(decomp_parts, ignore_index=True)

    # Merge back everything
    result = merged.merge(decomp, on=['station_id', 'center_year'], how='left')
    result.to_csv(os.path.join(DATA_DIR, "decomposed_params.csv"), index=False)
    print(f"\nDecomposition records: {len(result)}")
    print("Residual drift summary (standardized):")
    for p in PARAMS:
        r = result[p + '_resid'].dropna()
        print(f"  {p}: mean={r.mean():.4f} std={r.std():.4f}")

if __name__ == "__main__":
    main()
