import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.table import table
import os

# ====================== PATHS ======================
BASE_DIR = "/Users/tsukki/Downloads/files"
DSAS_DIR = os.path.join(BASE_DIR, "GEE_Brahmapur")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load your data
yearly_epr_path = os.path.join(DSAS_DIR, "yearly_epr.csv")
summary_path = os.path.join(OUTPUT_DIR, "dsas_summary_statistics.csv")

df_yearly = pd.read_csv(yearly_epr_path)
df_summary = pd.read_csv(summary_path)

print("Columns in yearly_epr.csv:", df_yearly.columns.tolist())
print("\nFirst few rows:\n", df_yearly.head())

# ====================== CREATE VISUAL TABLE ======================
fig, ax = plt.subplots(figsize=(14, 8))
ax.axis('off')

# Select key columns for display (adjust based on your actual columns)
key_cols = ['Year', 'EPR_mean', 'EPR_median', 'Net_Change_m', 'Erosion_Area_sqkm', 'Transects_Eroding']
available_cols = [col for col in key_cols if col in df_yearly.columns]

if not available_cols:
    available_cols = df_yearly.columns[:6]  # fallback

display_df = df_yearly[available_cols].round(3)

# Create the table
tbl = table(ax, 
            cellText=display_df.values,
            colLabels=display_df.columns,
            loc='center',
            cellLoc='center',
            colWidths=[0.15] * len(display_df.columns))

tbl.auto_set_font_size(False)
tbl.set_fontsize(9.5)
tbl.scale(1.2, 1.8)   # width, height scaling

# Style
for key, cell in tbl._cells.items():
    if key[0] == 0:  # header
        cell.set_text_props(weight='bold', color='white')
        cell.set_facecolor('#2E86C1')
    elif key[0] % 2 == 0:
        cell.set_facecolor('#EBF5FB')
    else:
        cell.set_facecolor('#FFFFFF')

ax.set_title('Brahmapur Coastline - Multi-Year Net Erosion Statistics\n(Gopalpur Region, 2013–2024)', 
             fontsize=16, pad=20, fontweight='bold')

plt.savefig(os.path.join(OUTPUT_DIR, "net_erosion_visual_table.png"), 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig(os.path.join(OUTPUT_DIR, "net_erosion_visual_table.pdf"), 
            bbox_inches='tight')

print(f"\n✅ Visual table saved to:")
print(f"   {os.path.join(OUTPUT_DIR, 'net_erosion_visual_table.png')}")
print(f"   {os.path.join(OUTPUT_DIR, 'net_erosion_visual_table.pdf')}")