import requests
# We'll pull from Open-Meteo's ERA5 archive — free, no account needed
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 19.2,
    "longitude": 84.8,
    "start_date": "2013-01-01",
    "end_date": "2024-12-31",
    "daily": "precipitation_sum",
    "timezone": "Asia/Kolkata"
}
response = requests.get(url, params=params)
data = response.json()
print(data.keys())

import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 19.2,
    "longitude": 84.8,
    "start_date": "2013-01-01",
    "end_date": "2024-12-31",
    "daily": "precipitation_sum",
    "timezone": "Asia/Kolkata"
}
response = requests.get(url, params=params)
data = response.json()

df = pd.DataFrame({
    "Date": pd.to_datetime(data["daily"]["time"]),
    "Rainfall_mm": data["daily"]["precipitation_sum"]
})

df["Year"] = df["Date"].dt.year
annual = df.groupby("Year")["Rainfall_mm"].sum().reset_index()
annual.columns = ["Year", "Rainfall_mm"]
annual["Rainfall_mm"] = annual["Rainfall_mm"].round(1)

print(annual)
annual.to_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/annual_rainfall.csv", index=False)
print("Saved")