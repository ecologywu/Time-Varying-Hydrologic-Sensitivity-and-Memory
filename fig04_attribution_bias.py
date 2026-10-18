"""
Figure 4: Attribution bias from ignoring response drift.
(a) Global map of bias_A (factual trend - stable-response trend), point size by magnitude.
(b) Box/violin plots of bias_A grouped by sign of residual drift, with sign-consistency rates.
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy import stats
import map_utils

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"
FIG_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\figures"

mpl.rcParams.update({
    'font.family': 'Arial', 'font.size': 9,
    'axes.linewidth': 0.8, 'axes.labelsize': 10,
    'xtick.labelsize': 8, 'ytick.labelsize': 8,
    'legend.fontsize': 8, 'figure.dpi': 300,
    'savefig.dpi': 300, 'savefig.bbox': 'tight',
})

def main():
    cf = pd.read_csv(os.path.join(DATA_DIR, "counterfactual_results.csv"))
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    cf['station_id'] = cf['station_id'].astype(str)
    attrs['station_id'] = attrs['station_id'].astype(str)
    cf = cf.merge(attrs[['station_id', 'lon', 'lat']], on='station_id', how='left')

    fig, axes = plt.subplots(1, 2, figsize=(12, 5),
                             gridspec_kw={'width_ratios': [1.6, 1]})

    # Panel a: global map of bias_A
    ax1 = axes[0]
    map_utils.draw_base_map(ax1)
    bias = cf['bias_A'].values
    vmax = np.nanpercentile(np.abs(bias), 95)
    sizes = np.clip(np.abs(bias) / (vmax + 1e-9) * 30, 3, 30)
    colors = ['#d73027' if b > 0 else '#4575b4' for b in bias]
    ax1.scatter(cf['lon'], cf['lat'], c=colors, s=sizes, alpha=0.65,
                edgecolors='none', rasterized=True, zorder=3)
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    ax1.set_title('(a) Attribution bias from freezing response function\n(trend$_{factual}$ - trend$_{stable}$, mm yr$^{-2}$)', fontsize=9)
    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#d73027',
               markersize=8, label='Positive bias\n(drift amplifies trend)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#4575b4',
               markersize=8, label='Negative bias\n(drift dampens trend)'),
    ]
    ax1.legend(handles=legend_elements, frameon=False, fontsize=8, loc='lower left')

    # Panel b: box plots by drift sign
    ax2 = axes[1]
    groups = []
    labels = []
    rates = []
    for drv, drv_label in [('beta_P_drift', '$\\beta_P$ drift'),
                           ('M75_P_drift', '$M_{75,P}$ drift')]:
        for sign_label, sign_val in [('Positive', 1), ('Negative', -1)]:
            sub = cf[np.sign(cf[drv]) == sign_val]['bias_A'].dropna()
            if len(sub) >= 10:
                groups.append(sub.values)
                labels.append(f"{drv_label}\n{sign_label} (n={len(sub)})")
                rate = np.mean(np.sign(sub) > 0)
                rates.append(rate)

    bp = ax2.boxplot(groups, labels=labels, patch_artist=True, showfliers=False,
                     medianprops=dict(color='black', lw=1.5))
    for patch, rate in zip(bp['boxes'], rates):
        patch.set_facecolor('#fee08b' if rate > 0.5 else '#d9ef8b')
        patch.set_alpha(0.7)
    ax2.axhline(0, color='gray', ls='--', lw=0.8)
    ax2.set_ylabel('Attribution bias (mm yr$^{-2}$)')
    ax2.set_title('(b) Bias by residual-drift direction', fontsize=9)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    # Annotate sign-consistency rates
    for i, rate in enumerate(rates):
        ax2.text(i + 1, ax2.get_ylim()[1] * 0.9, f"{rate:.0%}",
                 ha='center', fontsize=8, fontweight='bold')

    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "Figure4_attribution_bias.png"))
    plt.close()
    print("Figure 4 saved.")

if __name__ == "__main__":
    main()
