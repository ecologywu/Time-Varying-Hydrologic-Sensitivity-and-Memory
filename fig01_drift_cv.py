"""
Figure 1: Parameter drift variability (CV) vs aridity index and snow fraction.
Three panels (beta_P, beta_VPD, M75_P), points colored by climate zone,
LOWESS smooth with 95% bootstrap confidence band.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
FIG_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\figures"
os.makedirs(FIG_DIR, exist_ok=True)

# WRR-style aesthetics
mpl.rcParams.update({
    'font.family': 'Arial', 'font.size': 9,
    'axes.linewidth': 0.8, 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

def climate_zone(row):
    """Koppen-inspired coarse classification from aridity and snow fraction."""
    ai = row['aridity_index']
    sf = row['snow_fraction']
    if ai > 3: return 'Arid'
    if ai > 1.5: return 'Semi-arid'
    if sf > 0.3: return 'Snow-influenced'
    if ai < 0.7: return 'Humid'
    return 'Sub-humid'

def lowess(x, y, frac=0.3):
    from statsmodels.nonparametric.smoothers_lowess import lowess as _lowess
    mask = ~np.isnan(x) & ~np.isnan(y)
    if mask.sum() < 10:
        return np.array([]), np.array([])
    res = _lowess(y[mask], x[mask], frac=frac, it=0)
    return res[:, 0], res[:, 1]

def bootstrap_lowess_band(x, y, n_boot=200, frac=0.3):
    mask = ~np.isnan(x) & ~np.isnan(y)
    xs, ys = x[mask], y[mask]
    order = np.argsort(xs)
    xs_s = xs[order]
    preds = []
    n = len(xs)
    for _ in range(n_boot):
        idx = np.random.choice(n, n, replace=True)
        try:
            xb, yb = lowess(xs[idx], ys[idx], frac=frac)
            pred = np.interp(xs_s, xb, yb)
            preds.append(pred)
        except Exception:
            continue
    if not preds:
        return xs_s, np.zeros(len(xs_s)), np.zeros(len(xs_s))
    preds = np.array(preds)
    lo = np.percentile(preds, 2.5, axis=0)
    hi = np.percentile(preds, 97.5, axis=0)
    return xs_s, lo, hi

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"))
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    dec['station_id'] = dec['station_id'].astype(str)
    attrs['station_id'] = attrs['station_id'].astype(str)

    # Compute CV of each parameter across windows per catchment
    cv = dec.groupby('station_id').agg(
        beta_P_cv=('beta_P', lambda x: x.std() / (abs(x.mean()) + 1e-12)),
        beta_VPD_cv=('beta_VPD', lambda x: x.std() / (abs(x.mean()) + 1e-12)),
        M75_P_cv=('M75_P', 'std'),
    ).reset_index()

    cv = cv.merge(attrs[['station_id', 'aridity_index', 'snow_fraction', 'baseflow_index']],
                  on='station_id', how='left')
    cv['climate_zone'] = cv.apply(climate_zone, axis=1)

    # Clip aridity for plotting
    cv['aridity_index_plot'] = cv['aridity_index'].clip(upper=10)

    zone_colors = {
        'Arid': '#d73027', 'Semi-arid': '#fc8d59',
        'Sub-humid': '#fee08b', 'Humid': '#91bfdb',
        'Snow-influenced': '#4575b4',
    }

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    params = [('beta_P_cv', 'Sensitivity $\\beta_P$ (CV)'),
              ('beta_VPD_cv', 'Sensitivity $\\beta_{VPD}$ (CV)'),
              ('M75_P_cv', 'Memory $M_{75,P}$ (std, days)')]

    for i, (ax, (col, ylabel)) in enumerate(zip(axes, params)):
        for zone, color in zone_colors.items():
            sub = cv[cv['climate_zone'] == zone]
            if len(sub) == 0:
                continue
            ax.scatter(sub['aridity_index_plot'], sub[col], s=8, alpha=0.5,
                       color=color, edgecolors='none', label=zone, rasterized=True)
        # LOWESS + band
        xs_s, lo, hi = bootstrap_lowess_band(cv['aridity_index_plot'].values, cv[col].values)
        if len(xs_s) > 0:
            xl, yl = lowess(cv['aridity_index_plot'].values, cv[col].values)
            ax.plot(xl, yl, 'k-', lw=1.5)
            ax.fill_between(xs_s, lo, hi, color='k', alpha=0.15)
        ax.set_xlabel('Aridity index (PET/P)')
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, 10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.text(0.03, 0.96, f'({chr(97 + i)})', transform=ax.transAxes,
                fontsize=11, fontweight='bold', va='top')

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=5, frameon=False,
               fontsize=8, markerscale=2, bbox_to_anchor=(0.5, 1.02),
               columnspacing=1.2, handletextpad=0.4)
    fig.savefig(os.path.join(FIG_DIR, "Figure1_drift_CV_vs_aridity.png"))
    plt.close()
    print("Figure 1 saved.")

if __name__ == "__main__":
    main()
