"""
Step 2: Time-varying response function estimation via Distributed Lag Model (DLM)
in rolling 15-year windows.

For each catchment:
- Remove day-of-year climatology (31-day centered moving average) from P, VPD, SM, Q.
- Build lagged design matrix using a natural cubic spline basis (df=4) over lags 0..89.
- For each 15-year rolling window (1-year step), fit OLS.
- Extract:
    sensitivity_beta_P  = sum of lag coefficients for precipitation
    sensitivity_beta_VPD = sum of lag coefficients for VPD
    memory_M75_P         = lag (days) at which cumulative |lag coef| reaches 75% of total
- Save parameter time series (catchment x window).
"""
import os
import numpy as np
import pandas as pd
from numpy.linalg import lstsq

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"

# DLM settings
MAX_LAG = 90
LAG_DF = 4          # natural cubic spline df for lag dimension
WINDOW_YEARS = 15   # rolling window half-width equivalent = 15-yr full window
STEP_YEARS = 1

def natural_cubic_spline_basis(x, df=4):
    """
    Natural cubic spline basis matrix for the lag dimension.
    Returns basis of shape (len(x), df).
    Knots are placed at quantiles of x.
    """
    x = np.asarray(x, dtype=float)
    n_knots = df + 1  # K knots -> K-1 = df basis functions
    quantiles = np.linspace(0, 1, n_knots)
    knots = np.quantile(x, quantiles)
    knots = np.unique(knots)
    if len(knots) < n_knots:
        # fallback: evenly spaced
        knots = np.linspace(x.min(), x.max(), n_knots)

    K = len(knots)
    # truncated power basis for natural cubic spline
    d = np.zeros((len(x), K - 2))
    for j in range(K - 2):
        num = np.maximum(x - knots[j], 0.0) ** 3
        den = knots[-1] - knots[j]
        d[:, j] = num / den if den != 0 else 0.0
    # subtract the last d column to enforce natural boundary conditions
    if K >= 3:
        d_last = d[:, -1:]
        d = d - d_last
    # The basis: linear term + (K-2) nonlinear terms
    basis = np.column_stack([x, d])
    return basis

def build_lag_matrix(series, max_lag, basis):
    """
    Build lagged predictor matrix projected onto spline basis.
    series: 1-D array (n_days,)
    basis: (max_lag, df) spline basis for lags 0..max_lag-1
    Returns: (n_days - max_lag + 1, df)
    """
    n = len(series)
    # lagged matrix: row i has [series[i], series[i-1], ..., series[i-max_lag+1]]
    # use stride tricks for efficiency
    from numpy.lib.stride_tricks import sliding_window_view
    lagged = sliding_window_view(series, max_lag)  # (n-max_lag+1, max_lag)
    # reverse so that column 0 = lag 0
    lagged = lagged[:, ::-1]
    projected = lagged @ basis  # (n-max_lag+1, df)
    return projected

def estimate_catchment(station_id, attrs_row):
    """Estimate time-varying DLM parameters for one catchment."""
    fpath = os.path.join(DATA_DIR, "daily", f"{station_id}.csv.gz")
    df = pd.read_csv(fpath, parse_dates=['date'])

    # Anomalize: subtract day-of-year climatology (31-day centered moving avg of daily mean)
    for col in ['tp_sum_m', 'vpd_kPa', 'swvl1_mean_m3m3', 'Q']:
        daily_mean = df.groupby(df['date'].dt.dayofyear)[col].transform('mean')
        # 31-day centered smoothing
        daily_smooth = daily_mean.rolling(31, center=True, min_periods=1).mean()
        df[col + '_anom'] = df[col] - daily_smooth

    P = df['tp_sum_m_anom'].values
    VPD = df['vpd_kPa_anom'].values
    SM = df['swvl1_mean_m3m3_anom'].values
    Q = df['Q_anom'].values
    dates = df['date'].values
    years = df['date'].dt.year.values

    # Build spline basis for lags 0..MAX_LAG-1
    lag_basis = natural_cubic_spline_basis(np.arange(MAX_LAG), df=LAG_DF)  # (MAX_LAG, df)

    # Build full projected lag matrices (will index windows later)
    Xp = build_lag_matrix(P, MAX_LAG, lag_basis)
    Xv = build_lag_matrix(VPD, MAX_LAG, lag_basis)
    Xs = build_lag_matrix(SM, MAX_LAG, lag_basis)
    # Align Q (drop first MAX_LAG-1 days)
    Q_aligned = Q[MAX_LAG - 1:]
    dates_aligned = dates[MAX_LAG - 1:]
    years_aligned = years[MAX_LAG - 1:]

    # Design matrix: intercept + P(df) + VPD(df) + SM(df)
    X_full = np.column_stack([np.ones(len(Q_aligned)), Xp, Xv, Xs])
    n_feat = X_full.shape[1]

    # Determine window centers
    y_min, y_max = int(years_aligned.min()), int(years_aligned.max())
    half = WINDOW_YEARS // 2
    centers = list(range(y_min + half, y_max - half + 1, STEP_YEARS))

    records = []
    for c in centers:
        mask = (years_aligned >= c - half) & (years_aligned <= c + half)
        Xw = X_full[mask]
        Qw = Q_aligned[mask]
        if len(Qw) < 1500:
            continue
        # OLS
        coef, residuals, rank, sv = lstsq(Xw, Qw, rcond=None)
        # Decompose: intercept + Pcoef(df) + Vcoef(df) + Scoef(df)
        p_coef = coef[1:1+LAG_DF]
        v_coef = coef[1+LAG_DF:1+2*LAG_DF]
        s_coef = coef[1+2*LAG_DF:1+3*LAG_DF]
        # Lag coefficient curves
        p_lag_curve = lag_basis @ p_coef  # (MAX_LAG,)
        v_lag_curve = lag_basis @ v_coef
        s_lag_curve = lag_basis @ s_coef
        # Sensitivity = sum of lag coefficients (cumulative marginal effect)
        beta_P = np.sum(p_lag_curve)
        beta_VPD = np.sum(v_lag_curve)
        beta_SM = np.sum(s_lag_curve)
        # Memory M75 = lag where cumulative |coef| reaches 75% of total
        def m75(curve):
            abs_c = np.abs(curve)
            total = np.sum(abs_c)
            if total < 1e-15:
                return np.nan
            cum = np.cumsum(abs_c)
            idx = np.searchsorted(cum, 0.75 * total)
            return float(min(idx, MAX_LAG - 1))
        M75_P = m75(p_lag_curve)
        M75_VPD = m75(v_lag_curve)
        M75_SM = m75(s_lag_curve)

        records.append({
            'station_id': str(station_id),
            'center_year': c,
            'beta_P': beta_P,
            'beta_VPD': beta_VPD,
            'beta_SM': beta_SM,
            'M75_P': M75_P,
            'M75_VPD': M75_VPD,
            'M75_SM': M75_SM,
            'n_obs': int(mask.sum()),
            # spline coefficients for reconstruction
            'thP0': p_coef[0], 'thP1': p_coef[1], 'thP2': p_coef[2], 'thP3': p_coef[3],
            'thV0': v_coef[0], 'thV1': v_coef[1], 'thV2': v_coef[2], 'thV3': v_coef[3],
            'thS0': s_coef[0], 'thS1': s_coef[1], 'thS2': s_coef[2], 'thS3': s_coef[3],
        })

    return records

def main():
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    attrs['station_id'] = attrs['station_id'].astype(str)
    all_records = []
    n = len(attrs)
    for i, row in attrs.iterrows():
        if i % 100 == 0:
            print(f"DLM estimation {i}/{n}...")
        try:
            recs = estimate_catchment(row['station_id'], row)
            all_records.extend(recs)
        except Exception as e:
            print(f"  Error on {row['station_id']}: {e}")

    params = pd.DataFrame(all_records)
    params.to_csv(os.path.join(DATA_DIR, "dlm_params_timeseries.csv"), index=False)
    print(f"\nTotal parameter records: {len(params)}")
    print(f"Catchments with params: {params['station_id'].nunique()}")
    print(params[['beta_P', 'beta_VPD', 'M75_P']].describe())

if __name__ == "__main__":
    main()
