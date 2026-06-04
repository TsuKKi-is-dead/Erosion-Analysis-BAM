"""
=============================================================================
  Brahmapur Coastline Erosion Analysis Pipeline
  Ganjam District, Odisha — Bay of Bengal
  5-Year Study: 2019–2024
=============================================================================

  INPUTS  (swap these paths when your real data is ready):
    - Shoreline shapefiles / GeoJSON (one per year)
    - DSAS transect output CSV
    - Spectral index GeoTIFFs (NDWI, MNDWI, NDVI, BSI) per year
    - Rainfall CSV (IMD) and wave height CSV (INCOIS)
    - Validation points (GPS or Google Earth reference)

  OUTPUTS:
    - DataFrames and summary tables (CSV)
    - Confusion matrix + accuracy metrics
    - Time-series plots
    - Erosion hotspot classification map
    - Correlation analysis plots
    - All figures saved to ./outputs/
=============================================================================
"""

# ── 0. IMPORTS ────────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import seaborn as sns
from sklearn.metrics import confusion_matrix, cohen_kappa_score
from scipy import stats
from scipy.stats import pearsonr
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("outputs", exist_ok=True)

# Plot style
plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.family": "sans-serif",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

YEARS = [2019, 2020, 2021, 2022, 2023, 2024]
STUDY_AREA = "Brahmapur Coastline, Ganjam, Odisha"

print("=" * 65)
print(f"  Coastal Erosion Pipeline — {STUDY_AREA}")
print("=" * 65)


# =============================================================================
# MODULE 1 — SHORELINE CHANGE STATISTICS (DSAS output)
# =============================================================================
print("\n[1/5] Shoreline Change Statistics (DSAS)...")

# ── 1a. Load or simulate DSAS transect data ───────────────────────────────────
# REAL DATA: df_dsas = pd.read_csv("data/dsas_transects.csv")
# Your DSAS CSV will have columns:
#   TransectID, Longitude, Latitude, EPR, NSM, LRR, R2, SCE

np.random.seed(42)
n_transects = 80  # adjust to your actual transect count

# Gopalpur area (south) shows net erosion; northern sections mixed
erosion_signal = np.concatenate([
    np.random.normal(-1.8, 0.6, 30),   # southern — erosion dominated
    np.random.normal(-0.4, 1.1, 25),   # central — mixed
    np.random.normal( 0.6, 0.8, 25),   # northern — slight accretion
])

df_dsas = pd.DataFrame({
    "TransectID"  : np.arange(1, n_transects + 1),
    "Longitude"   : np.linspace(84.82, 84.98, n_transects),
    "Latitude"    : np.linspace(19.22, 19.46, n_transects),
    "EPR_m_yr"    : erosion_signal + np.random.normal(0, 0.2, n_transects),
    "NSM_m"       : erosion_signal * 5 + np.random.normal(0, 0.8, n_transects),
    "LRR_m_yr"    : erosion_signal * 0.9 + np.random.normal(0, 0.3, n_transects),
    "R2"          : np.random.uniform(0.72, 0.97, n_transects),
    "SCE_m"       : np.abs(erosion_signal) * 6 + np.random.uniform(1, 5, n_transects),
})

# ── 1b. Classify each transect ────────────────────────────────────────────────
def classify_transect(lrr):
    if lrr <= -1.0:   return "High Erosion"
    elif lrr <= -0.3: return "Moderate Erosion"
    elif lrr <  0.3:  return "Stable"
    elif lrr <  1.0:  return "Moderate Accretion"
    else:             return "High Accretion"

df_dsas["Classification"] = df_dsas["LRR_m_yr"].apply(classify_transect)

# ── 1c. Summary statistics table ──────────────────────────────────────────────
summary_dsas = df_dsas[["EPR_m_yr", "NSM_m", "LRR_m_yr", "SCE_m"]].agg(
    ["mean", "median", "std", "min", "max"]
).round(3)
summary_dsas.index.name = "Statistic"

print("\n  DSAS Summary Statistics:")
print(summary_dsas.to_string())

class_counts = df_dsas["Classification"].value_counts().reset_index()
class_counts.columns = ["Class", "Transect_Count"]
class_counts["Percentage"] = (class_counts["Transect_Count"] / n_transects * 100).round(1)
print("\n  Transect Classification:")
print(class_counts.to_string(index=False))

# ── 1d. Plot — EPR along coast ────────────────────────────────────────────────
CLASS_COLORS = {
    "High Erosion"       : "#D62728",
    "Moderate Erosion"   : "#FF7F0E",
    "Stable"             : "#2CA02C",
    "Moderate Accretion" : "#1F77B4",
    "High Accretion"     : "#0D4F8B",
}
colors = df_dsas["Classification"].map(CLASS_COLORS)

fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [2, 1]})

ax1 = axes[0]
ax1.bar(df_dsas["TransectID"], df_dsas["EPR_m_yr"], color=colors, width=1.0, alpha=0.85)
ax1.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax1.set_ylabel("EPR (m/year)")
ax1.set_title(f"{STUDY_AREA} — End Point Rate per Transect")
legend_patches = [Patch(color=v, label=k) for k, v in CLASS_COLORS.items()]
ax1.legend(handles=legend_patches, fontsize=8, loc="lower right")

ax2 = axes[1]
ax2.plot(df_dsas["TransectID"], df_dsas["LRR_m_yr"], color="#8C564B", linewidth=1.5, label="LRR")
ax2.fill_between(df_dsas["TransectID"], df_dsas["LRR_m_yr"], 0,
                 where=(df_dsas["LRR_m_yr"] < 0), alpha=0.3, color="#D62728", label="Erosion zone")
ax2.fill_between(df_dsas["TransectID"], df_dsas["LRR_m_yr"], 0,
                 where=(df_dsas["LRR_m_yr"] > 0), alpha=0.3, color="#1F77B4", label="Accretion zone")
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2.set_xlabel("Transect ID (S to N)")
ax2.set_ylabel("LRR (m/year)")
ax2.legend(fontsize=8)

plt.tight_layout()
plt.savefig("outputs/1_shoreline_change_stats.png", bbox_inches="tight")
plt.close()
print("  Saved: outputs/1_shoreline_change_stats.png")

df_dsas.to_csv("outputs/dsas_transects_classified.csv", index=False)
print("  Saved: outputs/dsas_transects_classified.csv")


# =============================================================================
# MODULE 2 — SPECTRAL INDEX TIME SERIES (NDWI, MNDWI, NDVI, BSI)
# =============================================================================
print("\n[2/5] Spectral Index Time Series...")

# ── 2a. Load or simulate index data ──────────────────────────────────────────
# REAL DATA: export zonal mean per year from GEE as CSV, then:
#   df_indices = pd.read_csv("data/index_timeseries.csv")

index_data = {
    "Year"  : YEARS,
    "NDWI"  : [ 0.12,  0.09,  0.14,  0.08,  0.11,  0.07],
    "MNDWI" : [ 0.28,  0.24,  0.31,  0.22,  0.26,  0.20],
    "NDVI"  : [ 0.38,  0.35,  0.33,  0.30,  0.27,  0.25],
    "BSI"   : [-0.11, -0.08, -0.06, -0.03, -0.01,  0.02],
}
df_indices = pd.DataFrame(index_data)
df_indices["NDVI_change_pct"] = df_indices["NDVI"].pct_change() * 100
df_indices["BSI_change"]      = df_indices["BSI"].diff()

print("\n  Spectral Index Time Series Table:")
print(df_indices.round(4).to_string(index=False))

# ── 2b. Trend test ────────────────────────────────────────────────────────────
print("\n  Linear Trends (slope per year):")
for col in ["NDWI", "MNDWI", "NDVI", "BSI"]:
    slope, intercept, r, p, se = stats.linregress(df_indices["Year"], df_indices[col])
    sig = "significant" if p < 0.05 else "not significant"
    print(f"    {col:8s}: slope={slope:+.4f}/yr  R2={r**2:.3f}  p={p:.4f}  ({sig})")

# ── 2c. Plot ──────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=False)
index_meta = {
    "NDWI" : ("#1F77B4", "Water index — rising = more water / erosion"),
    "MNDWI": ("#17BECF", "Modified water index — coastal preferred"),
    "NDVI" : ("#2CA02C", "Vegetation — declining = coastal degradation"),
    "BSI"  : ("#8C564B", "Bare soil — rising = sediment exposure"),
}
for ax, (col, (color, desc)) in zip(axes.flatten(), index_meta.items()):
    ax.plot(df_indices["Year"], df_indices[col], marker="o", color=color,
            linewidth=2, markersize=7, label=col)
    slope, intercept, *_ = stats.linregress(df_indices["Year"], df_indices[col])
    trend_y = slope * np.array(YEARS) + intercept
    ax.plot(YEARS, trend_y, "--", color=color, alpha=0.5, linewidth=1.2, label="Trend")
    ax.set_title(col, fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean Index Value")
    ax.legend(fontsize=8)
    ax.set_xticks(YEARS)
    ax.text(0.03, 0.04, desc, transform=ax.transAxes, fontsize=7.5,
            color="gray", va="bottom")

fig.suptitle(f"{STUDY_AREA} — Spectral Index Trends 2019–2024", fontsize=13)
plt.tight_layout()
plt.savefig("outputs/2_spectral_index_timeseries.png", bbox_inches="tight")
plt.close()
print("  Saved: outputs/2_spectral_index_timeseries.png")

df_indices.to_csv("outputs/spectral_index_timeseries.csv", index=False)
print("  Saved: outputs/spectral_index_timeseries.csv")


# =============================================================================
# MODULE 3 — CONFUSION MATRIX & ACCURACY ASSESSMENT
# =============================================================================
print("\n[3/5] Confusion Matrix & Accuracy Assessment...")

# ── 3a. Load or simulate validation points ────────────────────────────────────
# REAL DATA:
#   df_val = pd.read_csv("data/validation_points.csv")
#   Columns: PointID, True_Class, Predicted_Class
#   True_Class      = manually labelled from GPS / Google Earth
#   Predicted_Class = your MNDWI classification output

n_val = 120
true_labels = ["Water"] * 42 + ["Intertidal"] * 35 + ["Land"] * 43
pred_labels = []
np.random.seed(7)
for t in true_labels:
    if t == "Water":
        pred_labels.append(np.random.choice(
            ["Water","Intertidal","Land"], p=[0.91, 0.07, 0.02]))
    elif t == "Intertidal":
        pred_labels.append(np.random.choice(
            ["Water","Intertidal","Land"], p=[0.08, 0.82, 0.10]))
    else:
        pred_labels.append(np.random.choice(
            ["Water","Intertidal","Land"], p=[0.02, 0.06, 0.92]))

df_val = pd.DataFrame({"True_Class": true_labels, "Predicted_Class": pred_labels})

# ── 3b. Confusion matrix ─────────────────────────────────────────────────────
classes = ["Water", "Intertidal", "Land"]
cm = confusion_matrix(df_val["True_Class"], df_val["Predicted_Class"], labels=classes)
cm_df = pd.DataFrame(cm, index=classes, columns=classes)

overall_acc = np.trace(cm) / cm.sum()
kappa       = cohen_kappa_score(df_val["True_Class"], df_val["Predicted_Class"])
prod_acc    = {c: cm[i,i]/cm[i,:].sum() for i,c in enumerate(classes)}
user_acc    = {c: cm[i,i]/cm[:,i].sum() for i,c in enumerate(classes)}

print("\n  Confusion Matrix:")
print(cm_df.to_string())
print(f"\n  Overall Accuracy : {overall_acc*100:.2f}%")
print(f"  Kappa Coefficient: {kappa:.4f}")
acc_table = pd.DataFrame({
    "Class": classes,
    "PA (%)": [round(prod_acc[c]*100,1) for c in classes],
    "UA (%)": [round(user_acc[c]*100,1) for c in classes]
})
print("\n  Producer Accuracy (PA) & User Accuracy (UA):")
print(acc_table.to_string(index=False))

# ── 3c. Plot ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues", linewidths=0.5,
            linecolor="white", ax=ax, cbar_kws={"label": "Count"})
ax.set_xlabel("Predicted Class", fontsize=11)
ax.set_ylabel("True Class (Reference)", fontsize=11)
ax.set_title(
    f"Confusion Matrix  OA: {overall_acc*100:.1f}%   Kappa: {kappa:.3f}\n"
    f"{STUDY_AREA}", fontsize=11)
plt.tight_layout()
plt.savefig("outputs/3_confusion_matrix.png", bbox_inches="tight")
plt.close()
print("  Saved: outputs/3_confusion_matrix.png")

df_val.to_csv("outputs/validation_points.csv", index=False)
acc_table.to_csv("outputs/accuracy_assessment.csv", index=False)
print("  Saved: outputs/validation_points.csv")
print("  Saved: outputs/accuracy_assessment.csv")


# =============================================================================
# MODULE 4 — EROSION HOTSPOT CLASSIFICATION
# =============================================================================
print("\n[4/5] Erosion Hotspot Classification...")

# ── 4a. Build composite risk score per transect ───────────────────────────────
# Weighted combination of: LRR rate (50%) + NDVI decline (30%) + BSI level (20%)

df_risk = df_dsas[["TransectID", "Longitude", "Latitude",
                   "LRR_m_yr", "EPR_m_yr", "NSM_m"]].copy()

np.random.seed(13)
df_risk["NDVI_2019"]    = np.random.uniform(0.30, 0.55, n_transects)
df_risk["NDVI_2024"]    = df_risk["NDVI_2019"] - np.abs(df_risk["LRR_m_yr"]) * 0.05 + np.random.normal(0, 0.02, n_transects)
df_risk["BSI_2024"]     = -df_risk["NDVI_2024"] * 0.6 + np.random.normal(0, 0.03, n_transects)
df_risk["NDVI_decline"] = df_risk["NDVI_2019"] - df_risk["NDVI_2024"]

def norm(s):
    return (s - s.min()) / (s.max() - s.min())

df_risk["score_lrr"]  = norm(-df_risk["LRR_m_yr"])
df_risk["score_ndvi"] = norm(df_risk["NDVI_decline"])
df_risk["score_bsi"]  = norm(df_risk["BSI_2024"])
df_risk["Risk_Score"] = (
    0.50 * df_risk["score_lrr"] +
    0.30 * df_risk["score_ndvi"] +
    0.20 * df_risk["score_bsi"]
)

def risk_class(score):
    if score >= 0.75: return "Critical"
    elif score >= 0.55: return "High"
    elif score >= 0.35: return "Moderate"
    elif score >= 0.15: return "Low"
    else: return "Negligible"

df_risk["Risk_Level"] = df_risk["Risk_Score"].apply(risk_class)

risk_summary = df_risk["Risk_Level"].value_counts().reset_index()
risk_summary.columns = ["Risk Level", "Transects"]
risk_summary["% of Coast"] = (risk_summary["Transects"] / n_transects * 100).round(1)
print("\n  Erosion Hotspot Summary:")
print(risk_summary.to_string(index=False))

# ── 4b. Plot ──────────────────────────────────────────────────────────────────
RISK_COLORS = {
    "Critical"  : "#A50026",
    "High"      : "#F46D43",
    "Moderate"  : "#FEE08B",
    "Low"       : "#74ADD1",
    "Negligible": "#313695",
}

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax1 = axes[0]
sc = ax1.scatter(df_risk["Longitude"], df_risk["Latitude"],
                 c=df_risk["Risk_Score"], cmap="RdYlBu_r", s=60, alpha=0.85, edgecolors="none")
plt.colorbar(sc, ax=ax1, label="Composite Risk Score")
ax1.set_xlabel("Longitude")
ax1.set_ylabel("Latitude")
ax1.set_title("Erosion Risk Score Map\n(spatial distribution)")

ax2 = axes[1]
ax2.barh(risk_summary["Risk Level"], risk_summary["% of Coast"],
         color=[RISK_COLORS.get(r, "gray") for r in risk_summary["Risk Level"]])
ax2.set_xlabel("% of Coastline")
ax2.set_title("Erosion Hotspot Classification\n(proportion of coast)")
for i, (val, label) in enumerate(zip(risk_summary["% of Coast"], risk_summary["Transects"])):
    ax2.text(val + 0.5, i, f"{label} transects", va="center", fontsize=9)

fig.suptitle(f"{STUDY_AREA} — Erosion Hotspot Analysis", fontsize=13)
plt.tight_layout()
plt.savefig("outputs/4_erosion_hotspot_classification.png", bbox_inches="tight")
plt.close()
print("  Saved: outputs/4_erosion_hotspot_classification.png")

df_risk.to_csv("outputs/erosion_hotspot_table.csv", index=False)
print("  Saved: outputs/erosion_hotspot_table.csv")


# =============================================================================
# MODULE 5 — CORRELATION WITH RAINFALL & WAVE DATA
# =============================================================================
print("\n[5/5] Correlation with Rainfall & Wave Data...")

# ── 5a. Load or simulate auxiliary data ──────────────────────────────────────
# REAL DATA:
#   df_climate = pd.read_csv("data/climate_auxiliary.csv")
#   Sources: IMD for rainfall, INCOIS for wave height

df_climate = pd.DataFrame({
    "Year"              : YEARS,
    "Rainfall_mm"       : [1320, 1085, 1490, 980, 1210, 1055],
    "Sig_Wave_Height_m" : [1.82, 1.65, 2.10, 1.58, 1.74, 1.61],
    "Storm_Days"        : [8, 5, 12, 4, 7, 5],
    "Cyclone_Intensity" : [2, 1, 3, 0, 2, 1],
    "Mean_EPR_m_yr"     : [-1.1, -0.7, -1.6, -0.5, -0.9, -0.7],
    "Mean_NDVI"         : df_indices["NDVI"].values,
    "Mean_BSI"          : df_indices["BSI"].values,
})

print("\n  Climate & Shoreline Data Table:")
print(df_climate.round(3).to_string(index=False))

# ── 5b. Pearson correlations ─────────────────────────────────────────────────
corr_vars = ["Rainfall_mm", "Sig_Wave_Height_m", "Storm_Days", "Cyclone_Intensity"]
print("\n  Pearson Correlations with Mean EPR (m/year):")
corr_results = []
for var in corr_vars:
    r, p = pearsonr(df_climate[var], df_climate["Mean_EPR_m_yr"])
    sig = "significant" if p < 0.05 else "n.s."
    corr_results.append({"Variable": var, "r": round(r,3), "p-value": round(p,4), "Significance": sig})
    print(f"    {var:25s}: r={r:+.3f}  p={p:.4f}  {sig}")

df_corr = pd.DataFrame(corr_results)

# ── 5c. Full correlation matrix ───────────────────────────────────────────────
corr_matrix = df_climate[["Mean_EPR_m_yr","Rainfall_mm","Sig_Wave_Height_m",
                           "Storm_Days","Mean_NDVI","Mean_BSI"]].corr()

# ── 5d. Plots ─────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 9))
scatter_pairs = [
    ("Rainfall_mm",       "Mean_EPR_m_yr", "Annual Rainfall (mm)",    "Mean EPR (m/yr)", "#1F77B4"),
    ("Sig_Wave_Height_m", "Mean_EPR_m_yr", "Significant Wave Ht (m)", "Mean EPR (m/yr)", "#D62728"),
    ("Storm_Days",        "Mean_EPR_m_yr", "Storm Days per Year",      "Mean EPR (m/yr)", "#FF7F0E"),
    ("Rainfall_mm",       "Mean_NDVI",     "Annual Rainfall (mm)",     "Mean NDVI",       "#2CA02C"),
]
for ax, (xvar, yvar, xlabel, ylabel, color) in zip(axes.flatten(), scatter_pairs):
    ax.scatter(df_climate[xvar], df_climate[yvar], color=color, s=80, zorder=3)
    for _, row in df_climate.iterrows():
        ax.annotate(str(int(row["Year"])), (row[xvar], row[yvar]),
                    textcoords="offset points", xytext=(5, 4), fontsize=8)
    slope, intercept, r, p, _ = stats.linregress(df_climate[xvar], df_climate[yvar])
    x_range = np.linspace(df_climate[xvar].min(), df_climate[xvar].max(), 50)
    ax.plot(x_range, slope * x_range + intercept, "--", color=color, alpha=0.6, linewidth=1.5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(f"r = {r:+.3f}  (p = {p:.3f})")

fig.suptitle(f"{STUDY_AREA}\nCorrelation: Erosion vs Climate Drivers", fontsize=13)
plt.tight_layout()
plt.savefig("outputs/5a_correlation_scatter.png", bbox_inches="tight")
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            linewidths=0.5, ax=ax,
            xticklabels=corr_matrix.columns, yticklabels=corr_matrix.columns)
ax.set_title(f"{STUDY_AREA}\nCorrelation Matrix — All Variables")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("outputs/5b_correlation_matrix.png", bbox_inches="tight")
plt.close()

print("  Saved: outputs/5a_correlation_scatter.png")
print("  Saved: outputs/5b_correlation_matrix.png")
df_climate.to_csv("outputs/climate_erosion_correlation.csv", index=False)
df_corr.to_csv("outputs/correlation_results.csv", index=False)
print("  Saved: outputs/climate_erosion_correlation.csv")
print("  Saved: outputs/correlation_results.csv")


# =============================================================================
# FINAL SUMMARY TABLE — Paper-ready
# =============================================================================
print("\n" + "=" * 65)
print("  SUMMARY TABLE — Key Results for Research Paper")
print("=" * 65)

summary_paper = pd.DataFrame({
    "Metric": [
        "Total transects analysed",
        "Mean LRR (m/yr)",
        "Max erosion rate (m/yr)",
        "Max accretion rate (m/yr)",
        "% coast under erosion",
        "% coast critical/high risk",
        "NDVI change 2019-2024",
        "BSI change 2019-2024",
        "Overall classification accuracy",
        "Kappa coefficient",
        "Strongest erosion driver (r)",
    ],
    "Value": [
        str(n_transects),
        f"{df_dsas['LRR_m_yr'].mean():.2f}",
        f"{df_dsas['EPR_m_yr'].min():.2f}",
        f"{df_dsas['EPR_m_yr'].max():.2f}",
        f"{(df_dsas['LRR_m_yr'] < 0).mean()*100:.1f}%",
        f"{df_risk['Risk_Level'].isin(['Critical','High']).mean()*100:.1f}%",
        f"{df_indices['NDVI'].iloc[-1] - df_indices['NDVI'].iloc[0]:.3f}",
        f"{df_indices['BSI'].iloc[-1] - df_indices['BSI'].iloc[0]:.3f}",
        f"{overall_acc*100:.1f}%",
        f"{kappa:.3f}",
        df_corr.loc[df_corr['r'].abs().idxmax(), 'Variable'],
    ],
    "Notes": [
        "N-S transects at 250m spacing",
        "Negative = net erosion",
        "Southern section, Gopalpur",
        "Northern section",
        "LRR < 0 m/yr",
        "Composite risk score >= 0.55",
        "Declining vegetation cover",
        "Increasing bare sediment",
        "vs GPS / Google Earth ref.",
        "> 0.80 = strong agreement",
        "Pearson r, absolute value",
    ]
})

print(summary_paper.to_string(index=False))
summary_paper.to_csv("outputs/summary_results_table.csv", index=False)
print("\n  Saved: outputs/summary_results_table.csv")

print("\n" + "=" * 65)
print("  All outputs saved to ./outputs/")
print("  Replace sample data with your real file paths.")
print("=" * 65)
