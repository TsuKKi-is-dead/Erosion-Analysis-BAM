import pandas as pd

cyclone_data = {
    "Year": [2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024],
    "Storm_Days": [8, 2, 1, 2, 1, 5, 3, 4, 2, 1, 6, 2],
    "Cyclone_Intensity": [3, 1, 0, 1, 0, 3, 2, 2, 1, 0, 3, 1]
}

df_cyclone = pd.DataFrame(cyclone_data)
df_rain    = pd.read_csv("/Users/tsukki/Downloads/GEE_Brahmapur/annual_rainfall.csv")
df_wave    = pd.read_csv("/Users/tsukki/Downloads/GEE_Brahmapur/annual_waves.csv")[["Year","Sig_Wave_Height_m"]]
df_epr     = pd.read_csv("/Users/tsukki/Downloads/GEE_Brahmapur/annual_epr.csv")   # real EPR
df_indices = pd.read_csv("/Users/tsukki/Downloads/GEE_Brahmapur/index_timeseries_12yr.csv")
df_indices.columns = [c.strip() for c in df_indices.columns]

df_climate = df_rain.merge(df_wave, on="Year")
df_climate = df_climate.merge(df_cyclone, on="Year")
df_climate = df_climate.merge(df_epr, on="Year")   # real EPR replaces BSI-mapped
df_climate["Mean_NDVI"]    = df_indices["NDVI"].values
df_climate["Mean_BSI"]     = df_indices["BSI"].values

print(df_climate.to_string(index=False))
df_climate.to_csv("/Users/tsukki/Downloads/GEE_Brahmapur/climate_combined.csv", index=False)
print("Saved")