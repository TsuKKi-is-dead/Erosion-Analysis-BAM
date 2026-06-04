import pandas as pd

df = pd.read_csv("/Users/tsukki/Downloads/files/GEE_Brahmapur/validation_points_clean_final.csv", 
                 skiprows=1, header=0)
df.columns = ['system:index','Predicted','Predicted_Class','longitude','latitude','True_Class']
df = df[df['system:index'] != 'system:index'].reset_index(drop=True)
df['longitude'] = df['longitude'].astype(float)
df['latitude'] = df['latitude'].astype(float)

# Save clean version for GEE upload
df[['system:index','longitude','latitude','True_Class']].to_csv(
    "/Users/tsukki/Downloads/files/GEE_Brahmapur/validation_for_gee.csv", 
    index=False)
print("Saved: validation_for_gee.csv")
print(df.head(3))