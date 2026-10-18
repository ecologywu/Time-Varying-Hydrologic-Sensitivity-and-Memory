"""
Shared utility for drawing WGS84 global base maps in matplotlib using pyshp.
Uses: Countries.shp (land polygons), Lakes.shp, Rivers.shp from the
WorldMap_Shpfiles database (Natural Earth-derived, EPSG:4326).
"""
import os
import shapefile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection

SHP_DIR = r"D:\Software_Data\ArcMAP\基础地理信息数据库\WorldMap_Shpfiles"

_reader_cache = {}

def _get_reader(name):
    if name not in _reader_cache:
        _reader_cache[name] = shapefile.Reader(os.path.join(SHP_DIR, name))
    return _reader_cache[name]

def _shapes_to_patches(shp_path, **kwargs):
    """Convert a polygon shapefile to a matplotlib PatchCollection."""
    r = _get_reader(shp_path)
    patches = []
    for shp in r.shapes():
        parts = list(shp.parts) + [len(shp.points)]
        for i in range(len(parts) - 1):
            pts = shp.points[parts[i]:parts[i + 1]]
            if len(pts) < 3:
                continue
            arr = np.asarray(pts)
            # Skip antimeridian-crossing rings (crude span check)
            if arr[:, 0].max() - arr[:, 0].min() > 350:
                continue
            patches.append(MplPolygon(arr, closed=True))
    return PatchCollection(patches, match_original=False, **kwargs)

def _shapes_to_lines(shp_path, **kwargs):
    """Convert a polyline shapefile to a matplotlib LineCollection."""
    from matplotlib.collections import LineCollection
    r = _get_reader(shp_path)
    segments = []
    for shp in r.shapes():
        parts = list(shp.parts) + [len(shp.points)]
        for i in range(len(parts) - 1):
            pts = shp.points[parts[i]:parts[i + 1]]
            if len(pts) < 2:
                continue
            arr = np.asarray(pts)
            if arr[:, 0].max() - arr[:, 0].min() > 350:
                continue
            segments.append(arr)
    return LineCollection(segments, **kwargs)

def draw_base_map(ax, rivers=True, lakes=True, land_color='#E8E8E6',
                  land_edge='#B0B0B0', zbase=0.5):
    """Draw country outlines, lakes, and major rivers on a WGS84 axes."""
    land = _shapes_to_patches('Countries.shp', facecolor=land_color,
                              edgecolor=land_edge, linewidth=0.3, zorder=zbase)
    ax.add_collection(land)
    if lakes:
        lk = _shapes_to_patches('Lakes.shp', facecolor='white',
                                edgecolor='none', zorder=zbase + 0.5)
        ax.add_collection(lk)
    if rivers:
        rv = _shapes_to_lines('Rivers.shp', colors='#6BAED6', linewidths=0.35,
                              alpha=0.8, zorder=zbase + 0.75)
        ax.add_collection(rv)
    ax.set_facecolor('white')
    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 80)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xticks(np.arange(-180, 181, 60))
    ax.set_yticks(np.arange(-60, 81, 30))
    ax.tick_params(length=2, width=0.6)
    for s in ax.spines.values():
        s.set_linewidth(0.8)
