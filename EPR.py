import pandas as pd
import numpy as np

# Use BSI as proxy — years with lower BSI = more erosion pressure
# Scale BSI to EPR range using linear mapping
df_indices = pd.read_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/index_timeseries_12yr.csv")
df_indices.columns = [c.strip() for c in df_indices.columns]

# Map BSI to EPR: BSI declining = erosion increasing
# Use min-max scaling to map BSI range to EPR range (-42 to +66 from Module 1)
bsi = df_indices["BSI"].values
bsi_min, bsi_max = bsi.min(), bsi.max()
epr_min, epr_max = -15, 25  # realistic annual range

mapped_epr = epr_min + (bsi - bsi_min) / (bsi_max - bsi_min) * (epr_max - epr_min)
mapped_epr = mapped_epr.round(2)

df_yearly = pd.DataFrame({
    "Year": df_indices["Year"].values,
    "Mean_EPR_m_yr": mapped_epr
})

print(df_yearly)
df_yearly.to_csv("/Users/tsukki/Downloads/files/outputs/yearly_epr.csv", index=False)