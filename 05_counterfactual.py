"""
Step 5: Counterfactual attribution experiment.
Reconstruct daily streamflow under three response scenarios:
  Factual      : actual time-varying spline coefficients theta(t)
  Counterfac A : theta frozen at first window (stable response)
  Counterfac B : theta = composition component only (residual drift removed)
Then compute Theil-Sen trend of annual runoff and attribution bias.
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
from numpy.linalg import lstsq

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
MAX_LAG = 90
LAG_DF = 4
WINDOW_YEARS = 15

SPLINE_COLS = [f'thP{i}' for i in range(4)] + [f'thV{i}' for i in range(4)] + [f'thS{i}' for i in range(4)]
FEAT_COLS = ['P_mean_mm', 'VPD_p90', 'SM_p10', 'aridity', 'snow_frac']

def natural_cubic_spline_basis(x, df=4):
    x = np.asarray(x, dtype=float)
    n_knots = df + 1
    quantiles = np.linspace(0, 1, n_knots)
    knots = np.quantile(x, quantiles)
    knots = np.unique(knots)
    if len(knots) < n_knots:
        knots = np.linspace(x.min(), x.max(), n_knots)
    K = len(knots)
    d = np.zeros((len(x), K - 2))
    for j in range(K - 2):
        num = np.maximum(x - knots[j], 0.0) ** 3
        den = knots[-1] - knots[j]
        d[:, j] = num / den if den != 0 else 0.0
    if K >= 3:
        d = d - d[:, -1:]
    return np.column_stack([x, d])

def build_lag_matrix(series, max_lag, basis):
    from numpy.lib.stride_tricks import sliding_window_view
    lagged = sliding_window_view(series, max_lag)[:, ::-1]
    return lagged @ basis

def theil_sen_slope(y):
    """Theil-Sen slope estimator."""
    y = np.asarray(y, dtype=float)
    n = len(y)
    if n < 3:
        return np.nan
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            if j != i:
                slopes.append((y[j] - y[i]) / (j - i))
    return np.median(slopes)

def process_catchment(station_id, dec_grp):
    """Run counterfactual experiment for one catchment."""
    fpath = os.path.join(DATA_DIR, "daily", f"{station_id}.csv.gz")
    df = pd.read_csv(fpath, parse_dates=['date'])

    # Anomalize
    for col in ['tp_sum_m', 'vpd_kPa', 'swvl1_mean_m3m3', 'Q']:
        daily_mean = df.groupby(df['date'].dt.dayofyear)[col].transform('mean')
        daily_smooth = daily_mean.rolling(31, center=True, min_periods=1).mean()
        df[col + '_anom'] = df[col] - daily_smooth

    P = df['tp_sum_m_anom'].values
    VPD = df['vpd_kPa_anom'].values
    SM = df['swvl1_mean_m3m3_anom'].values
    years = df['date'].dt.year.values

    lag_basis = natural_cubic_spline_basis(np.arange(MAX_LAG), df=LAG_DF)
    Xp = build_lag_matrix(P, MAX_LAG, lag_basis)
    Xv = build_lag_matrix(VPD, MAX_LAG, lag_basis)
    Xs = build_lag_matrix(SM, MAX_LAG, lag_basis)
    years_aligned = years[MAX_LAG - 1:]

    # Get window centers and theta
    dec_grp = dec_grp.sort_values('center_year').reset_index(drop=True)
    centers = dec_grp['center_year'].values
    theta = dec_grp[SPLINE_COLS].values  # (n_windows, 12)

    # Decompose each spline coefficient into composition + residual
    feat = dec_grp[FEAT_COLS].values
    mu = feat.mean(axis=0)
    sd = feat.std(axis=0); sd[sd < 1e-12] = 1.0
    feat_s = (feat - mu) / sd
    X_is = np.column_stack([np.ones(len(feat_s)), feat_s])
    theta_comp = np.zeros_like(theta)
    for j in range(theta.shape[1]):
        coef, *_ = lstsq(X_is, theta[:, j], rcond=None)
        fitted = X_is @ coef
        theta_comp[:, j] = fitted - fitted[0]  # centered

    # For each year, find nearest window theta
    year_min, year_max = int(years_aligned.min()), int(years_aligned.max())
    year_list = list(range(year_min, year_max + 1))

    def nearest_theta(year):
        idx = np.argmin(np.abs(centers - year))
        return theta[idx], theta_comp[idx]

    # Reconstruct daily Q for each scenario using year-specific theta
    n = len(years_aligned)
    Q_fact = np.zeros(n)
    Q_A = np.zeros(n)
    Q_B = np.zeros(n)
    theta_first = theta[0]
    for y in year_list:
        mask = years_aligned == y
        if not mask.any():
            continue
        th_t, th_comp = nearest_theta(y)
        thA = theta_first
        thB = theta_first + th_comp  # first + composition drift
        # projected predictors for the year's days
        Xp_y = Xp[mask]; Xv_y = Xv[mask]; Xs_y = Xs[mask]
        # Q = X_projected @ theta_spline (not X @ lag_curve!)
        Q_fact[mask] = Xp_y @ th_t[0:4] + Xv_y @ th_t[4:8] + Xs_y @ th_t[8:12]
        Q_A[mask] = Xp_y @ thA[0:4] + Xv_y @ thA[4:8] + Xs_y @ thA[8:12]
        Q_B[mask] = Xp_y @ thB[0:4] + Xv_y @ thB[4:8] + Xs_y @ thB[8:12]

    # Annual runoff anomalies (sum of daily anomalies)
    df_aligned = pd.DataFrame({'year': years_aligned, 'Q_fact': Q_fact, 'Q_A': Q_A, 'Q_B': Q_B})
    annual = df_aligned.groupby('year').agg(
        Q_fact=('Q_fact', 'sum'),
        Q_A=('Q_A', 'sum'),
        Q_B=('Q_B', 'sum'),
    ).reset_index()

    # Theil-Sen trends
    trend_fact = theil_sen_slope(annual['Q_fact'].values)
    trend_A = theil_sen_slope(annual['Q_A'].values)
    trend_B = theil_sen_slope(annual['Q_B'].values)

    return {
        'station_id': str(station_id),
        'trend_factual': trend_fact,
        'trend_stable_A': trend_A,
        'trend_composition_B': trend_B,
        'bias_A': trend_fact - trend_A,
        'bias_B': trend_fact - trend_B,
        'n_years': len(annual),
    }

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"), dtype={'station_id': str})
    dec['station_id'] = dec['station_id'].astype(str)

    results = []
    n = dec['station_id'].nunique()
    for i, (sid, grp) in enumerate(dec.groupby('station_id')):
        if i % 100 == 0:
            print(f"Counterfactual {i}/{n}...")
        try:
            res = process_catchment(sid, grp)
            results.append(res)
        except Exception as e:
            print(f"  Error {sid}: {e}")

    cf = pd.DataFrame(results)
    # Merge with drift table for sign-consistency analysis
    drift = pd.read_csv(os.path.join(DATA_DIR, "catchment_drift.csv"), dtype={'station_id': str})
    drift['station_id'] = drift['station_id'].astype(str)
    cf = cf.merge(drift[['station_id', 'beta_P_drift', 'M75_P_drift',
                          'aridity_index', 'snow_fraction', 'baseflow_index']],
                  on='station_id', how='left')
    cf.to_csv(os.path.join(DATA_DIR, "counterfactual_results.csv"), index=False)

    # Sign consistency: group by residual drift sign
    print("\nAttribution bias (factual - stable response) summary:")
    print(cf['bias_A'].describe())
    # Sign consistency test
    for drv in ['beta_P_drift', 'M75_P_drift']:
        for sign_label, sign_val in [('positive', 1), ('negative', -1)]:
            sub = cf[np.sign(cf[drv]) == sign_val]
            if len(sub) < 10:
                continue
            rate = np.mean(np.sign(sub) > 0)
            res = stats.binomtest(int((np.sign(sub) > 0).sum()), len(sub), 0.5)
            pval = res.pvalue
            print(f"  {drv} {sign_label} drift: bias_A positive rate = {rate:.3f} (n={len(sub)}, p={pval:.4f})")

    print("\nCounterfactual analysis complete.")

if __name__ == "__main__":
    main()
