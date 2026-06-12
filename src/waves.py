import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 19.2,
    "longitude": 84.8,
    "start_date": "2013-01-01",
    "end_date": "2024-12-31",
    "daily": "wind_speed_10m_max",
    "timezone": "Asia/Kolkata"
}
response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame({
    "Date": pd.to_datetime(data["daily"]["time"]),
    "Wind_ms": data["daily"]["wind_speed_10m_max"]
})

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
seasonal = df[df["Month"].isin([11, 12, 1, 2])]
annual_wind = seasonal.groupby("Year")["Wind_ms"].mean().reset_index()

# Approximate Hs from wind speed using empirical relation Hs ≈ 0.0248 * U^1.5
# (simplified fetch-limited formula, cite CERC Shore Protection Manual)
annual_wind["Sig_Wave_Height_m"] = (0.0248 * annual_wind["Wind_ms"]**1.5).round(3)

print(annual_wind[["Year","Wind_ms","Sig_Wave_Height_m"]])
annual_wind.to_csv("/Users/tsukki/Downloads/GEE_Brahmapur/annual_waves.csv", index=False)
print("Saved")