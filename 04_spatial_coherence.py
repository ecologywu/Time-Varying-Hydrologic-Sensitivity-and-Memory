"""
Step 4: Spatial coherence analysis of residual drift.
- Compute catchment-level residual drift magnitude (OLS slope of residual time series).
- Moran's I (k=6 nearest neighbors) with stratified randomization null distribution.
- Regression of residual drift magnitude on forcing-change magnitude vs estimation conditions.
- Nearest-neighbor sign consistency test.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"

PARAMS = ['beta_P', 'beta_VPD', 'M75_P', 'M75_VPD']

def calc_drift_slope(series):
    """OLS slope of a parameter time series (units per year)."""
    s = series.dropna()
    if len(s) < 6:
        return np.nan
    x = np.arange(len(s))
    slope, *_ = stats.linregress(x, s.values)
    return slope

def standardize(x):
    x = np.asarray(x, dtype=float)
    return (x - np.nanmean(x)) / (np.nanstd(x) + 1e-12)

def morans_I(values, neighbors):
    """
    Moran's I.
    values: array of catchment-level values
    neighbors: list of lists (k nearest neighbor indices per catchment)
    """
    n = len(values)
    v = standardize(values)
    num = 0.0
    W = 0
    for i in range(n):
        for j in neighbors[i]:
            num += v[i] * v[j]
            W += 1
    denom = np.sum(v ** 2)
    if W == 0 or denom < 1e-12:
        return np.nan
    return (n / W) * (num / denom)

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"))
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    dec['station_id'] = dec['station_id'].astype(str)
    attrs['station_id'] = attrs['station_id'].astype(str)

    # Catchment-level residual drift = slope of residual time series
    drift_records = []
    for sid, grp in dec.groupby('station_id'):
        rec = {'station_id': sid}
        grp = grp.sort_values('center_year')
        for p in PARAMS:
            rec[p + '_drift'] = calc_drift_slope(grp[p + '_resid'])
            # Also total drift (actual parameter slope)
            rec[p + '_totaldrift'] = calc_drift_slope(grp[p])
        # Forcing change magnitude: euclidean distance of forcing features first vs last window
        feat_cols = ['P_mean_mm', 'VPD_p90', 'SM_p10', 'aridity', 'snow_frac']
        first = grp[feat_cols].iloc[0].values
        last = grp[feat_cols].iloc[-1].values
        rec['forcing_change_mag'] = np.sqrt(np.sum((last - first) ** 2))
        # Estimation conditions
        rec['n_windows'] = len(grp)
        drift_records.append(rec)
    drift = pd.DataFrame(drift_records)

    # Merge with attributes
    drift = drift.merge(attrs[['station_id', 'lon', 'lat', 'aridity_index',
                               'snow_fraction', 'baseflow_index', 'area_km2', 'n_years']],
                        on='station_id', how='left')
    drift = drift.dropna(subset=['lon', 'lat'])

    # k-nearest neighbors (k=6) based on lon/lat
    from scipy.spatial import cKDTree
    coords = drift[['lon', 'lat']].values
    # Convert to 3D for proper distance
    lat_r = np.deg2rad(coords[:, 1])
    lon_r = np.deg2rad(coords[:, 0])
    x = np.cos(lat_r) * np.cos(lon_r)
    y = np.cos(lat_r) * np.sin(lon_r)
    z = np.sin(lat_r)
    tree = cKDTree(np.column_stack([x, y, z]))
    k = 6
    _, nn_idx = tree.query(np.column_stack([x, y, z]), k=k + 1)
    neighbors = [list(idx[1:]) for idx in nn_idx]

    # Moran's I with stratified permutation null (within aridity bins)
    drift['aridity_bin'] = pd.qcut(drift['aridity_index'], q=5, labels=False, duplicates='drop')
    results = {}
    n_perm = 1000
    for p in PARAMS:
        vals = drift[p + '_drift'].values
        valid = ~np.isnan(vals)
        if valid.sum() < 50:
            continue
        obs_I = morans_I(vals[valid], [neighbors[i] for i in range(len(neighbors)) if valid[i]])
        # Stratified permutation: shuffle within aridity bins
        perm_I = []
        valid_idx = np.where(valid)[0]
        bins = drift['aridity_bin'].values[valid]
        for _ in range(n_perm):
            shuffled = vals[valid].copy()
            for b in np.unique(bins):
                in_bin = np.where(bins == b)[0]
                perm = np.random.permutation(in_bin)
                shuffled[in_bin] = vals[valid][perm]
            perm_I.append(morans_I(shuffled, [neighbors[i] for i in valid_idx]))
        pval = np.mean(np.array(perm_I) >= obs_I)
        results[p] = {'obs_I': obs_I, 'p_value': pval,
                      'I_mean_null': np.mean(perm_I), 'I_std_null': np.std(perm_I)}
        print(f"{p}: Moran's I = {obs_I:.4f}, p = {pval:.4f} (null mean={np.mean(perm_I):.4f})")

    # Save Moran's I results
    pd.DataFrame(results).T.to_csv(os.path.join(DATA_DIR, "morans_I_results.csv"))

    # Regression: residual drift magnitude on forcing change vs estimation conditions
    drift['Q_CV'] = np.nan  # will fill from attributes if available
    reg_results = {}
    for p in PARAMS:
        y = np.abs(drift[p + '_drift'].dropna())
        if len(y) < 50:
            continue
        sub = drift.loc[y.index]
        # Standardized regression coefficients
        X_forc = standardize(sub['forcing_change_mag'].values)
        X_nyrs = standardize(sub['n_years'].values)
        X_area = standardize(sub['area_km2'].values)
        X_mat = np.column_stack([np.ones(len(X_forc)), X_forc, X_nyrs, X_area])
        coef, *_ = np.linalg.lstsq(X_mat, y.values, rcond=None)
        reg_results[p] = {'beta_forcing_change': coef[1],
                          'beta_n_years': coef[2],
                          'beta_area': coef[3]}
    pd.DataFrame(reg_results).T.to_csv(os.path.join(DATA_DIR, "drift_regression_results.csv"))

    # Nearest neighbor sign consistency
    nn_consistency = {}
    for p in PARAMS:
        vals = drift[p + '_drift'].values
        sign = np.sign(vals)
        valid = ~np.isnan(vals)
        obs_consist = []
        rand_consist = []
        valid_idx = np.where(valid)[0]
        for i in valid_idx:
            nbrs = [j for j in neighbors[i] if valid[j]]
            if len(nbrs) == 0:
                continue
            obs_consist.append(np.mean(np.sign(vals[nbrs]) == sign[i]))
        # random pairing
        for _ in range(100):
            rand_sign = sign[valid_idx].copy()
            np.random.shuffle(rand_sign)
            rc = []
            for k_i, i in enumerate(valid_idx):
                nbrs = [j for j in neighbors[i] if valid[j]]
                if len(nbrs) == 0:
                    continue
                # map neighbor global idx to valid_idx position
                nb_pos = [np.where(valid_idx == j)[0][0] for j in nbrs]
                rc.append(np.mean(rand_sign[nb_pos] == rand_sign[k_i]))
            rand_consist.append(np.mean(rc))
        nn_consistency[p] = {'obs': np.mean(obs_consist),
                             'rand_mean': np.mean(rand_consist),
                             'rand_std': np.std(rand_consist)}
        print(f"{p} NN sign consistency: obs={np.mean(obs_consist):.3f}, rand={np.mean(rand_consist):.3f}")
    pd.DataFrame(nn_consistency).T.to_csv(os.path.join(DATA_DIR, "nn_consistency_results.csv"))

    # Save catchment-level drift table
    drift.to_csv(os.path.join(DATA_DIR, "catchment_drift.csv"), index=False)
    print("\nSpatial coherence analysis complete.")

if __name__ == "__main__":
    main()
