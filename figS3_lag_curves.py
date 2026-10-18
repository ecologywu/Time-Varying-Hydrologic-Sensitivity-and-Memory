"""
Figure S3: Example DLNM lag-response curves for a representative catchment.
Shows how lag coefficients for precipitation evolve across three windows
(early, middle, late), demonstrating time-varying sensitivity and memory.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
FIG_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\figures"

mpl.rcParams.update({
    'font.family': 'Arial', 'font.size': 9,
    'axes.linewidth': 0.8, 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

MAX_LAG = 90

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

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"))
    dec['station_id'] = dec['station_id'].astype(str)
    # Pick a catchment with many windows
    counts = dec.groupby('station_id').size()
    sid = counts.idxmax()
    grp = dec[dec['station_id'] == sid].sort_values('center_year')

    lag_basis = natural_cubic_spline_basis(np.arange(MAX_LAG), df=4)

    # Pick early, middle, late windows
    idx_early = 0
    idx_mid = len(grp) // 2
    idx_late = len(grp) - 1
    windows = [('Early', idx_early, '#4575b4'),
               ('Middle', idx_mid, '#1a9850'),
               ('Late', idx_late, '#d73027')]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    for ax, var, title in [(axes[0], 'P', 'Precipitation'),
                           (axes[1], 'VPD', 'VPD')]:
        for label, idx, color in windows:
            row = grp.iloc[idx]
            if var == 'P':
                th = [row[f'thP{i}'] for i in range(4)]
            else:
                th = [row[f'thV{i}'] for i in range(4)]
            curve = lag_basis @ np.array(th)
            cum = np.cumsum(curve)
            ax.plot(np.arange(MAX_LAG), curve, color=color, lw=1.5,
                    label=f"{label} ({int(row['center_year'])})")
            ax.fill_between(np.arange(MAX_LAG), 0, curve, color=color, alpha=0.1)
        ax.axhline(0, color='gray', lw=0.5)
        ax.set_xlabel('Lag (days)')
        ax.set_ylabel(f'Lag coefficient ({title})')
        ax.set_title(f'{title} lag-response')
        ax.legend(frameon=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    fig.suptitle(f'Figure S3. Time-varying lag-response curves (catchment {sid})', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "FigureS3_lag_curves.png"))
    plt.close()
    print("Figure S3 saved.")

if __name__ == "__main__":
    main()
