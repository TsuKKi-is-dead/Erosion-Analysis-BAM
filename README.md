# Brahmapur Coastline Erosion Analysis (2013–2024)

### A Multi-Temporal Remote Sensing Study of the Ganjam Coast, Odisha, India

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Google%20Earth%20Engine-green)](https://earthengine.google.com/)

---

## Overview

This repository contains the complete analysis pipeline for a 12-year (2013–2024) multi-temporal shoreline change and coastal erosion study of the Brahmapur coastline, Ganjam district, Odisha, India. The study area is centered around Gopalpur port (AOI: 84.68°E–84.92°E, 19.05°N–19.42°N).

The analysis integrates satellite remote sensing, digital shoreline analysis, spectral index time series, land cover validation, erosion hotspot classification, and climate driver correlation — forming a complete publishable research pipeline.

---

## Study Area

| Parameter        | Value                                        |
| ---------------- | -------------------------------------------- |
| Location         | Brahmapur (Berhampur), Ganjam, Odisha, India |
| AOI Bounding Box | [84.68, 19.05, 84.92, 19.42]                 |
| Coastline Length | ~37 km                                       |
| Study Period     | 2013–2024 (12 years)                         |
| Focal Feature    | Gopalpur port and downdrift accretion zone   |

---

## Key Findings

- **819 shore-normal transects** analysed at 250 m spacing using Python DSAS
- Mean shoreline change rate (LRR): **+10.70 m/yr** (net accretion dominates)
- Maximum erosion: **−42.91 m/yr** at transect 241 (~19.107°N)
- Maximum accretion: **+66.78 m/yr** near Gopalpur port downdrift zone
- **18.4% of coastline** under net erosion; 2 Critical + 3 High risk transects identified
- BSI showed a statistically significant declining trend (p = 0.034) over 2013–2024
- Land cover classification accuracy: **81.7% (Kappa = 0.723)** using real MNDWI pixel values
- Significant wave height is the strongest erosion driver (r = −0.617, p = 0.033)
- Cyclone Michaung (2023) flagged as anomaly year in spectral index trends

---

## Repository Structure

```
Erosion-Analysis-BAM/
│
├── brahmapur_coastal_erosion_analysis.ipynb   # Main analysis notebook (all 5 modules)
│
├── GEE_Brahmapur/                             # Core data directory
│   ├── shoreline_2013.shp → shoreline_2024.shp  # Annual shoreline shapefiles (UTM 32645)
│   ├── all_shorelines.shp                     # Merged multi-year shoreline
│   ├── dsas_results.csv                       # Raw DSAS transect output
│   ├── dsas_results_with_coords.csv           # DSAS with lat/lon
│   ├── dsas_transects_classified.csv          # Classified transects (EPR/LRR/NSM/SCE)
│   ├── index_timeseries_12yr.csv              # Annual spectral indices 2013–2024
│   ├── climate_combined.csv                   # ERA5 rainfall + wave + cyclone data
│   ├── annual_rainfall.csv                    # ERA5 annual rainfall (Open-Meteo)
│   ├── annual_waves.csv                       # ERA5 wind-derived wave height
│   ├── validation_final.csv                   # 180-point validated ground truth
│   ├── validation_for_gee.csv                 # Clean CSV used for GEE asset upload
│   ├── mndwi_sampled1.csv                     # Real MNDWI values sampled at 180 points
│   └── yearly_epr.csv                         # BSI-derived annual EPR proxy
│
├── outputs/                                   # All figures and result tables
│   ├── 1_shoreline_change_stats.png           # EPR/LRR transect bar chart
│   ├── 3_confusion_matrix.png                 # Land cover validation matrix
│   ├── 4_erosion_hotspot_classification.png   # Spatial risk map
│   ├── 5a_correlation_scatter.png             # Climate vs EPR scatter plots
│   ├── 5b_correlation_matrix.png              # Full variable correlation heatmap
│   ├── spectral_index_timeseries.png          # NDWI/MNDWI/NDVI/BSI trends
│   ├── accuracy_assessment.csv                # PA/UA per class
│   ├── correlation_results.csv                # Pearson r and p-values
│   ├── dsas_summary_statistics.csv            # Mean/min/max EPR/NSM/LRR/SCE
│   ├── erosion_hotspot_table.csv              # Risk score per transect
│   ├── index_trend_statistics.csv             # Slope/R²/p per spectral index
│   ├── spectral_index_timeseries.csv          # Annual mean index values
│   ├── summary_results_table.csv              # Master results summary for paper
│   └── validation_points.csv                 # 180 points with MNDWI + True/Predicted class
│
├── src/                                       # Standalone Python version of the pipeline
|    |
├   |── MNDWI.py                                   # MNDWI classification and accuracy script
├   |── EPR.py                                     # Yearly EPR computation script
├   |── cyclone.py                                 # Climate data assembly script
├   |── rain.py                                    # ERA5 rainfall download script
├   |── waves.py                                   # ERA5 wave height download script
├   |── split.py                                   # Utility: lat/lon extraction from .geo column
|
│---brahmapur_coastal_erosion_analysis.ipynb
├── requirements.txt                           # Python dependencies with versions
└── README.md                                  # This file
```

---

## Modules

### Module 1 — Shoreline Change Analysis (Python DSAS)

- Extracts annual shorelines from GEE (Landsat 8: 2013–2016, Sentinel-2: 2017–2024)
- Applies JRC permanent water mask; Nov–Feb dry season composites
- Computes EPR, NSM, LRR, R², SCE across 819 transects (250 m spacing, UTM 32645, 2013 baseline)

### Module 2 — Spectral Index Time Series

- Computes NDWI, MNDWI, NDVI, BSI annually for the AOI
- Linear regression + Mann-Kendall trend test
- BSI significant (p = 0.034); 2023 flagged as Cyclone Michaung anomaly

### Module 3 — Land Cover Validation

- 180 stratified random points (60 per class: Water / Intertidal / Land)
- Ground truth manually verified in Google Earth Pro (Dec 2020 imagery)
- Real MNDWI pixel values extracted from GEE Sentinel-2 composite
- **Overall Accuracy: 81.7%, Cohen's Kappa: 0.723**

### Module 4 — Erosion Hotspot Classification

- Composite risk score from LRR, NDVI decline, BSI exposure
- Four risk levels: Low / Moderate / High / Critical
- 2 Critical transects (~19.107°N and ~19.133°N); 3 High risk transects

### Module 5 — Climate Driver Correlation

- Annual ERA5 rainfall and wind-derived wave height (Open-Meteo API)
- RSMC cyclone records: Phailin (2013), Titli (2018), Amphan (2020), Michaung (2023)
- Pearson correlation of climate variables vs mean shoreline change rate
- **Significant result: wave height r = −0.617, p = 0.033**

---

## Data Sources

| Dataset                  | Source                              | Period         | Resolution  |
| ------------------------ | ----------------------------------- | -------------- | ----------- |
| Landsat 8 SR             | USGS via Google Earth Engine        | 2013–2016      | 30 m        |
| Sentinel-2 SR Harmonized | ESA via Google Earth Engine         | 2017–2024      | 10 m        |
| JRC Global Surface Water | EC JRC via GEE                      | Permanent mask | 30 m        |
| Annual Rainfall          | ERA5 via Open-Meteo archive API     | 2013–2024      | ~25 km      |
| Significant Wave Height  | ERA5/Open-Meteo marine API          | 2021–2024      | ~25 km      |
| Wind Speed (wave proxy)  | ERA5 via Open-Meteo                 | 2013–2020      | ~25 km      |
| Cyclone Records          | RSMC New Delhi / IMD                | 2013–2024      | Event-based |
| Ground Truth             | Google Earth Pro (Dec 2020 imagery) | 2020           | Visual      |

---

## Setup and Usage

### 1. Clone the repository

```bash
git clone https://github.com/TsuKKi-is-dead/Erosion-Analysis-BAM.git
cd Erosion-Analysis-BAM
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the notebook

```bash
jupyter notebook brahmapur_coastal_erosion_analysis.ipynb
```

Run all cells in order. Modules 1–5 are sequential — each builds on the previous output.

### Google Earth Engine Access

Modules 1, 2, and 3 (ground truth extraction) require a GEE account. Register free at [earthengine.google.com](https://earthengine.google.com). The Python analysis (Modules 3 accuracy onwards, 4, 5) runs entirely locally without GEE.

---

## Results Summary

| Metric                         | Value                    |
| ------------------------------ | ------------------------ |
| Total transects analysed       | 783                      |
| Mean LRR                       | +10.70 m/yr              |
| Max erosion rate               | −42.91 m/yr              |
| Max accretion rate             | +66.78 m/yr              |
| % coastline under net erosion  | 18.4%                    |
| Critical + High risk transects | 0.6% of coast            |
| NDVI change 2019–2024          | −0.036                   |
| BSI trend significance         | p = 0.034 ✅             |
| Classification accuracy (OA)   | 81.7%                    |
| Cohen's Kappa (κ)              | 0.723                    |
| Strongest erosion driver       | Significant wave height  |
| Wave height correlation        | r = −0.617, p = 0.033 ✅ |

---

## Citation

If you use this code or data in your research, please cite:

```
[Author Name(s)], [Year]. Multi-temporal shoreline change and erosion hotspot
analysis of the Brahmapur coastline, Ganjam, Odisha (2013–2024).
GitHub: https://github.com/TsuKKi-is-dead/Erosion-Analysis-BAM
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- Google Earth Engine for satellite data access
- Open-Meteo for ERA5 climate data API
- RSMC New Delhi / IMD for cyclone track records
- Copernicus/ESA for Sentinel-2 data
- USGS for Landsat 8 data
