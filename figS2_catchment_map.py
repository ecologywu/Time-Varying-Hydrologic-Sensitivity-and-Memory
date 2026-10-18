"""
Figure S2: Global map of catchment locations colored by climate zone.
Base map: country outlines, lakes, and major rivers (WorldMap_Shpfiles).
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
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

def climate_zone(row):
    ai = row['aridity_index']; sf = row['snow_fraction']
    if ai > 3: return 'Arid'
    if ai > 1.5: return 'Semi-arid'
    if sf > 0.3: return 'Snow-influenced'
    if ai < 0.7: return 'Humid'
    return 'Sub-humid'

def main():
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    attrs['climate_zone'] = attrs.apply(climate_zone, axis=1)

    zone_colors = {'Arid': '#d73027', 'Semi-arid': '#fc8d59',
                   'Sub-humid': '#fee08b', 'Humid': '#91bfdb',
                   'Snow-influenced': '#4575b4'}

    fig, ax = plt.subplots(1, 1, figsize=(11, 5.5))
    map_utils.draw_base_map(ax)
    for zone, color in zone_colors.items():
        sub = attrs[attrs['climate_zone'] == zone]
        ax.scatter(sub['lon'], sub['lat'], s=14, color=color, edgecolors='none',
                   alpha=0.75, label=f"{zone} (n={len(sub)})", rasterized=True,
                   zorder=3)
    ax.legend(frameon=False, fontsize=8.5, loc='upper center',
              bbox_to_anchor=(0.5, -0.12), ncol=3, columnspacing=1.0,
              handletextpad=0.3)
    fig.savefig(os.path.join(FIG_DIR, "FigureS2_catchment_map.png"))
    plt.close()
    print("Figure S2 saved.")

if __name__ == "__main__":
    main()
