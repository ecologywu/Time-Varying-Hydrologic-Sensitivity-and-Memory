"""
Figure 2: Residual drift fraction vs aridity index and snow fraction.
Panel a: residual fraction vs aridity. Panel b: residual fraction vs snow fraction.
Quantile regression lines (10th/50th/90th) for each parameter.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import statsmodels.formula.api as smf

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
FIG_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\figures"

mpl.rcParams.update({
    'font.family': 'Arial', 'font.size': 9,
    'axes.linewidth': 0.8, 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

PARAMS = [('beta_P', '$\\beta_P$'), ('beta_VPD', '$\\beta_{VPD}$'),
          ('M75_P', '$M_{75,P}$'), ('M75_VPD', '$M_{75,VPD}$')]
COLORS = ['#d73027', '#fc8d59', '#4575b4', '#91bfdb']

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"))
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    dec['station_id'] = dec['station_id'].astype(str)
    attrs['station_id'] = attrs['station_id'].astype(str)

    # Residual fraction per catchment = std(residual) / (std(residual) + std(composition))
    frac = dec.groupby('station_id').agg(
        **{p + '_resid_std': (p + '_resid', 'std') for p, _ in PARAMS},
        **{p + '_comp_std': (p + '_comp', 'std') for p, _ in PARAMS},
    ).reset_index()
    for p, _ in PARAMS:
        tot = frac[p + '_resid_std'] + frac[p + '_comp_std']
        frac[p + '_frac'] = frac[p + '_resid_std'] / tot.replace(0, np.nan)

    frac = frac.merge(attrs[['station_id', 'aridity_index', 'snow_fraction']],
                      on='station_id', how='left')
    frac['aridity_plot'] = frac['aridity_index'].clip(upper=10)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    for i, (ax, xcol, xlabel) in enumerate([(axes[0], 'aridity_plot', 'Aridity index (PET/P)'),
                                            (axes[1], 'snow_fraction', 'Snow fraction')]):
        for (p, label), color in zip(PARAMS, COLORS):
            col = p + '_frac'
            sub = frac[[xcol, col]].dropna()
            if len(sub) < 20:
                continue
            ax.scatter(sub[xcol], sub[col], s=6, alpha=0.3, color=color,
                       edgecolors='none', label=label, rasterized=True)
            # Quantile regression lines 10/50/90
            try:
                for q, ls in [(0.1, ':'), (0.5, '-'), (0.9, ':')]:
                    model = smf.quantreg(f'{col} ~ {xcol}', data=sub)
                    res = model.fit(q=q, max_iter=500)
                    xs = np.linspace(sub[xcol].min(), sub[xcol].max(), 100)
                    ys = res.params['Intercept'] + res.params[xcol] * xs
                    ax.plot(xs, ys, color=color, ls=ls, lw=1.2, alpha=0.8)
            except Exception:
                pass
        ax.axhline(0.5, color='gray', ls='--', lw=0.7, alpha=0.5)
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Residual drift fraction')
        ax.set_ylim(-0.05, 1.05)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.text(0.03, 0.96, f'({chr(97 + i)})', transform=ax.transAxes,
                fontsize=11, fontweight='bold', va='top')

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=4, frameon=False,
               fontsize=8, markerscale=2, bbox_to_anchor=(0.5, 1.02),
               columnspacing=1.2, handletextpad=0.4)
    fig.savefig(os.path.join(FIG_DIR, "Figure2_residual_fraction.png"))
    plt.close()
    print("Figure 2 saved.")

if __name__ == "__main__":
    main()
