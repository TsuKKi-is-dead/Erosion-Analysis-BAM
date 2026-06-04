import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

# Load shorelines and reproject to metric CRS (UTM zone 45N for Odisha)
shorelines = gpd.read_file("/Users/tsukki/Downloads/files/GEE_Brahmapur/all_shorelines.shp")
shorelines = shorelines.to_crs("EPSG:32645")

# Build baseline from 2013 shoreline (reference)
baseline = shorelines[shorelines['Year'] == 2013].geometry.values[0]

# Cast to single line if multilinestring
if baseline.geom_type == 'MultiLineString':
    from shapely.ops import linemerge
    baseline = linemerge(baseline)

# Generate transects every 250m along baseline
def make_transects(baseline, spacing=250, length=500):
    transects = []
    distances = np.arange(0, baseline.length, spacing)
    for i, d in enumerate(distances):
        pt = baseline.interpolate(d)
        # Get perpendicular direction
        d2 = min(d + 1, baseline.length)
        pt2 = baseline.interpolate(d2)
        dx = pt2.x - pt.x
        dy = pt2.y - pt.y
        norm = np.sqrt(dx**2 + dy**2)
        if norm == 0:
            continue
        # Perpendicular vector
        px, py = -dy/norm, dx/norm
        p1 = Point(pt.x + px*length, pt.y + py*length)
        p2 = Point(pt.x - px*length, pt.y - py*length)
        transects.append({'TransectID': i, 'geometry': LineString([p1, p2])})
    return gpd.GeoDataFrame(transects, crs="EPSG:32645")

transects = make_transects(baseline, spacing=250, length=500)
print(f"Generated {len(transects)} transects")

# For each transect, find intersection distance with each year's shoreline
years = list(range(2013, 2025))
results = []

for _, t in transects.iterrows():
    row = {'TransectID': t['TransectID']}
    ref_pt = None
    for yr in years:
        sl = shorelines[shorelines['Year'] == yr].geometry.values[0]
        inter = t['geometry'].intersection(sl)
        if inter.is_empty:
            row[str(yr)] = np.nan
        else:
            pt = inter if inter.geom_type == 'Point' else list(inter.geoms)[0]
            if ref_pt is None:
                ref_pt = pt
            row[str(yr)] = ref_pt.distance(pt)
    results.append(row)

df = pd.DataFrame(results)

# Calculate EPR, NSM, LRR per transect
from scipy import stats

dsas_rows = []
for _, row in df.iterrows():
    vals = [(yr, row[str(yr)]) for yr in years if not np.isnan(row[str(yr)])]
    if len(vals) < 4:
        continue
    yrs, dists = zip(*vals)
    slope, intercept, r, p, se = stats.linregress(yrs, dists)
    dsas_rows.append({
        'TransectID': int(row['TransectID']),
        'EPR_m_yr': round(slope, 4),
        'NSM_m': round(dists[-1] - dists[0], 4),
        'LRR_m_yr': round(slope, 4),
        'R2': round(r**2, 4),
        'SCE_m': round(max(dists) - min(dists), 4),
        'p_value': round(p, 4)
    })

dsas_df = pd.DataFrame(dsas_rows)
dsas_df.to_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/dsas_results.csv", index=False)
print(f"Saved {len(dsas_df)} transects")
print(dsas_df.describe())