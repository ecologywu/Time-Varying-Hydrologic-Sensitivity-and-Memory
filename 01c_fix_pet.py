"""Update PET column in all saved daily files with corrected Hamon formula."""
import os
import numpy as np
import pandas as pd

DATA_DIR = r"C:\Users\dell\Documents\Trae-CN\temp_20261018_01\data"

def daylight_hours(lat, doy):
    phi = np.deg2rad(lat)
    delta = np.deg2rad(23.45 * np.sin(2 * np.pi * (284 + doy) / 365.0))
    cos_h = np.clip(-np.tan(phi) * np.tan(delta), -1.0, 1.0)
    return 24.0 / np.pi * np.arccos(cos_h)

def main():
    attrs = pd.read_csv(os.path.join(DATA_DIR, "catchment_attributes.csv"))
    attrs['station_id'] = attrs['station_id'].astype(str)
    lat_map = dict(zip(attrs['station_id'], attrs['lat']))
    daily_dir = os.path.join(DATA_DIR, "daily")
    files = [f for f in os.listdir(daily_dir) if f.endswith('.csv.gz')]
    for i, f in enumerate(files):
        if i % 300 == 0:
            print(f"Updating PET {i}/{len(files)}...")
        sid = f.replace('.csv.gz', '')
        lat = lat_map.get(sid)
        if lat is None:
            continue
        fpath = os.path.join(daily_dir, f)
        df = pd.read_csv(fpath, parse_dates=['date'])
        doy = df['date'].dt.dayofyear.values
        N = daylight_hours(lat, doy)
        svp_mb = df['svp_kPa'].values * 10.0
        t = df['t2m_mean_C'].values
        df['PET'] = 0.1651 * (N / 12.0) * svp_mb * 216.7 / (t + 273.3)
        df['PET'] = df['PET'].clip(lower=0)
        df.to_csv(fpath, index=False, compression='gzip')
    print("PET update complete.")

if __name__ == "__main__":
    main()
