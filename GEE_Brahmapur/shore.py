import geopandas as gpd
import os
from shapely.ops import unary_union

data_folder = "/Users/tsukki/Downloads/files/GEE_Brahmapur"
all_shorelines = []

for yr in range(2013, 2025):
    path = os.path.join(data_folder, f"shoreline_{yr}.shp")
    gdf = gpd.read_file(path)
    
    # Keep only large polygons (removes noise/tiny water patches)
    gdf = gdf[gdf.geometry.area > 0.00001].copy()
    
    # Dissolve all water polygons into one shape, then get the boundary = shoreline
    dissolved = unary_union(gdf.geometry)
    shoreline = dissolved.boundary
    
    all_shorelines.append({
        'Year': yr,
        'Date': f"{yr}-12-01",  # mid-composite date
        'geometry': shoreline
    })
    print(f"{yr}: done")

shoreline_gdf = gpd.GeoDataFrame(all_shorelines, crs="EPSG:4326")
shoreline_gdf.to_file("/Users/tsukki/Downloads/files/GEE_Brahmapur/all_shorelines.shp")
print("Saved: /Users/tsukki/Downloads/files/GEE_Brahmapur/all_shorelines.shp")