import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.ops import linemerge

# Reload transects with coordinates
shorelines = gpd.read_file("/Users/tsukki/Downloads/files/GEE_Brahmapur/all_shorelines.shp")
shorelines = shorelines.to_crs("EPSG:32645")

baseline = shorelines[shorelines['Year'] == 2013].geometry.values[0]
if baseline.geom_type == 'MultiLineString':
    baseline = linemerge(baseline)

distances = np.arange(0, baseline.length, 250)
coords = []
for i, d in enumerate(distances):
    pt = baseline.interpolate(d)
    # Convert back to WGS84
    pt_gdf = gpd.GeoDataFrame(geometry=[pt], crs="EPSG:32645").to_crs("EPSG:4326")
    coords.append({
        'TransectID': i,
        'Longitude': round(pt_gdf.geometry.x[0], 6),
        'Latitude': round(pt_gdf.geometry.y[0], 6)
    })

coords_df = pd.DataFrame(coords)

# Merge with DSAS results
dsas_df = pd.read_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/dsas_results.csv")
final = dsas_df.merge(coords_df, on='TransectID')

final.to_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/dsas_results_with_coords.csv", index=False)
print(f"Done: {len(final)} transects with coordinates")
print(final[['TransectID','Longitude','Latitude','EPR_m_yr','NSM_m','R2']].head())