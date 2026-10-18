"""
Figure S4: Parameter time series for representative catchments across climate zones.
Shows beta_P, beta_VPD, M75_P with composition (dashed) and residual (shaded) components.
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

def climate_zone(row):
    ai = row['aridity_index']; sf = row['snow_fraction']
    if ai > 3: return 'Arid'
    if ai > 1.5: return 'Semi-arid'
    if sf > 0.3: return 'Snow-influenced'
    if ai < 0.7: return 'Humid'
    return 'Sub-humid'

def main():
    dec = pd.read_csv(os.path.join(DATA_DIR, "decomposed_params.csv"))
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    dec['station_id'] = dec['station_id'].astype(str)
    attrs['station_id'] = attrs['station_id'].astype(str)
    attrs['climate_zone'] = attrs.apply(climate_zone, axis=1)
    dec = dec.merge(attrs[['station_id', 'climate_zone']], on='station_id', how='left')

    # Pick one representative catchment per zone (most windows)
    reps = []
    for zone in ['Arid', 'Semi-arid', 'Sub-humid', 'Humid', 'Snow-influenced']:
        sub = dec[dec['climate_zone'] == zone]
        if len(sub) == 0:
            continue
        sid = sub.groupby('station_id').size().idxmax()
        reps.append((zone, sid))

    fig, axes = plt.subplots(len(reps), 3, figsize=(13, 3 * len(reps)), sharex=True)
    if len(reps) == 1:
        axes = axes[np.newaxis, :]

    params = [('beta_P', '$\\beta_P$'), ('beta_VPD', '$\\beta_{VPD}$'), ('M75_P', '$M_{75,P}$')]
    for r, (zone, sid) in enumerate(reps):
        grp = dec[dec['station_id'] == sid].sort_values('center_year')
        for c, (p, label) in enumerate(params):
            ax = axes[r, c]
            x = grp['center_year'].values
            actual = grp[p].values
            comp = grp[p + '_comp'].values
            resid = grp[p + '_resid'].values
            ax.plot(x, actual, 'k-', lw=1.5, label='Actual')
            ax.plot(x, comp, 'r--', lw=1.2, label='Composition')
            ax.fill_between(x, comp, actual, alpha=0.3, color='orange', label='Residual drift')
            ax.set_title(f'{label} ({zone})', fontsize=9)
            if c == 0:
                ax.set_ylabel(f'Catchment {sid}\n{label}')
            if r == len(reps) - 1:
                ax.set_xlabel('Window center year')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            if r == 0 and c == 0:
                ax.legend(frameon=False, fontsize=7)

    fig.suptitle('Figure S4. Decomposition of response-parameter time series into composition and residual drift', fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "FigureS4_parameter_timeseries.png"))
    plt.close()
    print("Figure S4 saved.")

if __name__ == "__main__":
    main()
